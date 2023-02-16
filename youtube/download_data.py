from django.db import models

from ugosite.models import Term,Category

from .models import ChannelSection,Playlist,PlaylistItem,Video,MY_CHANNEL_ID
from .models import ChannelId,ChannelSectionId,PlaylistId,VideoId
from .models import VideoType,VideoGenre,VIDEO_GENRE_TO_CAETEGORY,VIDEO_TYPE_CHOICES
from .models import University,Source

ALL_THUMBNAIL_DIR =  "/media_local/all_thumbnail/jpegs"

# ユーティリティ
import util.normalize as normalize
import util.text_transform as text_transform

import sys,re

from util.youtube_api import youtube_with_key
# from  util.youtube_api import youtube_with_auth

my_channel_id = ChannelId.objects.get(raw_text = MY_CHANNEL_ID)

class Download_Id:
    def channelSections(self):
        Download_Id().channelSectionIds_in_channel(my_channel_id)

    def playlists(self):
        Download_Id().playlistIds_in_channel(my_channel_id)
        for channelSectionId in ChannelSectionId.objects.all():
            Download_Id().playlistIds_in_channelSection(channelSectionId)
            
    def videos(self):
        uploads_playlistId = self.uploads_playlistId()
        Download_Id().videoIds_in_playlist(uploads_playlistId)
        for playlistId in PlaylistId.objects.all():
            Download_Id().videoIds_in_playlist(playlistId)


    def channelSectionIds_in_channel(self,channelId:ChannelId):#,pagetoken)
        print("チャンネル「%s」のセクションをダウンロードします" % channelId)
        res = youtube_with_key.channelSections().list(
            channelId = channelId.raw_text,
            part='snippet,contentDetails',
        ).execute()
        ChannelSectionResponses(res["items"]).save_each_channelSectionId()





    def playlistIds_in_channelSection(self,channelSectionId:ChannelSectionId):
        print("チャンネル「%s」のプレイリストをダウンロードします" % channelSectionId)
        res = youtube_with_key.channelSections().list(
            id = channelSectionId.raw_text,
            part='snippet,contentDetails',
        ).execute() 
        for law_playlistId in res["items"][0]["contentDetails"]["playlists"]:
            PlaylistId(raw_text = law_playlistId).add_to_local()

    def playlistIds_in_channel(self,channelId:ChannelId):
        print("チャンネル「%s」のPlaylistIdをダウンロードします" % channelId)
        pageToken = ""
        while True:
            res = youtube_with_key.playlists().list(
                channelId = channelId.raw_text,
                part='id',
                maxResults = 100,
                pageToken = pageToken
            ).execute() 

            PlaylistResponses(res["items"]).save_each_playlistId()
            try:
                pageToken = res["nextPageToken"]
                continue
            except:
                break

    def videoIds_in_playlist(self,playlistId:PlaylistId):
        print("プレイリスト「%s」内のVideoIdをダウンロード" % self)
        pageToken = ""
        while True:
            res = youtube_with_key.playlistItems().list(
                playlistId = playlistId.raw_text,
                part='snippet',
                maxResults = 100,
                pageToken = pageToken
            ).execute()
            PlaylistItemResponses(res["items"]).save_each_videoId()
            try:
                pageToken = res["nextPageToken"]
                continue
            except:
                break

    def uploads_playlistId(self):
        print("Cannnel「%s」のアップロード動画のplaylistIdを取得します" % my_channel_id)
        res = youtube_with_key.channels().list(
            id = my_channel_id,
            part="contentDetails"
        ).execute()
        channel_data = res["items"][0]
        return PlaylistId(raw_text = channel_data["contentDetails"]["relatedPlaylists"]["uploads"])
    





class Download_Response:
    def channelSections(self):
        ChannelSectionResponse.objects.all().delete()
        for channelSectionId in ChannelSectionId.objects.all():
            Download_Response().channelSection_from_channelSectionId(channelSectionId)

    def playlists(self):
        PlaylistResponse.objects.all().delete()
        for playlistId in PlaylistId.objects.all():
            Download_Response().playlist_from_playlistId(playlistId)
        
    
    def playlistItems(self):
        PlaylistItemResponse.objects.all().delete()
        for playlistId in PlaylistId.objects.all():
            Download_Response().playlistItems_from_playlistId(playlistId)

    def videos(self):
        VideoResponse.objects.all().delete()
        for videoId in VideoId.objects.all():
            Download_Response().video_from_videoId(videoId)
        


    def channelSection_from_channelSectionId(self,channelSectionId:ChannelSectionId):#,pagetoken)
        print("チャンネル「%s」のセクションをダウンロードします" % channelSectionId)
        res = youtube_with_key.channelSections().list(
            id = channelSectionId.raw_text,
            part='snippet,contentDetails',
        ).execute()
        ChannelSectionResponse.objects.create(json_data = res["items"][0])

    def playlist_from_playlistId(self,playlistId:PlaylistId):
        print("プレイリスト「%s」をダウンロード" % playlistId)
        pageToken = ""
        res = youtube_with_key.playlists().list(
            id = playlistId.raw_text,
            part='snippet',
            maxResults = 100,
            pageToken = pageToken
        ).execute()
        PlaylistResponse.objects.create(json_data = res["items"][0])

    def playlistItems_from_playlistId(self,playlistId:PlaylistId):
        print("プレイリスト「%s」のプレイリストアイテムをダウンロード" % self)
        pageToken = ""
        while True:
            res = youtube_with_key.playlistItems().list(
                playlistId = playlistId.raw_text,
                part='snippet',
                maxResults = 100,
                pageToken = pageToken
            ).execute()
            PlaylistItemResponses(res["items"]).save_each_data()
            try:
                pageToken = res["nextPageToken"]
                continue
            except:
                break

    def video_from_videoId(self,videoId:VideoId):
        print("Youtubeからビデオ「%s」をダウンロード" % self)
        res = youtube_with_key.videos().list(
            id = videoId.raw_text,
            part='snippet',
        ).execute()
        VideoResponse.objects.create(json_data = res["items"][0])
        # print("Video「%s」のデータを更新しました" % self)
    


class Create_Models:
    def videos(self):
        Video.objects.all().delete()
        for video_res in VideoResponse.objects.all():
            print("「%s」からVideoを作成" % video_res)
            video_res.create_model()

    def playlists(self):
        Playlist.objects.all().delete()
        for playlist_res in PlaylistResponse.objects.all():
            print("「%s」からPlaylistを作成" % playlist_res)
            playlist_res.create_model()

    def playlistItems(self):
        PlaylistItem.objects.all().delete()
        for playlistItem_res in PlaylistItemResponse.objects.all():
            print("「%s」からPlaylistItemを作成" % playlistItem_res)
            playlistItem_res.create_model()
            

    def channelSections(self):
        ChannelSection.objects.all().delete()
        for channelSection_res in ChannelSectionResponse.objects.all():
            print("「%s」からChannelSectionを作成" % channelSection_res)
            channelSection_res.create_model()

    def videoTypes(self):
        VideoType.objects.all().delete()
        for type in VIDEO_TYPE_CHOICES:
            VideoType.objects.create(name = type[0])

    def videoGenres(self):
        VideoGenre.objects.all().delete()
        genre_name_list = [playlist.genre_name() for playlist in PlaylistResponse.objects.all()]
        genre_name_list = list(set(genre_name_list))
        for name in genre_name_list:
            VideoGenre.objects.create(name = name)

class Add_Relation:
    def videos(self):
        for video in Video.objects.all():
            if not video.main_playlist() :continue
            video.video_type = video.main_playlist().video_type
            video.video_genre = video.main_playlist().video_genre
            video.save()

    def videos_to_terms(self):
        def isRelate(video:Video,term:Term):
            if term.name in video.title : return True
            if term.name in video.problem :return True
            if term.name in video.point :return True
            return False

        for term in Term.objects.all():
            for video in Video.objects.all():
                if term in video.terms.all():continue
                if isRelate(video,term):
                    print(f"Term({term})をVideo({video})に追加します")
                    video.terms.add(term)


class ChannelSectionResponses:
    def __init__(self,list:list[object]):
        self.list = list

    def save_each_data(self):
        for data in self.list:
            if not data["snippet"]["type"] == "multipleplaylists" : continue
            ChannelSectionResponse.objects.create(json_data = data)

    def save_each_channelSectionId(self):
        for data in self.list:
            if not data["snippet"]["type"] == "multipleplaylists" : continue
            ChannelSectionId(raw_text = data["id"]).add_to_local()

class PlaylistResponses:
    def __init__(self,list:list[object]):
        self.list = list

    def save_each_data(self):
        for data in self.list:
            PlaylistResponse.objects.create(json_data = data)

    def save_each_playlistId(self):
        for data in self.list:
            PlaylistId(raw_text = data["id"]).add_to_local()

class PlaylistItemResponses:
    def __init__(self,list:list[object]):
        self.list = list

    def save_each_data(self):
        for data in self.list:
            PlaylistItemResponse.objects.create(json_data = data)

    def save_each_videoId(self):
        for data in self.list:
            VideoId(raw_text = data["snippet"]['resourceId']["videoId"]).add_to_local()

class VideoResponses:
    def __init__(self,list:list[object]):
        self.list = list

    def save_each_data(self):
        for data in self.list:
            response = VideoResponse.objects.create(json_data = data)



class ChannelSectionResponse(models.Model):
    json_data = models.JSONField()

    def channelSectionId(self):
        return ChannelSectionId.objects.get(raw_text=self.json_data["id"])
    
    def title(self):
        return self.json_data["snippet"]["title"]
    
    def type(self):
        return self.json_data["snippet"]["type"]

    def playlists(self):
        playlists = []
        for raw_playlistId in self.json_data["contentDetails"]["playlists"]:
            playlistId = PlaylistId.objects.get(raw_text = raw_playlistId)
            playlist = Playlist.objects.get(playlistId = playlistId)
            playlists.append(playlist)
        return playlists
    
    
    def create_model(self):
        print(self.type())
        print(self.title())
        if not self.type() == "multipleplaylists" : return
        ChannelSection.objects.create(
            channelSectionId = self.channelSectionId(),
            title = self.title()
        )
        


class PlaylistResponse(models.Model):
    json_data = models.JSONField()

    def __str__(self):
        return self.title()

    def playlistId(self):
        return PlaylistId.objects.get(raw_text = self.json_data["id"])

    def title(self):
        return self.json_data["snippet"]["title"]

    def description(self):
        return self.json_data["snippet"]["description"]
    

    
    def type_name(self):
        s = re.findall("\s(.*?)\d",self.title())
        if not s:return "他"
        type_name = s[0]
        if not type_name in [choice[0] for choice in VIDEO_TYPE_CHOICES]:return "他"
        return type_name
    
    def genre_name(self):
        s = re.findall("(.*?)\s",self.title())
        if not s : return "他"
        return s[0]
    
    def category(self):
        try:
            category_name = VIDEO_GENRE_TO_CAETEGORY[self.genre_name()]
            return Category.objects.filter(type = "CHA").get(name = category_name)
        except:
            input(self.genre_name())
            return None
    
    def video_type(self):
        try: return VideoType.objects.get(name = self.type_name())
        except: return VideoType.objects.create(name = self.type_name())
    
    def video_genre(self):
        try: return VideoGenre.objects.get(name = self.genre_name())
        except: return VideoGenre.objects.create(
            name = self.genre_name(),
            category = self.category()
        )
    
    def create_model(self):
        Playlist.objects.create(
            playlistId = self.playlistId(),
            title = self.title(),
            description = self.description(),
            video_type = self.video_type(),
            video_genre = self.video_genre()
        )



    def update_on_youtube(self):
        response = youtube_with_auth.playlists().update(
            part="snippet,status",
            body=self.json_data
        ).execute()
        print("プレイリスト「%s」が更新されました" % response["snippet"]["title"])
        self.data = response
        self.save()


class PlaylistItemResponse(models.Model):
    json_data = models.JSONField()

    def title(self):
        return self.json_data["snippet"]["title"]
    
    def videoId(self):
        return VideoId.objects.get(raw_text=self.json_data["snippet"]['resourceId']["videoId"])
    
    def playlistId(self):
        return PlaylistId.objects.get(raw_text=self.json_data["snippet"]["playlistId"])
    
    def __str__(self):
        return self.title()
    
    def position(self):
        return self.json_data["snippet"]["position"]

    def video(self):
        return Video.objects.get(videoId = self.videoId())
        
    def playlist(self):
        return Playlist.objects.get(playlistId = self.playlistId())

    def create_model(self):
        PlaylistItem.objects.create(
            video = self.video(),
            playlist = self.playlist(),
            position = self.position(),
        )

import os

class VideoResponse(models.Model):
    json_data = models.JSONField()
    new_json_data = models.JSONField(null=True,blank = True,help_text='補正後のデータです。')

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title()

    def videoId(self):
        return VideoId.objects.get(raw_text=self.json_data["id"])
    
    def title(self):
        return self.json_data["snippet"]["title"]
    
    def description(self):
        return self.json_data["snippet"]["description"]
    
    def thumbnail_url(self):
        def exist_local_thumnail():
            local_path = ".%s/%s.jpeg" % (ALL_THUMBNAIL_DIR,self.videoId())
            abs_path = os.path.abspath(local_path)
            return os.path.isfile(abs_path)
        
        if exist_local_thumnail():
            return "/media/all_thumbnail/jpegs/%s.jpeg" % self.videoId()
        return None #self.json_data["snippet"]["thumbnails"]["high"]["url"]

    def title_in_mytex(self):
        text = text_transform.line_to_tex(self.title())
        text = text.replace("$ ","$").replace(" $","$")
        return text
    
    def extract_item(self,item_name:str):
        description = self.description()
        items = re.findall("＜%s＞\n([\s\S^＜]*?)(?:\n\n|$)" % item_name,description)
        if len(items)==0 : return ""
        if len(items)==1 : return items[0].replace("\n ","\n")
        if len(items)>1 : return "\n\n".join(items).replace("\n ","\n")
    
    def extract_item_in_jax(self,item_name:str):
        item = self.extract_item(item_name)
        if not item: return ""
        item = text_transform.text_to_tex(item)
        item = text_transform.transform_to_html_list(item)
        return item 

    def main_playlist(self):
        playlists = self.playlists()
        if len(playlists)==0:return
        if len(playlists)==1:
            return playlists[0]
        for playlist in playlists:
            for type in VIDEO_TYPE_CHOICES:
                if type[1] in playlist.title():
                    return playlist
        playlists[0]

    
    ### Source関係

    def university_name(self):
        source_text = self.extract_item("ソース")
        s = re.findall("[^\s\d]*大|共通1次|共通テスト",source_text)
        if not s : return
        return s[0]

    def university(self):
        try:
            return University.objects.get(name = self.university_name())
        except:
            return University.objects.create(name = self.university_name())
        
    def year(self):
        source_text = self.extract_item("ソース")
        y = re.findall("\d{4}|\d{2}",source_text)
        if not y : return int()
        year_text = y[0]
        if len(year_text)==2:
            year_last_two_digits = int(year_text)
            if year_last_two_digits>23:
                return 1900+year_last_two_digits
            if year_last_two_digits<=23:
                return 2000+year_last_two_digits
        if len(year_text)==4:
            return int(year_text)
        
    def question_num(self):
        source_text = self.extract_item("ソース")
        q = re.findall("第(\d)問",source_text)
        if not q : return int()
        return int(q[0])
        
    
    def division(self):
        result = self.extract_item("ソース")
        result = re.sub(self.university_name(),"",result)
        result = re.sub("\d{2}|\d{4}","",result)
        result = re.sub("年度|年","",result)
        result = re.sub("第(\d)問","",result)
        return result

    def source(self):
        try:
            return Source.objects.get(
                university = self.university(),
                division = self.division(),
                year = self.year(),
                question_num = self.question_num()
            )
        except:
            return Source.objects.create(
                university = self.university(),
                division = self.division(),
                year = self.year(),
                question_num = self.question_num()
            )
        
    ### Term に関するもの ###

    def keywords(self):
        def split_each_string(list:list[str],sign:str):
            result = []
            for string in list:
                for splited_string in string.split(sign):
                    if not splited_string.strip(): continue
                    result.append(splited_string)
            return result
        
        result = self.extract_item("キーワード").split("#")
        result = split_each_string(result,"、")
        result = split_each_string(result,"，")
        return result

    def tags_in_json_data(self):
        result = []
        for tag in self.json_data["snippet"]["tags"]:
            result.append(tag.replace(" ",""))
        return result
    
    def tags_in_description(self):
        return re.findall("#(.)[\s\n$]",self.description())
        
    def term_names(self):
        def isOKAsTerm(term_name:str):
            f = re.findall("\d{4}|年|大学|はやくち|解説|school|高校|第\d問|問\d|理系|文系|浪人|授業|入試|入学|：|難関|.*大$|.*大学$|^数学$|京大数学|一橋|過去問|II|受験|初めの問題|後期",term_name)
            if f: return False
            return True 
        
        def correct(term_name:str):
            correct_list = [["順象法","順像法"],["逆象法","逆像法"],["図形的意味を読み取る","図形的な考察"],["四面体の体積公式","四面体の体積"],["内分点の公式","内分点"],["^ある$","ある〇〇"],["^すべての$","すべての〇〇"]]
            result = term_name.strip()
            for c in correct_list:
                result =  re.sub(c[0],c[1],result)
            return result
        
        result = []
        for term_name in self.keywords()+self.tags_in_description()+self.tags_in_json_data():
            if isOKAsTerm(term_name.strip()):
                result.append(correct(term_name.strip()))
        return result
    
    def terms(self):
        result = []
        for term_name in self.term_names():
            try:
                term = Term.objects.get(name = term_name)
            except:
                term = Term.objects.create(name = term_name)
            result.append(term)
        return result

    def create_model(self):
        video = Video.objects.create(
            videoId = self.videoId(),
            title = self.title(),
            problem = self.extract_item_in_jax("問題"),
            point = self.extract_item("要点"),
            thumbnail_url = self.thumbnail_url()
        )
        table_text = self.extract_item("目次")
        if table_text:
            video.table_list = table_text.replace(",","，").replace("\n",",")
            video.save()
        if self.extract_item("ソース"):
            video.source = self.source()
            video.save()
        if self.extract_item("キーワード"):
            video.terms.add(*self.terms())







    ### json_dataを書き換える

    def set_title(self,title:str):
        self.new_json_data = self.data
        self.new_json_data["snippet"]["title"] = title
        return self
    
    def set_description(self,text):
        self.new_json_data = self.data
        self.new_json_data["snippet"]["description"] = text
        return self
    
    def set_problem(self,text):
        self.new_json_data = self.data
        description = self.description()
        if not "＜問題＞" in description: return self
        description = re.sub("＜問題＞\n[\s\S]*?(\n\n|$)","＜問題＞\n%s\\1" % text,description)
        description = normalize.clean_up_lines(description)
        self.new_json_data["snippet"]["description"] = description
        return self
    
    def rewrite_title(self):
        title = self.title()
        old_title = title

        new_title =  title
        if old_title == new_title : return self
        self.set_title(title)
        print(title)
        return self
    
    def rewrite_problem(self):
        if not self.extract_item("問題"):return self
        old_text = self.extract_item("問題")
        text = old_text
        a = re.search("\\\\vec\{[a-z]\}",text)
        if not a: return self
        text = re.sub("\\\\vec\{([a-z])\}","ベクトル\\1",text)
        new_text = text
        if new_text == old_text: return self
        self.set_problem(text)
        print("\n「%s」の問題文を変更しました:\n%s\n" % (self,self.description()))
        return self

    def update_on_youtube(self):
        response = youtube_with_auth.videos().update(
            part = "snippet,status",
            body = self.new_json_data
        ).execute()
        print("ビデオ「%s」が更新されました" % response["snippet"]["title"])
        self.data = response
        self.new_json_data  = None
        self.save()
