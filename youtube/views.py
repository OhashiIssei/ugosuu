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


### データ書き換え層への接続

from youtube.download_data import Download_Id,Download_Response,Create_Models,Add_Relation
from .download_data import ChannelSectionResponse,PlaylistResponse,PlaylistItemResponse,VideoResponse




def reflesh_Models():
    # Download_Id().channelSections()
    # Download_Id().playlists()
    # Download_Id().videos()

    # Download_Response().videos()
    # Download_Response().playlists()
    # Download_Response().playlistItems()
    # Download_Response().channelSections()

    VideoGenre.objects.all().delete()
    VideoType.objects.all().delete()

    University.objects.all().delete()
    Source.objects.all().delete()
    Term.objects.all().delete()
    
    Create_Models().videos()
    Create_Models().playlists()
    Create_Models().channelSections()
    Create_Models().playlistItems()
    Create_Models().channelSections()
    Add_Relation().videos()
    Add_Relation().videos_to_terms()


# reflesh_Models()

# for video_genre in VideoGenre.objects.all():
#     print(video_genre.category())
    


def display_status():
    print("ChannelIdの個数: %s" % ChannelId.objects.count())
    print("ChannelSectionIdの個数: %s" % ChannelSectionId.objects.count())
    print("PlaylistIdの個数: %s" % PlaylistId.objects.count())
    print("VideoIdの個数: %s" % VideoId.objects.count())

    print("ChannelSectionResponseの個数: %s" % ChannelSectionResponse.objects.count())
    print("PlaylistResponseの個数: %s" % PlaylistResponse.objects.count())
    print("PlaylistItemResponseの個数: %s" % PlaylistItemResponse.objects.count())
    print("VideoResponseの個数: %s" % VideoResponse.objects.count())

    print("Videoの個数: %s" % Video.objects.count())
    print("Playlistの個数: %s" % Playlist.objects.count())
    print("PlaylistItemの個数: %s" % PlaylistItem.objects.count())
    print("ChannelSectionの個数: %s" % ChannelSection.objects.count())

    print("VideoTypeの個数: %s" % VideoType.objects.count())
    print("VideoGenreの個数: %s" % VideoGenre.objects.count())

    print("Universityの個数: %s" % University.objects.count())
    print("Sourceの個数: %s" % Source.objects.count())

display_status()



