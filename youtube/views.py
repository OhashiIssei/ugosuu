from .models import Video,Playlist,PlaylistItem,ChannelSection,MY_CHANNEL_ID
from .models import VideoType,VideoGenre
from .models import ChannelId,ChannelSectionId,PlaylistId,VideoId

from .models import University,Source

from ugosite.models import Term


import random

class RandomPresentationSystem:
    def select(self,videos):
        random_num = random.randrange(len(videos))
        selected_video = videos[random_num]
        return selected_video

    def test():
        videos = Video.objects.filter(data__snippet__title__icontains = "2次関数")
        video_list_for_test = list(videos)
        for i in range(10):
            test_selected_video = RandomPresentationSystem().select(video_list_for_test)
            print("test_selected: %s" % test_selected_video)
            video_list_for_test.remove(test_selected_video)
            if video_list_for_test:continue
            break
        selected_video = RandomPresentationSystem().select(videos)
        print("✨selected: %s" % selected_video)
        return selected_video

import django.views.generic as generic

class Update:
    def make_new_datas():
        videos = Video.objects.all()
        for i,video in enumerate(videos):
            print("\n\n%s:%s" % (i,video))
            video.rewrite_title()
            video.save()
        updated_videos = Video.objects.filter(new_data__isnull = False)
        print("\n書き換え予定の問題の数：%s" % updated_videos.count())

    def videos():
        videos = Video.objects.filter(new_data__isnull = False)
        for i,video in enumerate(videos):
            print("\n\n%s:「%s」を更新中。。。" % (i,video))
            video.update()
            print(" 。。。更新成功")
        print("\n更新された問題の数：%s" % videos.count())

    def playlists():
        playlists = Playlist.objects.all()
        # playlists = Playlist.objects.filter(data__snippet__description__icontains = "数列")#.exclude(data__snippet__title__icontains = "強化")
        for i,playlist in enumerate(playlists):
            print("\n\n%s:「%s」を更新中。。。" % (i,playlist))
            playlist.rewrite_title()
            print(playlist)
            playlist.update()
            # playlist.save()
        print("\n更新されたプレイリストの数：%s" % playlists.count())

class PlaylistDetailView(generic.DetailView):
    model = Playlist

class ChannelSectionDetailView(generic.DetailView):
    model = ChannelSection

class VideoTypeDetailView(generic.DetailView):
    model = VideoType

class VideoGenreDetailView(generic.DetailView):
    model = VideoGenre

class VideoDetailView(generic.DetailView):
    model = Video

class UniversityDetailView(generic.DetailView):
    model = University

class UniversityListView(generic.ListView):
    model = University
    paginate_by = 500


