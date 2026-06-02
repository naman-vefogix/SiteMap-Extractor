from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from celery.result import AsyncResult

from .tasks import sitemap_extractor_task
from .serializers import SiteMapExtractorSerializer
from .services import get_user_ip, normalize_domain
from .models import SitemapExtraction

from django.utils import timezone
from datetime import timedelta

from math import ceil

# Create your views here.

def HomeView(request):
    return render(request,'home.html')

class Sitemap_ExtractorView(APIView):
    def post(self,request):
        serializer = SiteMapExtractorSerializer(data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        url = serializer.validated_data['url']
        max_urls = 100000 if request.user.is_authenticated else 1000
        user_id = request.user.id if request.user.is_authenticated else None
        user_ip = get_user_ip(request=request)

        record = SitemapExtraction.objects.create(user_id=user_id,ip_address=user_ip,domain=normalize_domain(url),urls=[],total_urls=0,expires_at=timezone.now() + timedelta(days=1),status="pending")
        
        task = sitemap_extractor_task.delay(extraction_id=record.id, url=url,max_urls= max_urls,user_id=user_id)
        return Response(
            {
                "task_id" : task.id,
                "status" : "processing" 
            },
            status=status.HTTP_202_ACCEPTED
        )



class SitemapTaskStatusView(APIView):
    def get(self, request, task_id):
        task = AsyncResult(task_id)
        if task.state == "PENDING":
            return Response({"status": "PENDING"})

        elif task.state == "STARTED":
            return Response({"status": "STARTED"})

        elif task.state == "SUCCESS":
            result = task.result
            page = max(int(request.GET.get("page", 1)), 1)
            page_size = min(
                int(request.GET.get("page_size", 100)),
                1000
            )

            urls = result["urls"]
            start = (page - 1) * page_size
            end = start + page_size
            return Response({
                "status": "SUCCESS",
                "count": result["count"],
                "page": page,
                "page_size": page_size,
                "total_pages": ceil(result["count"] / page_size),
                "results": urls[start:end]
            })
        elif task.state == "FAILURE":
            return Response({
                "status": "FAILURE",
                "error": str(task.result)
            })
        return Response({"status": task.state})
