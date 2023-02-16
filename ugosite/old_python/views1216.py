# from asyncio.windows_events import NULL
from ast import Num
from email import contentmanager
from importlib.resources import contents
# from types import NoneType
from django.shortcuts import render

# Create your views here.

# ここからがUgosuu

from .models import MyFile,Category, Article, Source, Term,  Problem
from django.contrib.auth.models import User #Blog author or author
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import generic

from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.urls import reverse

from django.views.generic import TemplateView

import os 

import re


from googletrans import Translator
tr = Translator()
tr.raise_Exception = True



import unicodedata

# ユーティリティ
from util.normalize import join_diacritic


def index(request):
    """View function for home page of site."""
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_categorys' : Category.objects.all().count(),
        'num_articles': Article.objects.all().count(),
        'num_problems' : Problem.objects.all().count(),
        'num_problems_of_univ' : Problem.objects.filter(source__isnull = False).count(),
        'num_videos' : YotubeVideo.objects.all().count(),
        'num_terms': Term.objects.all().count(),
        'num_visits': num_visits,
        'article_list' : Article.objects.all()[:3],
        'category_list' : Category.objects.filter(parent__isnull=True)
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


import pprint

class ArticleDetailView(generic.DetailView):
    model = Article
    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView,self).get_context_data(**kwargs)
        url = "articles/"+self.kwargs['id']+".html"
        context['template'] = os.path.isfile("ugosite/templates/"+url)
        context['html'] = url
        article = context["article"]
        if article.categorys.all():
            category = article.categorys.all()[0]
            articles = Article.objects.filter(parent = category)
            index = list(articles).index(article)
            if not len(articles) == index+1:
                context['next'] = articles[index+1].get_absolute_url()
            if not index-1<0:
                context['prev'] = articles[index-1].get_absolute_url()
            context['up'] = category.get_absolute_url()
        context['ancestors'] = article.ancestors()
        context['category'] = article.category
        context['self'] = article
        return context

class ArticleListView(generic.ListView):
    model = Article
    paginate_by = 500


class TermDetailView(generic.DetailView):
    model = Term


class TermListView(generic.ListView):
    model = Term
    paginate_by = 500


class CategoryDetailView(generic.DetailView):
    model = Category
    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView,self).get_context_data(**kwargs)
        context["categorys"] = [context["category"]]
        return context

class CategoryListView(generic.ListView):
    model = Category
    def get_context_data(self, **kwargs):
        context = super(CategoryListView,self).get_context_data(**kwargs)
        context["category_list"] = Category.objects.filter(parent__isnull = True)
        context["article_list"] = Article.objects.all()
        return context


class ProblemDetailView(generic.DetailView):
    def get_context_data(self, **kwargs):
        context = super(ProblemDetailView,self).get_context_data(**kwargs)
        problem = context["problem"]
        category = problem.categorys.all()[0]
        context["category"] = category
        problems = Problem.objects.filter(categorys = category) 
        index = list(problems).index(problem)
        if not len(problems) == index+1:
            context['next'] = problems[index+1].get_absolute_url()
        if not index-1<0:
            context['prev'] = problems[index-1].get_absolute_url()
        context['up'] = problem.get_absolute_url()
        context['ancestors'] =  category.ancestors()+[category]
        context['self'] = problem
        return context
    model = Problem

class ProblemListView(generic.ListView):
    model = Problem
    paginate_by = 100

import certifi
certifi.where()

        
# class Update_From_Source(Category):
#     def copy_from_myfile(self,myfile):
#         self.name = myfile.name
#         self.path = myfile.path
#         return self
        
#     def baseFile(self):
#         MyFile.objects.filter(name = self.name).delete()
#         return MyFile.objects.create(
#             name = self.name,
#             path = self.path
#         )
#     def baseCategory(self):
#         Category.objects.filter(name = self.name).delete()
#         return Category.objects.create(
#             name = self.name,
#             path = self.path
#         )

#     def Koukousuugaku(self):
#         self.baseCategory().update_excelfiles()
    
#     def Icons(self):
#         self.baseFile().update_icons()

#     def Myfile(self):
#         self.baseCategory().update_my_folder()

#     def Kakomon(self):
#         self.baseCategory().update_kakomon_folder()

#     def Note(self):
#         self.baseCategory().update_note()
                
# Update_From_Source(
#     name = "高校数学",
#     path = "/Users/greenman/Desktop/web-projects/django_projects/ugosite/ugosite/math_data"
# ).Koukousuugaku()
        
# Update_From_Source(
#     name = "icons",
#     path = "/Users/greenman/Desktop/web-projects/django_projects/ugosite/media_local/icons"
# ).Icons()
        
# Update_From_Source(
#     name = "講師関係",
#     path = '/Users/greenman/Library/Mobile Documents/com~apple~CloudDocs/講師関係'
# ).Myfile()

# Update_From_Source(
#     name = "大学別62年過去問題集",
#     path = '/Users/greenman/Library/Mobile Documents/com~apple~CloudDocs/旧帝大過去問',
#     description = "このモジュールには、旧帝7大+東工大の過去62年の問題が含まれています。",
#     type = "T",
# ).Kakomon()
            
# Update_From_Source(
#     name = "Notes",
#     path = '/Users/greenman/Desktop/web-projects/django_projects/ugosite/media_local/Notes'
# ).Note()

import sys

import json

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

def print_json(JSON):
    data = json.dumps(JSON, indent=1,ensure_ascii=False)
    print(highlight(data, JsonLexer(), TerminalFormatter()))

# class Update_To_Source(Category):

#     def baseCategory(self):
#         Category.objects.filter(name = self.name).delete()
#         return Category.objects.create(
#             name = self.name,
#             path = self.path
#         )
    
#     def baseFile(self):
#         MyFile.objects.filter(name = self.name).delete()
#         return MyFile.objects.create(
#             name = self.name,
#             path = self.path
#         )

#     def Koukousuugaku(self):
#         self.baseCategory().update_excelfiles()
            
    
#     def Icons(self):
#         self.baseFile().update_icons()

#     def Myfile(self):
#         self.baseCategory().update_my_folder()

#     def Kakomon(self):
#         self.baseCategory().update_kakomon_folder()

#     def Note(self):
#         self.baseCategory().update_note()

        
### Youtubeアップロード ###

from .models import YoutubeChannel,YoutubePlaylist,YoutubePlaylistItem,YoutubeVideo,YoutubeChannelSection

MY_CHANNEL_ID = "UCtEVdDYltR4eWf-QXvjmCJQ"

class YoutubeDownloader:
    def download_playlists(self):
        YoutubePlaylist.objects.all().delete()
        cannel = YoutubeChannel(channelId = MY_CHANNEL_ID)
        cannel.download_playlists()

    def download_playlistItems(self):
        YoutubePlaylistItem.objects.all().delete()
        playlists = YoutubePlaylist.objects.all()
        for playlist in playlists:
            playlist.download_playlistItems()

    def download_videos(self):
        # YoutubeVideo.objects.all().delete()
        cannel = YoutubeChannel(channelId = MY_CHANNEL_ID)
        playlistItems = cannel.download_uploads_playlistItems()
        for playlistItem in playlistItems:
            playlistItem.download_video()

    def download_sections(self):
        YoutubeChannelSection.objects.all().delete()
        cannel = YoutubeChannel(channelId = MY_CHANNEL_ID)
        cannel.download_sections()
        
    # download_youtube_data()

# YoutubeDownloader().download_videos()
# YoutubeDownloader().download_playlists()
# YoutubeDownloader().download_playlistItems()
# YoutubeDownloader().download_sections()

class YoutubeUpdater:
    def make_new_datas(self):
        videos = YoutubeVideo.objects.all()
        for i,video in enumerate(videos):
            print("\n\n%s:%s" % (i,video))
            video.rewrite_title()
            video.save()
        updated_videos = YoutubeVideo.objects.filter(new_data__isnull = False)
        print("\n書き換え予定の問題の数：%s" % updated_videos.count())


    def update_videos(self):
        videos = YoutubeVideo.objects.filter(new_data__isnull = False)
        for i,video in enumerate(videos):
            print("\n\n%s:「%s」を更新中。。。" % (i,video))
            video.update_on_youtube()
            print(" 。。。更新成功")
        print("\n更新された問題の数：%s" % videos.count())

    # create_updated_videos()
    

    def update_playlists(self):
        playlists = YoutubePlaylist.objects.all()
        # playlists = YoutubePlaylist.objects.filter(data__snippet__description__icontains = "数列")#.exclude(data__snippet__title__icontains = "強化")
        for i,playlist in enumerate(playlists):
            print("\n\n%s:「%s」を更新中。。。" % (i,playlist))
            playlist.rewrite_title()
            print(playlist)
            playlist.update_on_youtube()
            # playlist.save()
        print("\n更新されたプレイリストの数：%s" % playlists.count())

# YoutubeDownloader().download_videos()
# YoutubeUpdater().make_new_datas()
# YoutubeUpdater().update_videos()

# YoutubeUpdater().update_playlists()

# print(YoutubePlaylist.objects.count())

class YoutubeUploader:
    def create_playlist(self,title,description):
        return YoutubePlaylist.objects.create(
            data = {
                "snippet": {
                    "title": title,
                    "description": description
                },
                "status": {
                    "privacyStatus": "private"
                }
            }
        ).insert_on_youtube()
        
# YoutubeUploader().test()
    
from django.utils import timezone
import subprocess

class PDFGenerater:
    def make_texfile(self):
        sections = YoutubeChannelSection.objects.filter(data__snippet__type = "multipleplaylists")
        texts = []
        for section in sections:
            section_title = section.title()
            texts.append("\\section{%s}" % section_title)
            playlists =  section.playlists()
            for playlist in playlists:
                playlist_title = playlist.title()
                texts.append("\\subsection{%s}" % playlist_title)
                items = playlist.playlistItems()
                for item in items:
                    video = item.video()
                    if not video:continue
                    text = self.to_tex(video)
                    texts.append(text)
                    # texts.append("\\newpage")
        template_path = './notes/texs/templates/youtube_video_problems.tex'
        content_path =  "./notes/texs/youtube_video_problems.tex"
        t = open(template_path, 'r')
        template_text = t.read()
        f = open(content_path, 'w')#  % timezone.now()
        file_text = template_text.replace("{{template}}","\n\n".join(texts))
        f.write(file_text)
        f.close()

    def to_tex(self,video:YoutubeVideo):
        video_title = video.extract_title_in_mytex()
        problem_text = video.extract_problem_in_mytex()
        if not problem_text:return ""
        text = """\n\n\\begin{question}{\\bf\\boldmath %s}\\\\\n%s\n\\end{question}""" % (video_title,problem_text)    
        return text


# YoutubeDownloader().update_videos()
# PDFGenerater().make_texfile()
# FileTranformer().ptex2pdf("./notes/texs/youtube_video_problems.tex","./notes/texs")


from thumbnails.thumbnail import ThumbnailGenerator        












from .models import VideoOnApp

import random

class RandomPresentationSystem:
    def make_from_youtube_videos(self):
        videos = YoutubeVideo.objects.all()
        for i,video in enumerate(videos):
            # print("\n\n%s:%s" % (i,video))
            video_on_app = VideoOnApp.objects.create(
                youtube_video = video
            )
            print(video_on_app)
    
    def select(self,videos):
        random_num = random.randrange(len(videos))
        selected_video = videos[random_num]
        return selected_video

    def test():
        videos = VideoOnApp.objects.filter(data__snippet__title__icontains = "2次関数")
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

# RandomPresentationSystem().make_from_youtube_videos()

class VideoOnAppListView(generic.ListView):
    model = VideoOnApp
    def get_context_data(self, **kwargs):
        # RandomPresentationSystem().read_data_from_youtube_videos()
        context = super(VideoOnAppListView,self).get_context_data(**kwargs)
        videos = VideoOnApp.objects.all()
        selected_video = RandomPresentationSystem().select(videos)
        context["video"] = selected_video
        return context

# SumbnailGenerater().make_texfile()

from .models import YoutubePlaylist,YoutubePlaylistItem,Question,QuestionSet

class ArticleGenerater:
    # def make_from_playlist(self):
    def test(self):
        sections = YoutubeChannelSection.objects.filter(data__snippet__type = "multipleplaylists")
        for k,section in enumerate(sections):
            print("\n\n%s:%s" % (k+1,section))
            playlists = section.get_playlists()
            for i,playlist in enumerate(playlists):
                print(" %s:%s" % (i+1,playlist))
                playlistItems = playlist.get_playlistItems()
                for j,playlistItem in enumerate(playlistItems):
                    print("  %s:%s" % (j+1,playlistItem))
                    video = playlistItem.get_video()

    def make_from_playlists(self):
        for i,playlist in enumerate(YoutubePlaylist.objects.all()):
            print(" %s:%s" % (i+1,playlist))
            QuestionSet().make_from_playlist(playlist)
                    
    def display_statue(self):
        playlists = YoutubePlaylist.objects.all()
        Items = YoutubePlaylistItem.objects.all()
        videos = YoutubeVideo.objects.all()
        sections = YoutubeChannelSection.objects.all()
        videos_on_app = VideoOnApp.objects.all()
        print("YoutubeChannelSectionの個数: %s" % len(sections))
        print("YoutubePlaylistの個数: %s" % len(playlists))
        print("YoutubePlaylistItemの個数: %s" % len(Items))
        print("YoutubeVideoの個数: %s" % len(videos))
        print("VideoOnAppの個数: %s" % len(videos_on_app))

# ArticleGenerater().test()
 
# ArticleGenerater().make_from_playlists()
# ArticleGenerater().display_statue()
