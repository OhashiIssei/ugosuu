from django.db import models

from ugosite.models import Category,Term

import sys,re


from django_mysql.models import ListCharField
from youtube.id import VideoId,PlaylistId,ChannelSectionId,ChannelId


class University(models.Model):
    name = models.CharField(default = None,max_length=200)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('university-detail', args=[str(self.id)])
    
    def videos_num(self):
        result = 0
        for source in self.source_set.all():
            result += source.video_set.count()
        return result
    
    class Meta:
        ordering = ['-id']

class Source(models.Model):
    university = models.ForeignKey(University,default = None,null=True,on_delete=models.SET_NULL)
    division = models.CharField(default = None,null=True,max_length=200)
    year = models.SmallIntegerField(default = None,null=True)
    question_num = models.SmallIntegerField(default = None,null=True)

    def name(self):
        result = "%s" % self.university
        if self.division:
            result += " %s" % self.division
        if self.year:
            result += " %s年" % self.year
        if self.question_num:
            result += " 第%s問" % self.question_num
        return result
    
    def get_absolute_url(self):
        return self.university.get_absolute_url()
    
    def __str__(self):
        return self.name()
    

class Video(models.Model):
    videoId = models.OneToOneField(VideoId,unique=True,default = None,on_delete=models.CASCADE)
    title = models.CharField(default = None,max_length=200)
    source = models.ForeignKey(Source,default = None,null=True,on_delete=models.SET_NULL)

    terms = models.ManyToManyField(Term)

    problem = models.TextField(default = None, null=True, max_length = 10000)
    point = models.TextField(default = None ,null=True, max_length = 10000)

    video_type = models.ForeignKey("VideoType",default = None,null=True,on_delete=models.SET_NULL)
    video_genre = models.ForeignKey("VideoGenre",default = None,null=True,on_delete=models.SET_NULL)

    table_list = ListCharField(
        null = True,
        base_field = models.CharField(max_length = 100),
        size = 20,
        max_length = (100 * 21)
    )

    thumbnail_url = models.URLField(default = "", null=True ,max_length=50)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('video-detail', args=[str(self.id)])
    
    def youtube_url(self):
        return "https://youtu.be/%s" % self.videoId
    
    def youtube_studio_url(self):
        return "https://studio.youtube.com/video/%s/edit" % self.videoId

    def is_next_to(self,video:"Video"):
        for playlistItem_self in self.playlistItem_set.all():
            for playlistItem_video in video.playlistItem_set.all():
                if playlistItem_self.is_next_to(playlistItem_video):return True
                if playlistItem_self == playlistItem_video:return True
        return False
    
    def playlistItems(self):
        return self.playlistitem_set.all()
    
    def playlists(self):
        return [playlistItem.playlist for playlistItem in self.playlistItems()]

    def main_playlist(self):
        playlists = self.playlists()
        if len(playlists)==0: return
        if len(playlists)==1:
            return playlists[0]
        for playlist in playlists:
            for type in VIDEO_TYPE_CHOICES:
                if type[1] in playlist.title:
                    return playlist
        return playlists[0]
    
    def related_videos(self):
        text = self.extract_item("関連問題")
        if not text:
            text = self.extract_item("関連")
        if not text: return []
        lines = text.split("\n")
        videoId_list = [
            re.findall("(.{11})$",line)[0]
            for line in lines
            if re.match("http",line)
        ]
        return [
            VideoId(videoId).video()
            for videoId in videoId_list
            if not self.is_next_to(VideoId(videoId).video())
        ]

    

class Playlist(models.Model):
    playlistId = models.OneToOneField(PlaylistId,unique=True,default = None,on_delete=models.CASCADE)
    title = models.CharField(default = None,max_length=200)
    description = models.TextField(default = None, max_length=1000)
    video_type = models.ForeignKey("VideoType",default = None,null=True,on_delete=models.SET_NULL)
    video_genre = models.ForeignKey("VideoGenre",default = None,null=True,on_delete=models.SET_NULL)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('playlist-detail', args=[str(self.id)])



class PlaylistItem(models.Model):
    video = models.ForeignKey(Video,default = None,on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist,default = None,on_delete=models.CASCADE)
    position = models.SmallIntegerField(default = 0)

    def __str__(self):
        return "%s-%s-%s" % (self.playlist,self.position,self.playlist)
    
    def next(self):
        item_list = self.playlist.playlistitem_set.all()
        next_num = self.position+1
        if next_num<len(item_list):
            return item_list[next_num]
        return None
    
    def prev(self):
        parent_playlist =  self.playlist
        item_list = parent_playlist.playlistitem_set.all()
        prev_num = self.position-1
        if prev_num>=0:
            return item_list[prev_num]
        return None
    
    def is_next_to(self,playlistItem:"PlaylistItem"):
        if self.next()==playlistItem:return True
        if self.prev()==playlistItem:return True
        return False


class ChannelSection(models.Model):
    channelSectionId = models.OneToOneField(ChannelSectionId,unique=True,default = None,on_delete=models.CASCADE)
    title = models.CharField(default = None,max_length=200)
    playlists = models.ManyToManyField(Playlist)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('channelSection-detail', args=[str(self.id)])
    
    
import os
from django.urls import reverse

VIDEO_TYPE_CHOICES = [
    ('計算', '計算問題'), 
    ('基本', '基本事項'), 
    ('典型', '典型問題'), 
    ('応用', '応用問題'), 
    ('強化', '強化問題'),
    ('他', 'その他')
]

MY_CHANNEL_ID = "UCtEVdDYltR4eWf-QXvjmCJQ"

VIDEO_GENRE_TO_CAETEGORY = {
    "数I数と式":"数と式",
    "集合と命題":"集合と命題",
    "２次関数":"２次関数",
    "2次関数":"２次関数",
    "三角比":"図形と計量",

    "場合の数":"場合の数と確率",

    "確率":"場合の数と確率",
    "平面図形":"図形の性質",
    "整数":"整数の性質",

    "二項係数":"式と証明",
    "数II式と証明":"式と証明",
    "複素数と方程式":"複素数と方程式",
    "通過領域":"図形と方程式",
    "図形と方程式":"図形と方程式",
    "図形と領域":"図形と方程式",
    "三角関数":"三角関数",
    "指数対数":"指数関数と対数関数",
    "面積の組み換え":"微分法と積分法",
    "数II微積":"微分法と積分法",

    "平面ベクトル":"平面上のベクトル",
    "空間ベクトル":"空間のベクトル",
    "数B数列":"数列",
    "確率分布と統計的な推測":"確率統計",

    "数III複素数平面":"複素数平面",
    "数III曲線":"式と曲線",
    "数III関数":"関数",
    "数III極限":"極限",
    "数III微分":"微分法",
    "平均値の定理":"微分法",
    "数III積分":"積分法",
}

class VideoType(models.Model):
    name = models.CharField(max_length=10,unique=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('video_type-detail', args=[str(self.id)])


class VideoGenre(models.Model):
    name = models.CharField(max_length=10,unique=True)
    category = models.ForeignKey(Category,null=True,on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('video_genre-detail', args=[str(self.id)])
        