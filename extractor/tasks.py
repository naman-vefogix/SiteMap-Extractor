from django.core.cache import cache
from .services import parse_sitemap, resolve_sitemap_urls, normalize_domain, get_user_ip
from celery import shared_task 

from django.utils import timezone
from datetime import timedelta
from .models import SitemapExtraction


@shared_task(bind=True, name='tools.backlinkGap.sitemap_extractor', track_started=True, result_extended=True)
def sitemap_extractor_task(self, extraction_id, url, max_urls, user_id):

    record = SitemapExtraction.objects.get(id=extraction_id)

    try:
        domain = normalize_domain(url)
        cache_key = f"sitemap:{domain}"

        if not user_id:
            cached_data = cache.get(cache_key)
            if cached_data:
                record.urls = cached_data["urls"]
                record.total_urls = cached_data["count"]
                record.status = "completed"
                record.save(
                    update_fields=[
                        "urls",
                        "total_urls",
                        "status",
                    ]
                )
                return cached_data

        if user_id:
            existing = SitemapExtraction.objects.filter(
                user_id=user_id,
                domain=domain,
                status="completed",
                expires_at__gt=timezone.now()
            ).exclude(id=extraction_id).order_by("-created_at").first()
            if existing:
                record.urls = existing.urls
                record.total_urls = existing.total_urls
                record.status = "completed"
                record.save(
                    update_fields=["urls","total_urls","status",]
                )
                return {"count": existing.total_urls,"urls": existing.urls}

        sitemap_urls = resolve_sitemap_urls(url)

        urls = []
        for sitemap_url in sitemap_urls:
            if max_urls is not None and len(urls) >= max_urls:
                break
            remaining = (max_urls - len(urls)) if max_urls is not None else None
            urls.extend(parse_sitemap(url=sitemap_url, max_urls=remaining))

        result = {"count": len(urls), "urls": urls}
        
        record.urls = urls
        record.total_urls = len(urls)
        record.status = "completed"
        record.save(update_fields=["urls","total_urls","status",])

        if not user_id:
            cache.set(cache_key, result, timeout=3600)

        return result
    
    except Exception:
        record.status = "failed"
        record.save(update_fields=["status"])
        raise