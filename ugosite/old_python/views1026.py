# from asyncio.windows_events import NULL
from ast import Num
from email import contentmanager
from importlib.resources import contents
# from types import NoneType
from django.shortcuts import render

# Create your views here.

# ここからがUgosuu

from .models import Module, Article, Term, Genre, Problem
from django.contrib.auth.models import User #Blog author or author
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import generic

from django.shortcuts import get_object_or_404

def index(request):
    """View function for home page of site."""
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_articles': Article.objects.all().count(),
        'num_terms': Term.objects.all().count(),
        'num_videos' : Video.objects.all().count(),
        'num_problems' : Problem.objects.all().count(),
        'num_modules' : Module.objects.all().count(),
        'num_visits': num_visits,
        'article_list' : Article.objects.all()[:3],
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class GenreDetailView(generic.DetailView):
    def get_context_data(self, **kwargs):
        context = super(GenreDetailView,self).get_context_data(**kwargs)
        genre = context["genre"]
        if genre.parent_genre:
            genres = Genre.objects.filter(parent_genre = genre.parent_genre)
            context['up'] = genre.parent_genre.get_absolute_url()
        else:
            genres = Genre.objects.filter(parent_genre__isnull = True)
        index = list(genres).index(genre)
        if not len(genres) == index+1:
            context['next'] = genres[index+1].get_absolute_url()
        if not index-1<0:
            context['prev'] = genres[index-1].get_absolute_url()
        context['ancestors'] = genre.ancestors()
        context['self'] = genre
        return context
    model = Genre

# from flask import Flask, request

import pprint

def problemEditView(request,slug):
    if request.method == 'POST' :
        # pprint.pprint(request.POST)
        # pprint.pprint(list(request.POST.keys()))
        for p_slug in list(request.POST.keys())[2:]:
            # print(p_slug)
            problem = Problem.objects.get(slug = p_slug)
            g_slug = request.POST.get(p_slug,None)
            if g_slug:
                genre = Genre.objects.get(slug = g_slug)
                # print(problem)
                # print(genre)
            problem.genres.clear()
            problem.genres.add(genre)
        context = {
            'genre':Genre.objects.get(slug = slug)
        }
        return render(request, "ugosite/genre_detail.html", context)


class GenreListView(generic.ListView):
    model = Genre
    def get_context_data(self, **kwargs):
        context = super(GenreListView,self).get_context_data(**kwargs)
        context["genre_list"] = Genre.objects.filter(parent_genre__isnull = True)
        return context
    paginate_by = 500

import os 

class ArticleDetailView(generic.DetailView):
    model = Article
    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView,self).get_context_data(**kwargs)
        url = "articles/"+self.kwargs['slug']+".html"
        context['template'] = os.path.isfile("ugosite/templates/"+url)
        context['html'] = url
        article = context["article"]
        if article.modules.all():
            module = article.modules.all()[0]
            articles = Article.objects.filter(modules = module)
            index = list(articles).index(article)
            if not len(articles) == index+1:
                context['next'] = articles[index+1].get_absolute_url()
            if not index-1<0:
                context['prev'] = articles[index-1].get_absolute_url()
            context['up'] = module.get_absolute_url()
        context['ancestors'] = article.ancestors()
        context['module'] = article.modules.first()
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


class ModuleDetailView(generic.DetailView):
    model = Module
    def get_context_data(self, **kwargs):
        context = super(ModuleDetailView,self).get_context_data(**kwargs)
        module = context["module"]
        if module.parent_module:
            modules = Module.objects.filter(parent_module = module.parent_module)
            context['up'] = module.parent_module.get_absolute_url()
        else:
            modules = Module.objects.filter(parent_module__isnull = True)
        index = list(modules).index(module)
        if not len(modules) == index+1:
            context['next'] = modules[index+1].get_absolute_url()
        if not index-1<0:
            context['prev'] = modules[index-1].get_absolute_url()
        context['ancestors'] = module.ancestors()
        context['self'] = module
        return context
    

class ModuleListView(generic.ListView):
    model = Module
    def get_context_data(self, **kwargs):
        context = super(ModuleListView,self).get_context_data(**kwargs)
        context["module_list"] = Module.objects.filter(parent_module__isnull = True)
        return context
    paginate_by = 500


class ProblemDetailView(generic.DetailView):
    def get_context_data(self, **kwargs):
        context = super(ProblemDetailView,self).get_context_data(**kwargs)
        problem = context["problem"]
        genre = problem.genres.all()[0]
        context["genre"] = genre
        problems = Problem.objects.filter(genres = genre) 
        index = list(problems).index(problem)
        if not len(problems) == index+1:
            context['next'] = problems[index+1].get_absolute_url()
        if not index-1<0:
            context['prev'] = problems[index-1].get_absolute_url()
        context['up'] = problem.get_absolute_url()
        context['ancestors'] = ancestors = genre.ancestors()+[genre]
        context['self'] = problem
        return context
    model = Problem

class ProblemListView(generic.ListView):
    model = Problem
    paginate_by = 100

def add_univ_module():
    Module.objects.filter(name = "大学別過去問題集").delete()
    univprop = Module.objects.create(
        name = "大学別過去問題集",
        slug = "univ-problems",
        description = "このモジュールには、旧帝7大+東工大の過去62年の問題が含まれています。",
        type = "T",
    )

    for module in Module.objects.filter(name__contains = "過去問"):
        module.parent_module = univprop
        module.save()
        # article.title = article.headline
        # article.save()
        print(module.name)

# add_univ_module()




### Youtube ###

from .models import Video, Playlist

from django.views.generic import TemplateView

replaceRule = []
replaceRule += [["＜","&lt;"],["＞","&gt;"]]
replaceRule += [["・","\cdot"],["…","\cdots"]]
replaceRule += [["⁰","^0"],["¹","^1"],["²","^2"],["³","^3"],["⁴","^4"],["⁵","^5"],["ⁿ","^n"],["⁻","^-"],["⁺","^+"]]
replaceRule += [["₀","_0"],["₁","_1"],["₂","_2"],["₃","_3"],["₄","_4"],["₅","_5"],["₈","_8"],["₉","_9"],["ₓ","_x"],["ₐ","_a"]]
replaceRule += [["√","\\sqrt "],["≦","\\leqq "],["≧","\\geqq "],["≠","\\neq "],["→","\\to "]]
replaceRule += [["\\frac","\\displaystyle\\frac"],["\\vec","\\overrightarrow"]]
replaceRule += [["π","\\pi "],["α","\\alpha "],["β","\\beta "],["γ","\\gamma"],["θ","\\theta "]]
replaceRule += [["∠","\\angle "],["△","\\triangle "],["◦","^\\circ "],["°","^\\circ "]]
replaceRule += [["log","\\log "],["sin","\\sin "],["cos","\\cos "],["tan","\\tan "]]
replaceRule += [["lim","\\displaystyle\\lim"],["∫","\\displaystyle\\int"],["∑","\\displaystyle\\sum"],["Σ","\\displaystyle\\sum"]]
replaceRule += [["nCr","_nC_r"]]

class VideoDetailView(generic.DetailView):
    model = Video
    def get_context_data(self, **kwargs):
        context = super(VideoDetailView,self).get_context_data(**kwargs)
        context["editUrl"] = "https://studio.youtube.com/video/"+self.kwargs['slug']+"/edit"
        return context

class VideoListView(generic.ListView):
    model = Video
    paginate_by = 50

class VideoUpdate(UpdateView):
    model = Video
    fields = ['genres']

    def get_success_url(self): 
        return reverse('video-detail', kwargs={'slug': self.kwargs['slug']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.first()
        return context

class PlaylistDetailView(generic.DetailView):
    model = Playlist

class PlaylistListView(generic.ListView):
    model = Playlist
    paginate_by = 50



#コメント機能


from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.urls import reverse

from .models import Comment

# @login_required
class CommentCreate(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['date']

    def get_context_data(self, **kwargs):
        context = super(CommentCreate, self).get_context_data(**kwargs)
        context['blog'] = get_object_or_404(Article, pk = self.kwargs['pk'])
        return context
        
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.article=get_object_or_404(Article, pk = self.kwargs['pk'])
        return super(CommentCreate, self).form_valid(form)

    def get_success_url(self): 
        return reverse('article-detail', kwargs={'pk': self.kwargs['pk'],})

class CommentUpdate(UpdateView):
    model = Comment
    fields = ['content']

    def get_context_data(self, **kwargs):
        context = super(CommentUpdate, self).get_context_data(**kwargs)
        # Get the blog from id and add it to the context
        context['article'] = context['comment'].blog
        return context


    def get_success_url(self):
        return reverse('author-detail', kwargs={'pk': self.request.user.id})

class CommentDelete(DeleteView):
    model = Comment

    def get_success_url(self, **kwargs): 
        context = super(CommentDelete, self).get_context_data(**kwargs)
        return reverse('article-detail', kwargs={'pk':context['comment'].article.id})

class UserCreate(CreateView):
    model = User
    fields = ['username','email', 'password']
    template_name = 'account_create.html'
    def get_success_url(self): 
        return reverse('index')




### ここからyoutubeDataの移行作業

from apiclient.discovery import build


import re

from googletrans import Translator
tr = Translator(service_urls=['translate.googleapis.com'])

youtube = build('youtube', 'v3', developerKey='AIzaSyD-ohN5V0dlXYHjP7lSrUgKcCgXDkjpR14')

from pykakasi import kakasi
kakasi = kakasi()
kakasi.setMode('J', 'H') 
conv = kakasi.getConverter()

import json

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

def get_uploads(channel_id):
    channels_response = youtube.channels().list(
    id=channel_id,
    part='contentDetails,snippet'
    ).execute()

    for channel in channels_response['items']:
        return channel['contentDetails']['relatedPlaylists']['uploads']

    return None


def downlaod_playlist_data(pagetoken,channel_id):
    # Playlist.objects.all().delete()
    # Genre.objects.all().delete()
    # Term.objects.all().delete()
    # Problem.objects.all().delete()
    # Video.objects.all().delete()
    print("チャンネル %s のplaylist_dataをdownlaodします" % channel_id)
    playlists = youtube.playlists().list(
        channelId = channel_id,
        part='snippet',
        maxResults = 100,
        pageToken=pagetoken
    ).execute()
    for playlist in playlists["items"]:
        title = playlist["snippet"]["title"].replace("Ⅲ","III")
        for p in Playlist.objects.all():
            if p.slug == playlist["id"]:
                print("Playlist: %s は既にあります" % p.title)
                break
        else:
            print("新しく、Playlist: %s を作成します。" % title)
            newPlaylist = Playlist.objects.create(
                slug = playlist["id"],
                title = title,
                description = playlist["snippet"]["description"]+title,
                data = playlist,
                type = "O"
            )
            # formatted_data=json.dumps(playlists ,indent=2,ensure_ascii=False)
            # print(highlight(formatted_data, JsonLexer(), TerminalFormatter()))
            newVideos = downlaod_video_data(playlist["id"])
            for newVideo in newVideos:
                newPlaylist.videos.add(newVideo)
    try:
        nextPagetoken = playlists["nextPageToken"] 
        # print(nextPagetoken)
        downlaod_playlist_data(nextPagetoken,channel_id)
    except:
        return

def downlaod_video_data(playlist_id):
    print("プレイリスト %s のvideoをdownlaodします" % playlist_id )
    # Playlist.objects.filter(slug = playlist_id).all()[0].videos.all().delete()
    playlistItems = youtube.playlistItems().list(
        playlistId=playlist_id,
        part='snippet',
        maxResults = 100
    ).execute()
    newVideos = []
    for playlistItem in playlistItems['items']:
        res = youtube.videos().list(
            id=playlistItem["snippet"]['resourceId']["videoId"],
            part='snippet',
            maxResults = 100
        ).execute()
        video = res["items"][0]
        # formatted_data=json.dumps(video ,indent=2,ensure_ascii=False)
        # print(highlight(formatted_data, JsonLexer(), TerminalFormatter()))
        for v in Video.objects.all():
            if v.slug == video["id"]:
                newVideo = v
                print("Video: %s は既にあります" % v.title)
                break;
        else:
            title = video["snippet"]["title"]
            name = title
            name = re.sub("(#\S+)","",name)
            name = re.sub("(【\S+】)","",name)
            slug = video["id"]
            print("新しく、Video: %s を追加します" % title)
            description = video["snippet"]["description"]
            description = description.replace("問 ","問．").replace("問　","問．").replace("問.","問．").replace("問：","問．").replace("． (","．(").replace(".(","．(").replace(". (","．(")
            problem = Problem(
                name = name,
                slug = slug,
            )
            newVideo = Video(
                name = name,
                title = title,
                slug = slug,
                description = description,
                data = video,
            )
            questions = re.findall("(問．(?:.+\n)+)\n",description)
            # print("questions %s" % questions)
            if questions:
                question = questions[0]
                sources = re.findall("\(.{,10}大.*\)",question)
                if sources:
                    source = sources[0]
                    question = question.replace(source,"")
                    source = source.replace("(","").replace(")","")
                    problem.source = source
                question = transform_question(question)
                problem.text = question
            problem.save()
            newVideo.problem = problem
            tables = re.findall("\d*:\d\d\s.*",description)
            if tables:
                newVideo.table = tables
            newVideo.save()
        newVideos += [newVideo]
    print(len(newVideos))
    return newVideos

# for video in Video.objects.all():
#     text = video.description.replace(",","_")
#     table = re.findall("\d*:\d\d\s.*", text)
#     if table:
#         video.table = table
#         print(table)
#         video.save()
    # if video.table:
    #     video.newTable = video.table.replace("'","").replace("[","").replace("]","")
    #     video.save()

def transform_question(question):
    text =  question.replace("　","").replace(" ","")
    texts = re.split("\n\([\d\w]\)|問．\([\d\w]\)",text)
    # print("sentences %s" % sentences)
    newtexts = []
    for text in texts:
        text =  join_diacritic(text)
        # text = re.sub("([^A-Eぁ-んァ-ヶ一-龠])，", "\\1, ",text)
        text = re.sub("([ぁ-んァ-ヶ一-龠々]),", "\\1，",text)
        text = re.sub("([ぁ-んァ-ヶ一-龠々])\.", "\\1．",text)
        text = re.sub("([ぁ-んァ-ヶ一-龠々])。", "\\1．",text)
        text = re.sub("([ぁ-んァ-ヶ一-龠々．，。、]*)([^ぁ-んァ-ヶ一-龠々．，。、\n\bー]+)([ぁ-んァ-ヶ一-龠々．，。、]*)", "\\1 $\\2$ \\3",text)
        text = re.sub("\n\s\$([^ぁ-んァ-ヶ一-龠々\n\b]+)\$\s\n","\\n\\[\\1\\]\\n",text)
        text = re.sub("(\\[.*)$(.*)$(.*\\])","\\1\\2\\3",text)
        text = transform_frac(text,"{","}")
        text = transform_frac(text,"(",")")
        for replace in replaceRule:
            text = text.replace(replace[0],replace[1])
        text = re.sub("\^(.)\^(.)\^(.)\^(.)", "^{\\1\\2\\3\\4}",text)
        text = re.sub("\^(.)\^(.)\^(.)", "^{\\1\\2\\3}",text)
        text = re.sub("\^(.)\^(.)", "^{\\1\\2}",text)
        text = re.sub("\_(.)\_(.)\_(.)", "_{\\1\\2\\3}",text)
        text = re.sub("\_(.)\_(.)", "_{\\1\\2}",text)
        newtexts += [text]
    question = newtexts[0]
    if len(newtexts)>1:
        question = newtexts[0]+"\n<ol class = 'small-question'>"
        for text in newtexts[1:]:
            question += "\n <li>"+text+"</li>"
        question += "\n</ol>"
    return question

import unicodedata

def join_diacritic(text, mode="NFC"):
    """
    基底文字と濁点・半濁点を結合
    """
    # str -> bytes
    bytes_text = text.encode()

    # 濁点Unicode結合文字置換
    bytes_text = re.sub(b"\xe3\x82\x9b", b'\xe3\x82\x99', bytes_text)
    bytes_text = re.sub(b"\xef\xbe\x9e", b'\xe3\x82\x99', bytes_text)

    # 半濁点Unicode結合文字置換
    bytes_text = re.sub(b"\xe3\x82\x9c", b'\xe3\x82\x9a', bytes_text)
    bytes_text = re.sub(b"\xef\xbe\x9f", b'\xe3\x82\x9a', bytes_text)

    # bytet -> str
    text = bytes_text.decode()

    # 正規化
    text = unicodedata.normalize(mode, text)

    return text

def transform_frac(sentence,startbr,endbr):
    depth = 0
    target = sentence
    for i,c in enumerate(target):
        if c == startbr:
            depth +=1
            if depth == 1:
                start = i
        elif c == endbr:
            depth -=1
            if depth == 0 and target[i+1]=="/":
                end = i
                child = target[start+1:end]
                text = target[end:]
                for j,d in enumerate(text):
                    if d == startbr:
                        depth +=1
                        if depth == 1:
                            start = j
                    elif d== endbr:
                        depth -=1
                    if depth == 0:
                        end = j
                mom = text[1:end]
                sentence =  target.replace(startbr+child+endbr+"/"+startbr+mom+endbr,"\\frac{"+child+"}{"+mom+"}")
                print(sentence)
                # break
    return sentence
    
    
def add_tags_to_video(videoObj):
    tags = []
    t = re.compile("#\S*")
    tags += t.findall(videoObj.data["snippet"]["title"])
    tags += t.findall(videoObj.data["snippet"]["description"])
    newtages = []
    for tag in tags:
        newtages += [tag.replace("#","")]
    tags = newtages
    tags += videoObj.data["snippet"]["tags"]
    for tag in tags:
        for t in Term.objects.all():
            if t.name == tag:
                print("Term: %s は既にあります" % tag)
                videoObj.terms.add(t)
                break;
        else:
            en_name = tr.translate(tag, dest="en").text
            slug = en_name.replace(" ","_")
            slug = en_name
            w = re.compile("\w|\d|_")
            slug = "".join(w.findall(slug))
            for t in Term.objects.all():
                if t.slug == slug:
                    print("Term: %s は既にあります" % tag)
                    break;
            else:
                print("Term: %s を追加します" % tag)
                # newTerm = Term.objects.create(
                #     name = tag,
                #     hurigana = conv.do(tag),
                #     en_name = en_name,
                #     slug = slug,
                # )
                # videoObj.terms.add(newTerm)
    videoObj.save()


def make_slug(name):
    en_name = tr.translate(name, dest="en").text
    en_name = en_name.replace(" ","_").replace("θ","theta")
    w = re.compile("\w|\d|_")
    slug = "".join(w.findall(en_name))
    # en_name.replace("$","").replace(" ","_").replace("'","").replace(",","").replace("/","").replace("∑","sigma").replace(" ","_").replace("`","").replace(")","").replace("(","").replace("+","").replace("\u200b","").replace("ⁿ","").replace("=","").replace(":","")
    return slug

def add_genre_from_playlisy(playlistObj):
    name = playlistObj.title
    s = re.compile("数学(\w*)\s")
    c = re.compile("\[(\w*)\]")
    subject = re.findall(s,name)
    chapter = re.findall(c,name)
    name = re.sub(s,"",name)
    name = re.sub(c,"",name)
    playlistObj.name = name
    if subject and chapter:
        subj = "".join(subject)
        sub = "数学%s" % subj
        genreObj = Genre.objects.filter(name = sub)[0]
        children = genreObj.children()
        while children:
            print(children)
            genres = Genre.objects.filter(name = None)
            for genre in children:
                if genre.name == name:
                    for video in playlistObj.videos.all():
                        print("%s：%s" % (video,genre))
                        video.genres.add(genre)
                        problems = Problem.objects.filter(slug = video.slug).first()
                        problems.genres.add(genre)
                        # video.save()
                    playlistObj.genres.add(genre)
                    continue
                if genre.children():
                    genres =  genres.union(genre.children())
            else:
                if genres:
                    children = genres
                else:
                    break


def update_genre_from_playlisy():
    playlists = Playlist.objects.all()
    for playlist in playlists:
        add_genre_from_playlisy(playlist)

# update_genre_from_playlisy()

### UPDATE

# download_video_data(get_uploads("UCtEVdDYltR4eWf-QXvjmCJQ"))
# print(Module.objects.all())

# downlaod_playlist_data("","UCtEVdDYltR4eWf-QXvjmCJQ")
# Video.objects.all().delete()
# Genre.objects.all().delete()

# videos = Video.objects.all()
# videos = Playlist.objects.get(slug = "PL_tGOJs7_tFQLFMm7I4V4dep7XGqk2fv3").videos.all()
# videos = Video.objects.filter(title__contains = "数学A ")
# Playlist.objects.filter(name=None).delete()
# term = Term.objects.get(slug = "Math_A")
# print(videos)
# for video in videos:
#     
    # print("%s：%s" % (problems.first(),video))
    # video.problems.add(problems.first())
    # video.genres.clear()
    # playlist.videos.remove(video)
    # video.terms.add(term)
    # term = Term.objects.get(slug = "number_of_cases")
    # video.terms.remove(term)
    # add_tags_to_video(video)
    # video.pub = video.data["snippet"]["publishedAt"]
    # video.save()

### 4stepの目次からgenreを読み込む

import pandas as pd
import openpyxl

def add_genre_from_excel(sub,url,sheet_num):
    subject = Genre.objects.create(
        name = "数学%s" % sub,
        slug = "Math_%s" % sub,
        # type = "SUB",
        parent = Genre.objects.filter(name = "高校数学")[0]
    )
    wb = openpyxl.load_workbook(url)
    ws = wb.worksheets[sheet_num]
    i=3
    while i<1000:
        cell = ws.cell(i,2)
        if not cell.value == None:
            name = cell.value.replace("　"," ")
            genre = Genre(
                name = name,
                slug = make_slug(name)
            )
            if re.match("第[０-９]章",name):
                parent = Genre.objects.filter(name = subject.name)
                genre.parent = parent[len(parent)-1]
                genre.type = "CHA"
            if re.match("第[０-９]節",name):
                parent = Genre.objects.filter(type = "CHA")
                genre.parent = parent[len(parent)-1]
                genre.type = "SEC"
            parent = Genre.objects.filter(type__in = ["CHA","SEC"])
            if re.match("[０-９]\s|1[0-9]\s",name):
                genre.parent = parent[len(parent)-1]
                genre.type = "SSE"
            if re.match("研究\s",name):
                genre.parent = parent[len(parent)-1]
                genre.type = "STU"
            if re.match("発展\s",name):
                genre.parent = parent[len(parent)-1]
                genre.type = "DEV"
            if re.match("補\s",name):
                genre.parent = parent[len(parent)-1]
                genre.type = "SUP"
            if re.search("演習問題",name):
                parent = Genre.objects.filter(type = "CHA")
                genre.parent = parent[len(parent)-1]
                genre.slug = "%s_%s" % (sub,genre.slug)
                genre.type = "PRA"
            if genre.parent:
                genre.save()
                print("%s：%s" % (genre.name, genre.parent.name))
        i += 1

def make_genre_name():
    genres = Genre.objects.all()
    for genre in genres:
        title = genre.name
        title = re.sub("\s(\w)\s(\w)$"," \\1\\2",title)
        title = re.sub("(^第[０-９]章\s)","",title)
        title = re.sub("(^第[0-9]章\s)","",title)
        title = re.sub("(^第[０-９]節\s)","",title)
        title = re.sub("(^[０-９]\s)","",title)
        title = re.sub("(^研究\s)","",title)
        title = re.sub("(^補\s)","",title)
        title = re.sub("(^発展\s)","",title)
        # print(title)
        genre.name = title
        genre.save()


def add_genre_from_excels():
    Genre.objects.all().delete()
    name = "高校数学"
    Genre.objects.create(
        name = name,
        slug = make_slug(name),
    )
    add_genre_from_excel("I",'ugosite/math_data/k4step_b1a.xlsx',0)
    add_genre_from_excel("A",'ugosite/math_data/k4step_b1a.xlsx',1)
    add_genre_from_excel("II",'ugosite/math_data/k4step_b2b.xlsx',0)
    add_genre_from_excel("B",'ugosite/math_data/k4step_b2b.xlsx',1)
    add_genre_from_excel("III",'ugosite/math_data/k4step_b3.xlsx',0)
    make_genre_name()
    update_genre_from_playlisy()

# add_genre_from_excels()

# 


def set_parent_of_genre():
    genres = Genre.objects.all()
    for genre in genres:
        if not genre.chapter:
            # genre.subject = None
            # genre.parent = Genre.objects.filter(name = "数学%s" % genre.subject)[0]
            genre.parent = Genre.objects.filter(name = "高校数学")[0]
            # print(genre.parent)
            # print(Genre.objects.filter(name = genre.subject))
            genre.save()



def update_problem_tex_from_video_description():
    problems = Problem.objects.all()
    # problems = Problem.objects.filter(slug="k1KD4_lwCs4")
    for problem in problems:
        video = problem.video
        description = video.description
        description = re.sub("\r\n","\n",description)
        description = re.sub("#\S*","",description)
        description = re.sub("問\n","問．",description)
        description = re.sub("問．\n","問．",description)
        description = re.sub("問\d\s","問．",description)
        description = description.replace("問 ","問．").replace("問　","問．").replace("問.","問．").replace("問：","問．").replace("． (","．(").replace(".(","．(").replace(". (","．(")
        # description = description+"\n"
        video.description = description
        video.save()
        questions = re.findall("(問．(?:.+\n)+)\n",description)
        print("questions %s" % questions)
        if questions:
            question = transform_question(questions[0])
            problem.text = question
        problem.save()

# update_problem_tex_from_video_description()

def update_video_name_from_title():
    videos = Video.objects.all()
    for video in videos:
        name = video.title.replace("空間のベクトル","空間ベクトル")
        name = name.replace("平面上のベクトル","平面ベクトル")
        name = name.replace("Ⅲ","III")
        name = re.sub("数学(\w*)\s","",name)
        name = re.sub("#\S*","",name)
        name = re.sub("【\w*】","",name)
        name = re.sub("＜\w*＞","",name)
        name = re.sub("\s.*?大","",name)
        name = name.replace(" "+video.playlist_set.all()[0].name,"")
        # print(name)
        video.name = name
        video.save()

def add_terms_to_video():
    videos = Video.objects.all()
    terms = Term.objects.all()
    for v in videos:
        for t in terms:
            if "2020夏" in v.description:
                v.description.replace("2020夏","夏")
                v.terms.remove(Term.objects.get(slug = 2020))
            # if t.name in v.description or t.name in v.title:
            #     v.terms.add(t)
        v.save()

# add_terms_to_video()


### 自分のTeXから問題を読み込む

# def transform_question_from_tex(text):

def add_problem_from_tex(module,article_name,path):
    Article.objects.filter(slug = make_slug(article_name)).delete()
    article = Article.objects.create(
        headline = article_name,
        slug = make_slug(article_name)
    )
    article.modules.add(module)

    genre = Genre.objects.get(slug = "Chapter_5_Differentiation")
    # print(genre)
    module.genres.add(genre)

    with open(path) as f:
        s = f.read()
        s = re.sub("\r\n","\n",s)
        questions = re.split("\n\\\\bqu",s)
        
    # print(len(answers))

    i=1
    for question in questions[1:]:
        text = question
        text = re.sub("<[0-9]>","",text)
        text = text.replace("<","&lt;").replace(">","&gt;")
        text = text.replace("\\bunsuu","\\displaystyle\\frac").replace("\\dlim","\\displaystyle\\lim").replace("\\dsum","\\displaystyle\\sum")
        text = text.replace("\\barr","\\left\{\\begin{array}{l}").replace("\\earr","\\end{array}\\right.")
        text = text.replace("\\NEN","\\class{arrow-pp}{}").replace("\\NEE","\\class{arrow-pm}{}").replace("\\SES","\\class{arrow-mm}{}").replace("\\SEE","\\class{arrow-mp}{}")
        text = text.replace("\\NE","&#x2197;").replace("\\SE","&#x2198;")
        text = text.replace("\\ifkaisetu \\vspace{-2zw}\\fi\\","")
        text = re.sub("%+[^\n]*\n","",text)
        text = text.replace("\\beda","<ol>").replace("\\eeda","</ol>").replace("\\benu","<ol>").replace("\\eenu","</ol>")
        text = text.replace("\n</ol>","</li>\n</ol>").replace("\n\\item","</li>\n<li>").replace("<ol></li>","<ol>").replace("<ol>","<ol class = 'small-question'>")
        text = text.replace("\\sqrt","\\sq").replace("\\sq","\\sqrt")
        text = re.sub("\$([\s\S]+?)\$"," $\\1$ ",text)
        text = text.replace("\\xlongrightarrow","\\xrightarrow")
        s = re.compile("\\\\hfill\((.*)\)")
        sources = re.findall(s,text)
        text = re.sub(s,"",text)
        text = text.replace(r"\hfill □","<p class = 'end'>□</p>")
        text = text.replace("\\iffigure","").replace("\\fi","")
        text = re.sub("\\\\vspace{.*?}","",text)
        text = text.replace("\\begin{mawarikomi}{}{","")
        text = text.replace("\n}\n","\n")
        text = text.replace("\\end{mawarikomi}","")
        # text = re.sub("\{\\\\bb(.*)\}","$\{\\bf\{\\1\}$",text)
        # text = re.sub("{\\\\bb","\\\\textbf{",text)
        for j in range(10):
            text = text.replace("\\MARU{%s}" % str(j),str("&#931%s;" % str(j+1)))
        answers = re.findall("\n\\\\begin{解答[\d]*}[^\n]*\n([\s\S]+?)\\\\end{解答[\d]*}",text)
        text = re.findall("(^[\s\S]*?)\\\\equ",text)[0]
        t = re.compile("{\\\\bb([^\n]*?)}.*\n")
        name = re.findall(t,text)
        if name:
            name = name[0]
        else:
            name = "%s %s" %(article_name,i)
            i += 1
        text = re.sub(t,"",text)
        text = text.replace("\\ ","~")
        text = text.replace("\\~","\\\\")
        text = re.sub(r"\\\s",r"\\\\ ",text)
        print("%s：%s" %(name,sources))
        problem = Problem.objects.create(
            name = name,
            slug = make_slug(name),
            text = text,
        )
        if sources:
            problem.source = sources[0]
            problem.save()
        if answers:
            problem.answer = answers[0]
            problem.save()
        problem.genres.add(genre)
        # article = Article.objects.create(
        #     headline = name,
        #     slug = make_slug(name),
        #     content = text,
        # )
        article.problems.add(problem)

# Module.objects.filter(slug = make_slug("数学III微分法の基本計算")).delete()

def add_problem_from_texs():
    module_name = "数学III の微分法の基本と演習"
    Module.objects.filter(slug = make_slug(module_name)).delete()
    module = Module.objects.create(
        name = module_name,
        slug = make_slug(module_name)
    )

    for problem in Problem.objects.all():
        if not Video.objects.filter(problems = problem):
            problem.delete()
    
    add_problem_from_tex(module,"数学III 微分法の基本計算","ugosite/math_data/8 数学III 微分法/210110-微分法の基本計算.tex")
    add_problem_from_tex(module,"数学III 極限と微分法 重要テーマ8","ugosite/math_data/8 数学III 微分法/210120-極限と微分法 重要テーマ8.tex")
    add_problem_from_tex(module,"数学III 微分演習","ugosite/math_data/8 数学III 微分法/210210-微分演習.tex")

# add_problem_from_tex("数学の考え方講座",



# add_problem_from_texs()

# Article.objects.all().delete()

### 過去問TeXを読み込む

import codecs

def update_kakomon():
    for module in Module.objects.filter(name__contains = "過去問"):
        for article in Article.objects.filter(modules = module):
            article.problems.all().delete()
            article.delete()
        module.delete()
    univ_problem_module = Module.objects.create(
        name = "大学別62年過去問題集",
        slug = "univ_problems",
        description = "このモジュールにはは旧帝7大学+東工大の62年分の過去問が含まれます。"
    )
    f_path = '/Users/greenman/Library/Mobile Documents/com~apple~CloudDocs/講師関係/2021 西京 17期3年/旧帝大過去問'
    i = 0
    for univ in sorted(os.listdir(f_path)):
        # univname = re.findall("([\w]+?)_",univ)
        if not univ.startswith('.'):
            univName = univ[3:].replace("hokudai","北大").replace("kyoto","京大").replace("tokyo","東大").replace("kyushu","九大").replace("nagoya","名大").replace("osaka","阪大").replace("titech","東工大").replace("tohoku","東北大")
            module = Module.objects.create(
                name = "%s 過去問62年" % univName,
                slug = univ[3:],
                type = "T"
            )
            module.parent_module=univ_problem_module
            module.save()
            for year in sorted(os.listdir("%s/%s" % (f_path,univ))):
                if not year.startswith('.'):
                    article = Article.objects.create(
                        title = "%s %s 問題セット" % (univName,year),
                        slug = "%s_%s" % (univ[3:],year)
                    )
                    article.modules.add(module)
                    for file in sorted(os.listdir('%s/%s/%s' % (f_path,univ,year))):
                        if file.endswith('.tex'):
                            # print(file)
                            with codecs.open('%s/%s/%s/%s' % (f_path,univ,year,file), 'r', encoding='shift_jis') as f:
                                inQuestion = False
                                question = ""
                                for line in f:
                                    line = line.strip()
                                    if inQuestion:
                                        if "\end{flushleft}" in line:
                                            inQuestion = False
                                        else:
                                            question = "%s%s\n" % (question,line)
                                    else:
                                        if "{\huge" in line:
                                            # num = re.findall("[\d]",line)[0]
                                            inQuestion = True
                                
                                question = question.replace("<","&lt;").replace(">","&gt;")
                                question = question.replace("\\begin{description}","<ol>").replace("\\end{description}","</ol>")
                                question = question.replace("\n</ol>","</li>\n</ol>").replace("\n\\item","</li>\n<li>").replace("<ol></li>","<ol>").replace("<ol>","<ol class = 'small-question'>")
                                question = question.replace("<li>[(＊)]","<li class ='unorder'>(*) ")
                                question = question.replace("\\hspace{1zw}","~")
                                question = question.replace('\\ding{"AC}',"&#9312;")
                                question = question.replace('\\ding{"AD}',"&#9313;")
                                question = question.replace('\\ding{"AE}',"&#9314;")
                                question = re.sub("<li>\[\([\d]\)\]","<li> ",question)
                                # question = re.sub("<li>\[\(([^\s]+)\)\]","<li class='unorder'> (\\1) ",question)
                                question = re.sub("<li>\[([^\s]+)\]","<li class='unorder'> \\1 ",question)
                                text = question
                                question = ""
                                isInMathMode = False
                                for c in text:
                                    if c=="$":
                                        if isInMathMode:
                                            question = question+"$ " 
                                            isInMathMode = False
                                        else:
                                            question = question+" $" 
                                            isInMathMode = True
                                    else:
                                        question = question+c
                                question = question.replace("$ ，","$，")
                                question = question.replace("\\\\","<br>")
                                print(question)
                                slug = "%s_%s" % (univ,file.replace(".tex",""))
                                yearNum =  re.findall("([^_]+)_",file)[0]
                                num =  re.findall("_(\w+).tex",file)[0]
                                if re.match("\d_\d",num):
                                    division = "文"
                                    num = num[2:]
                                else:
                                    division = "理"
                                problem = Problem.objects.create(
                                    name = "%s %s年度 %s系 第%s問" % (univName,yearNum,division,num),
                                    source = "%s %s年度 %s系 第%s問" % (univName,yearNum,division,num),
                                    slug = slug,
                                    text = question,
                                )
                                article.problems.add(problem)
                                i += 1
    # print(i)

    
# update_kakomon()



### Notesなど

from .models import Folder,Note


class NoteDetailView(generic.DetailView):
    def get_context_data(self, **kwargs):
        context = super(NoteDetailView,self).get_context_data(**kwargs)
        note = context["note"]
        folder = note.folders.all()[0]
        context["folder"] = folder
        notes = Note.objects.filter(folders = folder) 
        index = list(notes).index(note)
        if not len(notes) == index+1:
            context['next'] = notes[index+1].get_absolute_url()
        if not index-1<0:
            context['prev'] = notes[index-1].get_absolute_url()
        context['up'] = folder.get_absolute_url()
        context['ancestors'] = note.ancestors()
        context['self'] = note
        return context
    model = Note

class NoteListView(generic.ListView):
    model = Note
    def get_context_data(self, **kwargs):
        context = super(NoteListView,self).get_context_data(**kwargs)
        context["folder_list"] = Folder.objects.filter(folders__isnull = True)
        return context

class FolderDetailView(generic.DetailView):
    model = Folder
    def get_context_data(self, **kwargs):
        context = super(FolderDetailView,self).get_context_data(**kwargs)
        folder = context["folder"]
        if folder.folders.first():
            up = folder.folders.first()
            folders = Folder.objects.filter(folders = up) 
            index = list(folders).index(folder)
            if not len(folders)==index+1:
                context['next'] = folders[index+1].get_absolute_url()
            if not index-1<0:
                context['prev'] = folders[index-1].get_absolute_url()
            context['up'] = up.get_absolute_url()
        context['ancestors'] = folder.ancestors()
        context['self'] = folder
        return context

class FolderListView(generic.ListView):
    model = Folder
    
    paginate_by = 100

def profileView(request):
    return render(request, "profile.html")

import pathlib
import datetime

def add_folder(folder):
    for fileName in os.listdir(folder.path):
        if not fileName.startswith('.') and not "attachments" in fileName:
            if fileName.endswith(".html"):
                path = "%s/%s" % (folder.path,fileName)
                p = pathlib.Path(path)
                update_date = datetime.datetime.fromtimestamp(p.stat().st_ctime)
                created_date = datetime.datetime.fromtimestamp(p.stat().st_mtime)
                # print(update_date,created_date)
                note = Note.objects.create(
                    name = fileName,
                    title = fileName.replace(".html",""),
                    path = path,
                    created_date = created_date,
                    update_date = update_date,
                )
                note.folders.add(folder)
                with open(note.path) as f:
                    note.text = f.read()
                    note.save()
            else:
                newfolder = Folder.objects.create(
                    name = fileName,
                    path = "%s/%s" % (folder.path,fileName),
                )
                newfolder.folders.add(folder)
                add_folder(newfolder)
    return folder

def update_notes():
    Folder.objects.all().delete()
    Note.objects.all().delete()
    main_path = '/Users/greenman/Desktop/web-projects/django_projects/ugosuu/media_local/Notes'
    for fileName in os.listdir(main_path):
        print(fileName)
        if fileName in ["開発ログ","2022 徒然メモ"]:
            newfolder = Folder.objects.create(
                name = fileName,
                path = "%s/%s" % (main_path,fileName),
            )
            add_folder(newfolder)

# update_notes()


### いろいろなところからModule,Articleをを読み込む ###

# print(vars(Folder.objects.filter(name="Notes")[0]))
PLAYLIST_TYPE_CHOICES = [
    ['C', '単元別'],
    ['T', 'テーマ別'],
    ['O', 'その他'],
]

def add_article_form_playlist():
    for type in PLAYLIST_TYPE_CHOICES:
        print(type)
        module = Module.objects.filter(name = type[1])
        Article.objects.filter(modules = module[0]).delete()
        module.delete()
        Module.objects.create(
            name = type[1],
            slug = type[0],
            type = type[0],
            description = "このモジュールは、Youtubeから読み込んだデータをもとに%sの記事が含まれます" % type[1]
        )
    
    for playlist in Playlist.objects.all():
        module = Module.objects.get(type = playlist.type)
        article = Article.objects.create(
            headline = playlist.name,
            slug = playlist.slug,
            description = playlist.description,
        )
        for video in playlist.videos.all():
            article.problems.add(video.problems.first())
        article.modules.add(module)

# add_article_form_playlist()

def add_module_from_genre(genre):
    # for genre in Genre.objects.all():
    print("title:%s" % genre.name)
    print("slug:%s" % genre.slug)
    print("type:%s" % genre.type)
    if genre.parent_genre:
        print("parent_genre:%s" % genre.parent_genre.name)
    problems = Problem.objects.filter(genres = genre)
    if problems:
        article = Article.objects.create(
            title = genre.name,
            slug = genre.slug,
            description = "これは%sタイプのgenreから自動生成されたのArticleです。" % genre.type,
        )
        module = Module.objects.get(slug = genre.parent_genre.slug)
        article.modules.add(module)
        for problem in problems:
            article.problems.add(problem)
    module = Module.objects.create(
        name = genre.name,
        slug = genre.slug,
        description = "これは%sタイプのgenreから自動生成されたのmoduleです。" % genre.type,
        type = "C",
    )
    if genre.parent_genre:
        parent_module = Module.objects.get(slug = genre.parent_genre.slug)
        module.parent_module = parent_module
        module.save()

    if genre.children():
        for child in genre.children():
            add_module_from_genre(child)
    # print()


# print(koukousuugaku)

def add_module_from_genre_all():
    Module.objects.filter(description__contains = "genreから自動生成された").delete()
    Article.objects.filter(description__contains = "genreから自動生成された").delete()
    koukousuugaku = Genre.objects.get(name="高校数学")
    add_module_from_genre(koukousuugaku)

# add_module_from_genre_all()

def clear_module():
    module = Module.objects.get(name = "単元別")
    print(module)
    Article.objects.filter(modules = module).delete()
    module.delete()

# clear_module()