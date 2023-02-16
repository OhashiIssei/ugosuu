from django.db import models

# Create your models here.

from youtube.models import Video,VideoType,VideoGenre,MY_CHANNEL_ID
from util.youtube_api import youtube_with_key

class VideoSearch(models.Model):
    keyword = models.CharField(max_length=100)
    video_types = models.ManyToManyField(VideoType)
    video_genres = models.ManyToManyField(VideoGenre)

    def __str__(self):
        return self.keyword
    
    def display_video_types(self):
        return ",".join([video_type.name for video_type in self.video_types.all()])

    def result_video_list(self):
        set = SearchedVideoSet.objects.create(search = self)
        # set.search_youtube()
        set.add_all_videos()
        set.filter_by_types()
        set.filter_by_genres()
        return [searched_video.video for searched_video in set.searched_videos.all()]
    
    def download_videoId_list(self):
        search_response = youtube_with_key.search().list(
            channelId = MY_CHANNEL_ID,
            type = "video",
            q = self.keyword,
            part = "id",
            maxResults = 50 ##1〜50を指定する。
        ).execute()
        return [item["id"]["videoId"] for item in search_response["items"]]
    
    def initialize(self):
        VideoSearch.objects.all().delete()
        VideoSearch.objects.create(keyword = "はやくち解説")

    


class SearchedVideo(models.Model):
    video = models.ForeignKey(Video,on_delete=models.CASCADE)
    num = models.PositiveSmallIntegerField(blank=True)

    def __str__(self):
        return f'{self.num}:{self.video}'

    class Meta:
        ordering = ['num']

class SearchedVideoSet(models.Model):
    search = models.ForeignKey(VideoSearch,on_delete=models.CASCADE)
    searched_videos = models.ManyToManyField(SearchedVideo)

    ### Model変数を書き換えるメソッド
    def search_youtube(self):
        videoId_list = self.search.download_videoId_list()
        self.add_by_videoId_list(videoId_list)


    def add_all_videos(self):
        for num,video in enumerate(Video.objects.all()):
            searched_video = SearchedVideo.objects.create(
                num = num,
                video = video
            )
            self.searched_videos.add(searched_video)

    def add_by_videoId_list(self,videoId_list:list):
        for num,videoId in enumerate(videoId_list):
            searched_video = SearchedVideo.objects.create(
                num = num,
                video = Video.objects.get(videoId = videoId)
            )
            self.searched_videos.add(searched_video)

    def filter_by_videos_list(self,videos_list:list[SearchedVideo]):
        remove_videos = self.searched_videos.exclude(video__in = videos_list)
        self.searched_videos.remove(*remove_videos.all())

    def filter_by_types(self):
        videos_list = Video.objects.filter(video_type__in = self.search.video_types.all())
        self.filter_by_videos_list(videos_list)

    def filter_by_genres(self):
        videos_list = Video.objects.filter(video_genre__in = self.search.video_genres.all())
        self.filter_by_videos_list(videos_list)

    
        
