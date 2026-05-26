from rest_framework import serializers

class SiteMapExtractorSerializer(serializers.Serializer):
    url = serializers.URLField()


