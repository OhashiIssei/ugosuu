from youtube.models import ChannelId,MY_CHANNEL_ID

from .models import VideoSearch
from .forms import VideoSearchForm

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.views import View


class VideoSearchView(View):
    form_class = VideoSearchForm
    initial = {'keyword': 'はやくち解説'}
    template_name = 'youtube/video_saerch.html'

    def get(self, request, *args, **kwargs):
        searchs = VideoSearch.objects.filter(id = self.kwargs["pk"])
        if not searchs:
            return render(request, self.template_name, context={'form': self.form_class()})
        search = searchs[0]
        video_list = search.result_video_list()
        context = {
            'keyword': search.keyword,
            "videos_list" : video_list,
            "videos_num" : len(video_list),
            'form': self.form_class(
                initial={
                    'keyword': search.keyword, 
                    'video_types': search.video_types.all(),
                    'video_genres': search.video_genres.all()
                    }
                )
        }
        return render(request, self.template_name, context=context)
    


    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        
        keyword = str(form.cleaned_data['keyword'])
        video_type_list = list(form.cleaned_data['video_types'])
        video_genre_list = list(form.cleaned_data['video_genres'])
        
        search = VideoSearch.objects.create(keyword= keyword)
        search.video_types.add(*video_type_list)
        search.video_genres.add(*video_genre_list)

        return HttpResponseRedirect(reverse('video_search', args=[search.id]))