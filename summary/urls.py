from django.urls import path
from .views import YouTubeDataAPIView

urlpatterns = [
    # Define your URL patterns here
    path('video-info/', YouTubeDataAPIView.as_view(), name='youtube-data'),
]
