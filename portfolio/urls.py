from django.urls import path
from .views import ContactView, ResumeDownloadView

urlpatterns = [
    path('contact/', ContactView.as_view(), name='contact'),
    path('resume/', ResumeDownloadView.as_view(), name='resume-download'),
]