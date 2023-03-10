from django.db import models

from util.youtube_api import youtube_with_key

class ChannelId(models.Model):
    raw_text = models.CharField(max_length=50,unique=True)

    def __str__(self):
        return self.raw_text
    
    def download_channelSectionId_and_res(self):#,pagetoken)
        print(f"ChannelId「{self}」からChannelSectionIdをすべて取得します")
        res = youtube_with_key.channelSections().list(
            channelId = self.raw_text,
            part='snippet,contentDetails',
        ).execute()
        from youtube.create_datas import ChannelSectionResponses
        ChannelSectionResponses(res["items"]).save_each_id_and_res()

    def download_playlistId_and_res(self):
        print(f"ChannelId「{self}」からPlaylistIdをすべて取得します")
        pageToken = ""
        while True:
            res = youtube_with_key.playlists().list(
                channelId = self.raw_text,
                part='id,snippet',
                maxResults = 100,
                pageToken = pageToken
            ).execute() 
            from youtube.create_datas import PlaylistResponses
            PlaylistResponses(res["items"]).save_each_id_and_res()
            try:
                pageToken = res["nextPageToken"]
                continue
            except:
                break

    def download_playlistId_of_uploads(self):
        print("CannelId「%s」のuploadsのplaylistIdを取得します" % self)
        res = youtube_with_key.channels().list(
            id = self.raw_text,
            part="contentDetails"
        ).execute()
        channel_data = res["items"][0]
        playlistId,created = PlaylistId.objects.get_or_create(raw_text = channel_data["contentDetails"]["relatedPlaylists"]["uploads"])
        playlistId.download_playlistResponse()
        return playlistId

class ChannelSectionId(models.Model):
    raw_text = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.raw_text
    
    def download_playlistId_and_res(self):
        print(f"ChannelSectionId「{self}」からPlaylistIdをすべて取得します")
        res = youtube_with_key.channelSections().list(
            id = self.raw_text,
            part='snippet,contentDetails',
        ).execute() 
        from youtube.create_datas import PlaylistId
        for raw_text in res["items"][0]["contentDetails"]["playlists"]:
            playlistId,created = PlaylistId.objects.get_or_create(raw_text = raw_text)
            if created:
                playlistId.download_playlistResponse()

class PlaylistId(models.Model):
    raw_text = models.CharField(max_length=50,unique=True)

    def __str__(self):
        return self.raw_text

    def download_playlistItemId_and_res_and_videoId(self):
        print(f"PlaylistId「{self}」内のPlaylistItemIdをすべて取得します")
        pageToken = ""
        while True:
            res = youtube_with_key.playlistItems().list(
                playlistId = self.raw_text,
                part='id,snippet',
                maxResults = 100,
                pageToken = pageToken
            ).execute()
            from youtube.create_datas import PlaylistItemResponse
            for data in res["items"]:
                PlaylistItemId.objects.get_or_create(raw_text = data["id"])
                PlaylistItemResponse.objects.get_or_create(json_data = data)
                VideoId.objects.get_or_create(raw_text = data["snippet"]['resourceId']["videoId"])
            try:
                pageToken = res["nextPageToken"]
                continue
            except:
                break

    def download_playlistResponse(self):
        print("PlaylistId「%s」からplaylistResponseを取得します" % self)
        pageToken = ""
        res = youtube_with_key.playlists().list(
            id = self.raw_text,
            part='id,snippet',
            maxResults = 100,
            pageToken = pageToken
        ).execute()
        from youtube.create_datas import PlaylistResponse
        PlaylistResponse.objects.get_or_create(json_data = res["items"][0])

class PlaylistItemId(models.Model):
    raw_text = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.raw_text
    
    def download_videoIds_and_res(self):
        print(f"PlaylistItemId「{self}」のVideoIdをすべて取得します")
        pageToken = ""
        while True:
            res = youtube_with_key.playlistItems().list(
                id = self.raw_text,
                part='snippet',
                maxResults = 100,
                pageToken = pageToken
            ).execute()
            videoId,created = VideoId.objects.get_or_create(raw_text = res["items"][0]["snippet"]['resourceId']["videoId"])
            videoId.download_videoResponse()
            try:
                pageToken = res["nextPageToken"]
                continue
            except:
                break

class VideoId(models.Model):
    raw_text = models.CharField(max_length=50,unique=True)
    
    def __str__(self):
        return self.raw_text

    def download_videoResponse(self):
        print("VideoId「%s」からVideoResponseを取得します" % self)
        res = youtube_with_key.videos().list(
            id = self.raw_text,
            part='snippet',
        ).execute()
        from youtube.create_datas import VideoResponse
        VideoResponse.objects.get_or_create(json_data = res["items"][0])
        # print("Video「%s」のデータを更新しました" % self)

        
        