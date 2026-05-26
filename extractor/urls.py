from django.urls import path
from . import views


urlpatterns = [
    path('', views.HomeView, name='home_view'),
    path('xml/', views.SitemapExtractorAPIView.as_view(), name='sitemap')
]
