from rest_framework import serializers
from urllib.parse import urlparse

class SiteMapExtractorSerializer(serializers.Serializer):
    url = serializers.URLField()

    def validate_url(self, value):
        parsed = urlparse(value)

        if parsed.scheme not in ("http", "https"):
            raise serializers.ValidationError("URL must start with http:// or https://")

        path = parsed.path.rstrip("/")

        allowed_endings = ("", "/sitemap.xml", "/robots.txt")
        # also allow any .xml path like /sitemap_index.xml
        if not (path == "" or path.endswith(".xml") or path.endswith("robots.txt") or path.endswith("xmlsitemap.php")) :
            raise serializers.ValidationError(
                "Provide a domain, a .xml sitemap URL, or a robots.txt URL."
            )

        return value
