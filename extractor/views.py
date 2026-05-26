from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from .serializers import SiteMapExtractorSerializer
from .services import parse_sitemap

# Create your views here.

def HomeView(request):
    return render(request,'home.html')

class SitemapExtractorAPIView(APIView):
    def post(self,request):
        serializer = SiteMapExtractorSerializer(data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        url = serializer.validated_data['url']
        try:
            sitemap_url = f"{url.rstrip('/')}/sitemap.xml"
            urls = parse_sitemap(
                sitemap_url
            )
            return Response({
                "count": len(urls),
                "urls": urls
            })

        except Exception as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    