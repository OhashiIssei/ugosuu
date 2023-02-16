from django import forms

from django.forms import ModelForm

from youtube.models import VIDEO_TYPE_CHOICES

from .models import VideoSearch

video_types = [choice[0] for choice in VIDEO_TYPE_CHOICES]

class VideoSearchForm(ModelForm):
    class Meta:
        model = VideoSearch
        fields = ['keyword', 'video_types','video_genres']
