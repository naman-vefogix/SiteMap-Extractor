from django.urls import path
from .views import *


urlpatterns = [
    path('', HomeView, name='home_view'),
    path('sitemap-extractor/', Sitemap_ExtractorView.as_view(), name='sitemap'),
    path('sitemap-task/<str:task_id>/', SitemapTaskStatusView.as_view(), name = 'SitemapTaskStatusView'),
]

