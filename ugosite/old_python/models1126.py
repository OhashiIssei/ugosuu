from email.policy import default
import enum
from operator import contains
from tokenize import String
from django.db import models

from datetime import date
from django.urls import reverse #Used to generate URLs by reversing the URL patterns
from django.contrib.auth.models import User #Blog author or commenter


from django.utils import timezone
from django.contrib import admin


from django.db import models
from django_mysql.models import ListCharField

# import uuid # Required for unique comment instances

from urllib.parse import quote

import unicodedata
import sys,os

import codecs
import openpyxl

import pathlib
import datetime

import codecs
import re

from pykakasi import kakasi
kakasi = kakasi()
kakasi.setMode('J', 'H') 
conv = kakasi.getConverter()

import httplib2

from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRETS_FILE = 'client_secret.json'

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
SCOPES = ["https://www.googleapis.com/auth/youtube"]
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

import pickle
from google.auth.transport.requests import Request

def get_authenticated_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=creds)

# if __name__ == "__main__":
# youtube = get_authenticated_service()
youtube = build('youtube', 'v3', developerKey='AIzaSyD-ohN5V0dlXYHjP7lSrUgKcCgXDkjpR14')

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


class Term(models.Model):
    """用語を表すモデル"""
    name = models.CharField(max_length=200, help_text='用語名を入力してください')
    hurigana = models.CharField(max_length=200, default="ふりがな" , help_text='ふりがなを入力してください')
    en_name = models.CharField(max_length=200, blank=True, help_text='英語名を入力してください')
    description = models.TextField(max_length=1000, blank=True, help_text='この用語の説明を入力してください')
    related_terms = models.ManyToManyField("Term",help_text='この用語に関連する用語を選んでください')

    class Meta:
        ordering = ['hurigana']

    def get_absolute_url(self):
        return reverse('term-detail', args=[self.id])
    
    def __str__(self):
        return self.name
    
ARTICLE_TYPE_CHOICES = [
    ('BAS', '基本'), 
    ('STU', '研究'), 
    ('DEV', '発展'), 
    ('SUP', '補足'), 
    ('PRA', '演習'), 
    ('TER', 'テーマ'), 
    ('CAT', 'カテゴリ'), 
    ('NOT', 'ノート'), 
    ('OTH', 'その他'), 
]

import re

class MyFile(models.Model):
    name = models.CharField(max_length=200, help_text='記事のタイトルを入力してください')
    title = models.CharField(max_length=200, blank=True, help_text='記事のタイトルを入力してください')
    path = models.CharField(max_length=200,default="/" ,blank=True, help_text='このカテゴリのpathを入力してください')
    created_date = models.DateTimeField(default=timezone.now, blank=True, help_text='このカテゴリの作成日を指定してください')
    update_date = models.DateTimeField(default=timezone.now, blank=True, help_text='このカテゴリの更新日を指定してください')
    playlistId = models.SlugField(max_length=100, null=True, blank=True, help_text='このカテゴリのYoutubeIDを入力してください')
    data = models.JSONField(null=True, help_text='このFieldはYoutubeAPIによって読み込まれます。')

    def update_excelfiles(self):
        """
        数研出版の4stepの目次EXCELからカテゴリデータを取得する
        """
        datas = [
            ["I","k4step_b1a.xlsx"],
            ["A",'k4step_b1a.xlsx'],
            ["II",'k4step_b2b.xlsx'],
            ["B",'k4step_b2b.xlsx'],
            ["III",'k4step_b3.xlsx']
        ]
        for data in datas:
            category = Category.objects.create(
                name = "数学%s" % data[0],
                title = "数学%s" % data[0],
                type = "SUB",
                parent = self,
                path = '%s/%s' % (self.path,data[1])
            )
            print("new Category: %s (parent: %s)" % (category, category.parent))
            wb = openpyxl.load_workbook(category.path)
            shieet_num = 0 if category.name[-1]=="I" else 1
            ws = wb.worksheets[shieet_num]
            for i in range(1000):
                if i <3 : continue
                cell = ws.cell(i,2)
                if not cell.value : continue
                title = cell.value.replace("　"," ")
                sub_category = Category().make_from_title(title)
                if sub_category.type in ["CHA","SEC"]:
                    sub_category.save()
                    print("new Category: %s (parent: %s)" % (sub_category, sub_category.parent))
                    continue
                Article(
                    name = sub_category.name
                ).make_from_title(title)

    def update_icons(self):
        for fileName in os.listdir(self.path):
            if not ".svg" in fileName:continue
            svgPath = "%s/%s" % (self.path,fileName)
            name = fileName.replace(".svg","")
            name = join_diacritic(name)
            categorys = Category.objects.filter(name=name)
            for category in categorys:
                if not category.type in ["CHA","SEC"]:continue
                with open(svgPath) as f:
                    svg = f.read()
                svg = re.findall("<svg[\s\S]*",svg)[0]
                svg = re.sub("<svg","<svg class='icon'",svg)
                svg = re.sub("stroke=.........\s","stroke='inherit' ",svg)
                category.icon = svg
                category.save()
                print("Category: %sにiconを設定しました" % category)

    def update_youtube(self,pagetoken):
        print("チャンネル %s のplaylist_dataをdownlaodします" % self.playlistId)
        playlists = youtube.playlists().list(
            channelId = self.playlistId,
            part='snippet',
            maxResults = 100,
            pageToken=pagetoken
        ).execute()
        for playlist in playlists["items"]:
            Article(parent=self).make_from_data(playlist)
        return
        # try:
        #     nextPagetoken = playlists["nextPageToken"] 
        #     # print(nextPagetoken)
        #     self.update_youtube(nextPagetoken)
        # except:
        #     return


    def update_my_folder(self):
        for fileName in os.listdir(self.path):
            if fileName.startswith('.'): continue
            if "阪大" in fileName: continue
            if "旧帝大" in fileName: continue
            file_path = "%s/%s" % (self.path,fileName)
            if os.path.isdir(file_path):
                child_category = Category.objects.create(
                    name = fileName,
                    parent = self,
                    path = file_path,
                )
                child_category.update_my_folder()
                continue
            if fileName.endswith(".tex"):
                Article(parent = self).make_from_my_texfile(file_path)
    
    def update_kakomon_folder(self):
        for univ in sorted(os.listdir(self.path)):
            if univ.startswith('.'): continue
            name = univ[3:]
            replaceRule = [["hokudai","北大"],["kyoto","京大"],["tokyo","東大"],["kyushu","九大"],["nagoya","名大"],["osaka","阪大"],["titech","東工大"],["tohoku","東北大"]]
            for r in replaceRule:
                name = name.replace(r[0],r[1])
            category = Category.objects.create(
                name = name,
                type = "TER",
                parent = self,
                path = "%s/%s" % (self.path,univ)
            )
            print("new Category: %s (parent: %s)" % (category,category.parent))
            for year in sorted(os.listdir(category.path)):
                if year.startswith('.'):continue
                path = "%s/%s" % (category.path,year)
                Article(parent = category).make_from_kakomon_folder(path)

    def update_note(self):
        for name in os.listdir(self.path):
            if name.startswith('.'):continue
            if "attachments" in name:continue
            p = pathlib.Path(self.path)
            filePath = "%s/%s" % (self.path,name)
            if os.path.isdir(filePath):
                category = Category.objects.create(
                    name = name,
                    type = "OTH",
                    created_date = datetime.datetime.fromtimestamp(p.stat().st_ctime),
                    update_date = datetime.datetime.fromtimestamp(p.stat().st_mtime),
                    parent = self,
                    path = filePath
                )
                category.update_note()
                continue
            with open(filePath) as f:
                content = f.read()
            Article.objects.create(
                name = name.replace(".html",""),
                title = name,
                type = "NOT",
                created_date = datetime.datetime.fromtimestamp(p.stat().st_ctime),
                update_date = datetime.datetime.fromtimestamp(p.stat().st_mtime),
                parent = self,
                content = content
            )

    

    def __str__(self):
        return self.name

class Article(MyFile):
    """記事を表すモデル"""
    description = models.TextField(max_length=1000, blank=True, help_text='記事の説明を入力してください')
    content = models.TextField(max_length=2000, blank=True, help_text='記事の内容をHTML形式で入力してください')
    type =  models.CharField(max_length=200, default = "OTH", choices = ARTICLE_TYPE_CHOICES, help_text='このカテゴリの種類を選択してください')
    parent = models.ForeignKey('Category', on_delete = models.CASCADE, help_text='この記事の親カテゴリ選んでください')
    # related_terms = models.ManyToManyField(Term, help_text='この記事に関連する用語を選んでください')

    class Meta:
        ordering = ['created_date']

    def get_absolute_url(self):
        return reverse('article-detail', args=[str(self.id)])

    def __str__(self):
        return self.name
    
    def make_youtube_url(self):
        return "https://youtube.com/playlist?list=%s" % self.playlistId
    
    def make_video_list(self):
        videolist = []
        for problem in self.problem_set.all():
            for video in problem.video_set.all():
                videolist.append(video)
        return videolist
    
    def make_from_title(self,title:str):
        self.title = title
        def type(title):
            if re.match("[０-９]\s|1[0-9]\s",title): return "BAS"
            if re.match("研究\s",title): return "STU"
            if re.match("発展\s",title): return  "DEV"
            if re.match("補\s",title): return "SUP"
            if re.search("演習問題",title) : return "PRA"
        self.type = type(self.title)
        if not self.type:
            return self
        if self.type == "PRA":
            self.parent = Category.objects.filter(type = "CHA").last()
        else:
            self.parent = Category.objects.filter(type__in = ["CHA","SEC"]).last()
        self.save()
        print("new Article: %s (parent: %s)" % (self, self.parent))
        return self
    
    def make_from_data(self,data):
        self.data = data
        self.playlistId = data["id"]
        name = data["snippet"]["title"].replace("Ⅲ","III")
        name = re.sub("数学(\w*)\s","",name)
        name = re.sub("\[(\w*)\]","",name)
        name = join_diacritic(name)
        name = name.replace("三角比（図形と計量）","図形の計量").replace("空間 ","空間の").replace("平面ベクトル","平面上のベクトル")
        name = re.sub("^整数$","整数の性質",name)
        self.name = self.title = name
        self.description = data["snippet"]["description"]
        if Category.objects.filter(name=name):
            self.type = "CAT"
            self.parent = Category.objects.filter(name=name).first()
        elif re.search("【.*】",name):
            self.name = re.sub("【.*】","",name)
            self.type ="TER"
            self.parent = Category.objects.get(name = "テーマ別記事")
        else:
            self.parent = Category.objects.get(name = "高校数学")
        self.save()
        print("new Article: %s (parent: %s)" % (self,self.parent))
        print("プレイリスト %s のvideoをdownlaodします" % self.playlistId )
        playlistItems = youtube.playlistItems().list(
            playlistId = self.playlistId,
            part='snippet',
            maxResults = 100
        ).execute()
        self.data = playlistItems
        self.save()
        for playlistItem in playlistItems['items']:
            videoId = playlistItem["snippet"]['resourceId']["videoId"]
            oldVideo = Video.objects.filter(videoId = videoId)
            if oldVideo: 
                video = oldVideo[0]
                video.problem.articles.add(self)
                continue
            res = youtube.videos().list(
                id = videoId,
                part='snippet',
                maxResults = 100
            ).execute()
            data = res["items"][0]
            video = Video().make_from_data(data)
            problem = Problem().make_from_video(video)
            problem.articles.add(self)
            video.make_terms_from_data(data)
        return self
        
    
    def make_from_my_texfile(self,path:str):
        self.name = os.path.basename(path).replace(".tex","")
        self.path = path
        with open(path) as f:
            file_text = f.read()
        file_text = re.sub("\r\n","\n",file_text)
        s = re.search("\\\\begin{document}(.*\n)*\\\\end{document}",file_text)
        if not s: return self##これがなければ話にならない
        file_text = s.group().replace("\\sub{","\\subsection{")
        subsections = re.split("\n\\\\subsection",file_text)
        if len(subsections)<3:##subが1つ以下のときは
            self.save()
            questions = re.findall("\n\\\\bqu((?:.*\n)*?)\\\\equ",file_text)
            if not questions: return
            print("new Article: %s (parent: %s)" % (self,self.parent))
            for text in questions:
                problem = Problem().make_from_my_tex(text)
                problem.articles.add(self)
            return self
        child_category = Category.objects.create(
            name = self.name,
            parent = self.parent,
            path = path,
        )
        for sub in subsections[1:]:
            n = re.findall("^{\\\\bb\s(.*)}",sub)
            if n:
                name = n[0]
            else:
                name = "%s %s" % (child_category.name,len(child_category.children())+1)
            sub_article = Article.objects.create(
                name = name,
                parent = child_category,
            )
            print("new Article: %s (parent: %s)" % (sub_article,sub_article.parent))
            questions = re.findall("\n\\\\bqu((?:.*\n)*?)\\\\equ",sub)
            for text in questions:
                problem = Problem().make_from_my_tex(text)
                problem.articles.add(sub_article)

    def make_from_kakomon_folder(self,path):
        self.name = "%s %s" % (self.parent.name,os.path.basename(path))
        self.type = "TER"
        self.path = path
        self.save()
        for file in sorted(os.listdir(path)):
            if not file.endswith('.tex'):continue
            problem = Problem().make_from_kakomon_texfile("%s/%s" % (path,file))
            problem.articles.add(self)
        print("new Article: %s (parent: %s)" % (self,self.parent))

            # if not problem.text_for_video:
            #         print(problem)

        # for problem in self.problem_set.all():
        #     if not problem.text_for_video:
        #         print(problem)
        #         print(problem.text)
            # for video in problem.video_set.all():
            #     data = video.data
                # print(data)

CATEGORY_TYPE_CHOICES = [
    ('SUB', '科目'), 
    ('CHA', '章'), 
    ('SEC', '節'), 
    ('SSE', '分節'), 
    ('TER', 'テーマ'), 
    ('OTH', 'その他'), 
]


class Category(MyFile):
    """カテゴリを表すモデル"""
    description = models.TextField(max_length=10000, blank=True, help_text='このカテゴリの説明を入力してください')
    type =  models.CharField(max_length=200, default="OTH", choices=CATEGORY_TYPE_CHOICES,help_text='このカテゴリの種類を選択してください')
    icon = models.CharField(max_length=10000,  blank=True, help_text='このカテゴリのアイコンSVG')
    parent = models.ForeignKey('Category', on_delete = models.CASCADE, null=True,help_text='この記事の親カテゴリ選んでください')

    class Meta:
        ordering = ['created_date']

    def get_absolute_url(self):
        return reverse('category-detail', args=[str(self.id)])

    def __str__(self):
        return self.name
    
    def children(self):
        children = list(Article.objects.filter(parent = self))
        children.extend(list(Category.objects.filter(parent = self)))
        return children

    def ancestors(self):##先祖(自分含まない)
        module = Category.objects.get(id = self.id)
        ancestors = []
        while module.parent:
            ancestors.insert(0, module.parent)
            module = module.parent
        return ancestors
    
    def make_from_title(self,title:str):
        self.title = title
        if re.match("第[０-９]章",title):
            self.parent = Category.objects.filter(type = "SUB").last()
            self.type = "CHA"
        if re.match("第[０-９]節",title):
            self.parent = Category.objects.filter(type = "CHA").last()
            self.type = "SEC"
        name = title
        name = re.sub("\s(\w)\s(\w)$"," \\1\\2",name)
        name = re.sub("(^第[０-９]章\s)","",name)
        name = re.sub("(^第[0-9]章\s)","",name)
        name = re.sub("(^第[０-９]節\s)","",name)
        # name = re.sub("(^[０-９]\s)","",name)
        # name = re.sub("(^研究\s)","",name)
        # name = re.sub("(^補\s)","",name)
        # name = re.sub("(^発展\s)","",name)
        self.name = name
        return self
            
LEVEL_CHOICES = [
    ('BASIC', '基礎レベル'), 
    ('ADVANCED', '発展レベル'), 
    ('EXAM', '大学入試問題'), 
    ('MANIA', 'マニア向け'), 
]

class Source(models.Model):
    name = models.CharField(max_length=200, help_text='引用名を入力してください')
    univ = models.CharField(max_length=200,  blank=True)
    division = models.CharField(max_length=200, blank=True)
    pub_date = models.DateField(default = timezone.now)
    def __str__(self):
        return self.name
    
    def make_from_name(self,name):
        self.name = name
        name = name.replace("(","").replace(")","")
        self.name = name
        self.save()
        return self

class TeX:
    def __str__(self):
        return self.text

    def __init__(self,text:str):
        self.text = text

    def itemize_to_ol(self):
        text = self.text
        text = re.sub("\\\\beda<[0-9]>","<ol>",text)
        text = text.replace("\\beda","<ol>").replace("\\eeda","</ol>")
        text = text.replace("\\benu","<ol>").replace("\\eenu","</ol>")
        text = text.replace("\\begin{itemize}","<ol>").replace("\\end{itemize}","</ol>")
        text = text.replace("\\begin{enumerate}","<ol>").replace("\\end{enumerate}","</ol>")
        text = text.replace("\\begin{description}","<ol>").replace("\\end{description}","</ol>")
        text = text.replace("<ol>","<ol class = 'small-question'>")
        if not len(re.findall("<ol.*>",text))==len(re.findall("</ol>",text)):
            print("olの数が一致しません\n%s" % text)
            sys.exit()
        self.text = text
        return self.text
    
    def item_to_li(self):
        text = self.text
        if not re.search("\\\\item",text):
            return text
        lines = text.split("\n")
        for i,line in enumerate(lines):
            # print(line)
            if re.match("\\\\item",line):
                line = re.sub("\\\\item","",line)
                lines[i] = "<li>%s</li>" % line
        print(lines)
        text = "\n".join(lines)
        text = text.replace("<li>[(＊)]","<li class ='unorder'>(*) ")
        text = re.sub("<li>\[\([\d]\)\]","<li> ",text)
        text = re.sub("<li>\[([^\s]+)\]","<li class='unorder'> \\1 ",text)
        if not len(re.findall("<li.*>",text))==len(re.findall("</li>",text)):
            print("liの数が一致しません\n%s" % text)
            sys.exit()
        self.text = text
        return self.text
    
    def videos_title_to_name(self):
        name = self.text
        name = join_diacritic(name)
        name = re.sub("(#\S+)","",name)
        name = re.sub("(【\S+】)","",name)
        name = name.replace("Ⅲ","III")
        name = re.sub("数学(\w*)\s","",name)
        name = re.sub("#\S*","",name)
        name = re.sub("【\w*】","",name)
        name = re.sub("＜\w*＞","",name)
        name = re.sub("\s.*?大","",name)
        self.text = name
        return self.text
    
    def transform_frac(self):
        text = self.text
        f = re.search("/",text)
        if not f: return self
        # print(self.text)
        if text[f.start()-1] == "}" or text[f.end()+1] == "{":
            print(text)
            ireko = Ireko(text=text,startbr="{",endbr="}")
        else:
            ireko = Ireko(text=text,startbr="(",endbr=")")
        mom = ireko.read_mom()
        child = ireko.read_child()
        frac = "\\frac{%s}{%s}" % (child,mom)
        print(frac)
        # if not re.search("%s/%s" % (child,mom),text):
        #     print(text)
        #     print("%s/%s" % (child,mom))
        #     sys.exit()
        self.text = text.replace("%s/%s" % (child,mom),frac)
        print("transform_frac を適用します")
        return self.transform_frac()
    
    def transform_sqrt(self):
        text = self.text
        self.text = text.replace("√","\\sqrt")
        s = re.search("\\\\sqrt",text)
        if not s: return self
        print(self.text)
        if text[s.end()+1] == "{":
            ireko = Ireko(text=text,startbr="{",endbr="}")
        else:
            ireko = Ireko(text=text,startbr="(",endbr=")")
        ireko.text = ireko.text[s.end()+1:]
        inv = ireko.read_one_invariant()
        sqrt = "\\sqrt{%s}" % inv
        print(sqrt)
        self.text = self.text.replace("\\sqrt%s" % inv,sqrt)
        transformed = self.transform_sqrt()
        superNum = ["⁰","¹","²","³","⁴","⁵","⁶","⁷","⁸","⁹"]
        for i,n in enumerate(superNum):
            transformed.text = text.replace("%s\\sqrt" % n,"\\sqrt[%s]" % i)
        return transformed
    
    def text_to_tex(self):
        text = self.text
        replaceRule = []
        replaceRule += [["＜","&lt;"],["＞","&gt;"]]
        replaceRule += [["・","\cdot"],["…","\cdots"]]
        superNum = ["⁰","¹","²","³","⁴","⁵","⁶","⁷","⁸","⁹"]
        subNum = ["₀","₁","₂","₃","₄","₅","₆","₇","₈","₉"]
        for i,n in enumerate(superNum):
            replaceRule += [[n,"^%s" % i]]
        for i,n in enumerate(subNum):
            replaceRule += [[n,"_%s" % i]]
        replaceRule += [["ⁿ","^n"],["⁻","^-"],["⁺","^+"],["ₓ","_x"],["ₐ","_a"]]
        replaceRule += [["≦","\\leqq "],["≧","\\geqq "],["≠","\\neq "],["→","\\to "]]
        replaceRule += [["\\frac","\\displaystyle\\frac"],["\\vec","\\overrightarrow"]]
        replaceRule += [["π","\\pi "],["α","\\alpha "],["β","\\beta "],["γ","\\gamma"],["θ","\\theta "]]
        replaceRule += [["∠","\\angle "],["△","\\triangle "],["◦","^\\circ "],["°","^\\circ "]]
        replaceRule += [["log","\\log "],["sin","\\sin "],["cos","\\cos "],["tan","\\tan "]]
        replaceRule += [["lim","\\displaystyle\\lim"],["∫","\\displaystyle\\int"],["∑","\\displaystyle\\sum"],["Σ","\\displaystyle\\sum"]]
        replaceRule += [["nCr","_n\\text{C}_r"]]
        text = text.replace("　","").replace(" ","")
        text = text.replace("\r","")
        text = text.replace("\n\n","\n")
        texts = re.split("\n\([\d\w]\)|問．\([\d\w]\)",text)
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
            # print(type(text))
            text = TeX(text).transform_frac().text
            text = TeX(text).transform_sqrt().text
            for r in replaceRule:
                text = text.replace(r[0],r[1])
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
                question += "\n <li>%s</li>" % text
            question += "\n</ol>"
        self.text = question
        return self.text

class Problem(models.Model):
    """問題を表すモデル"""
    name = models.CharField(max_length=200, help_text='問題名を入力してください')
    text = models.TextField(max_length=1000, help_text='この問題の内容をTeX形式で入力してください')
    articles = models.ManyToManyField(Article, help_text='この問題が含まれる記事を選んでください')
    source = models.ForeignKey(Source, on_delete = models.CASCADE,null=True, help_text='この問題のソースを選んでください')
    answer = models.TextField('example_answer', max_length=10000, null=True, blank=True, help_text='この問題の解答例をTeX形式で入力してください')

    def get_admin_url(self):
        return "http://127.0.0.1:8000/admin/ugosite/problem/%s/" % self.id
    
    def get_absolute_url(self):
        return reverse('problem-detail', args=[str(self.id)])

    def __str__(self):
        return self.name
    
    def make_from_video(self,video):
        Problem.objects.filter(name = video.name).delete()
        video.problem = self
        self.name = video.name
        self.title = video.title
        question = video.question
        s = re.search("\(.{,10}大.*\)",question)
        if s:
            self.source = Source().make_from_name(s.group())
            question = question.replace(s.group(),"")
        self.text = TeX(question).text_to_tex()
        if not self.text:
            self.save()
            video.save()
            return self
        oldProblems = Problem.objects.filter(text = self.text)
        if not oldProblems:
            print("new Problem: %s" % self)
            self.save()
            video.save()
            return self
        p = oldProblems[0]
        m = min(len(p.name),len(self.name))
        print("%s:%s %s" % (p.name,self.name,m))
        for i in range(0,m-1,1):
            # print(i)
            if p.name[i] == self.name[i]:continue
            p.name = p.name[:i].replace(" (","").replace("(","").replace(" （","").replace("（","")
            break
        p.save()
        video.problem = p
        video.save()
        return p
    
    def make_from_my_tex(self,text:str):
        self.text = text
        replaceRule = []
        replaceRule += [["<","&lt;"],[">","&gt;"],["\\bunsuu","\\displaystyle\\frac"],["\\dlim","\\displaystyle\\lim"],["\\dsum","\\displaystyle\\sum"]]
        replaceRule += [["\\vv","\\overrightarrow"],["\\bekutoru","\\overrightarrow"],["\\doo","^{\\circ}"],["\\C","^{\\text{C}}","\\sq{","\\sqrt{"]]
        replaceRule += [["\\barr","\\left\{\\begin{array}{l}"],["\\earr","\\end{array}\\right."]]
        replaceRule += [["\\PP","^{\\texc{P}}"],["\\QQ","^{\\texc{Q}}"],["\\RR","^{\\texc{R}}"]]
        replaceRule += [["\\NEN","\\class{arrow-pp}{}"],["\\NEE","\\class{arrow-pm}{}"],["\\SES","\\class{arrow-mm}{}"],["\\SEE","\\class{arrow-mp}{}"]]
        replaceRule += [["\\NE","&#x2197;"],["\\SE","&#x2198;"],["\\xlongrightarrow","\\xrightarrow"]]
        replaceRule += [["\\hfill □","<p class = 'end'>□</p>"]]
        replaceRule += [["\\bf\\boldmath", "\\bb"],["\n}\n","\n"],["\\bf", "\\bb"]]
        for r in replaceRule:
            text = text.replace(r[0],r[1])
        text = transform_dint(text,"{","}")
        text = re.sub("%+[^\n]*\n","\n",text)
        text = text.replace("\r","")
        text = TeX(text).itemize_to_ol()
        text = TeX(text).item_to_li()
        text = re.sub("\$([\s\S]+?)\$"," $\\1$ ",text)
        s = re.compile("\\\\hfill\((.*)\)")
        sources = re.findall(s,text)
        text = re.sub(s,"",text)
        text = re.sub("\\\\vspace{.*?}","",text)
        for l in ["\\newpage","\\iffigure","\\fi","\\ifkaisetu","\\begin{mawarikomi}{}{","\\end{mawarikomi}","\\vfill","\\hfill","\\Large"]:
            text = text.replace(l,"")

        for j in range(10):
            text = text.replace("\\MARU{%s}" % str(j),str("&#931%s;" % str(j+1)))
        answers = re.findall("\n\\\\begin{解答[\d]*}[^\n]*\n([\s\S]+?)\\\\end{解答[\d]*}",text)
        n = re.findall("^\s*{\\\\bb\s*(.+)}.*\n",text)
        if n:
            self.name = n[0]
        text = re.sub("^\s*{\\\\bb\s*(.+)}.*\n","",text)
        text = text.replace("\\ ","~")
        text = text.replace("\\~","\\\\")
        text = re.sub(r"\\\s",r"\\\\ ",text)
        if sources:
            self.source = Source().make_from_name(sources[0])
        if answers:
            self.answer = answers[0]
        self.text = text
        self.save()
        print("new Problem: %s" % self)
        return self

    def make_from_kakomon_texfile(self,path:str):
        with codecs.open(path, 'r', encoding='shift_jis') as f:
            text = f.read()
        t = re.findall("{\\\\huge\s\d.*}\r\n([\s\S]*?)\\\\end{flushleft}",text)
        if not t:
            print(text)
            sys.exit()
        atricleName = Article.objects.get(path=os.path.dirname(path)).name
        num =  re.findall("_(\w+).tex",os.path.basename(path))[0]
        if re.match("\d_\d",num):
            division = "文"
            num = num[2:]
        else:
            division = "理"
        self.name = "%s %s系 第%s問" % (atricleName,division,num)
        self.source = Source().make_from_name(self.name)
        text = t[0]
        text = text.replace("<","&lt;").replace(">","&gt;")
        text = text.replace("\r","")
        text = TeX(text).itemize_to_ol()
        text = TeX(text).item_to_li()
        print(text)
        text = re.sub("\\\\hspace{\dzw}","",text)
        text = text.replace("\\hspace{1zw}","~").replace('\\ding{"AC}',"&#9312;").replace('\\ding{"AD}',"&#9313;").replace('\\ding{"AE}',"&#9314;")
        text = re.sub("\$([\s\S]+?)\$"," $\\1$ ",text)
        text = text.replace("$ ，","$，")
        text = text.replace("\\\\","<br>")
        self.text = text
        self.save()
        print("new Problem: %s" % self)
        return self

class Ireko:
    depth = 0
    start = 0
    parent = None
    
    def __init__(self,text,startbr,endbr):
        self.text = text
        self.startbr = startbr
        self.endbr = endbr

    def __str__(self):
        return self.text

    def new_child(self,text,start:int):
        child = Ireko(
            text = text,
            startbr = self.startbr,
            endbr = self.endbr
        )
        child.start = start
        child.parent = self
        child.depth = self.depth+1
        return child
    
    def read_one_invariant(self):
        text = self.text
        invs = [self]
        length = len(text)
        for i,c in enumerate(text):
            if c in self.startbr:
                invariant = invs[0].new_child(text[i:],i)
                invs.insert(0,invariant)
                continue
            if c in self.endbr:
                invariant = invs[0]
                invariant.text = invariant.text[:-length+i]+self.endbr
                invs.remove(invariant)
                if len(invs)==1:
                    # print(invariant.text)
                    return invariant.text
                continue
            if c==" ":continue
            if invs[0].depth==0 :return c
        return text
        
    def reversed(self):
        return Ireko(
            text = self.text[::-1],
            startbr = self.endbr,
            endbr =  self.startbr,
            start = len(self.text)-self.start
        )
    
    def copy(self):
        return Ireko(
            text = self.text,
            startbr = self.startbr,
            endbr = self.endbr,
            parent = self.parent,
            depth = self.depth,
            start = self.start
        )
    
    def read_mom(self):
        f = re.search("/",self.text)
        after_Ireko = self.copy()
        after_Ireko.text = self.text[f.start()+1:]
        mom = after_Ireko.read_one_invariant()
        return mom
    
    def read_child(self):
        f = re.search("/",self.text)
        before_Ireko = self.copy()
        before_Ireko.text = self.text[:f.start()+1]
        before_Ireko.reversed()
        mom = before_Ireko.read_mom()
        child = mom[::-1]
        return child
    
def transform_dint(text,startbr,endbr):
    m = re.search("\\\\dint",text)
    if not m: return text
    ireko = Ireko(
        text = text[m.end():],
        startbr = startbr,
        endbr = endbr
    )
    low = ireko.read_one_invariant()
    ireko.text = ireko.text[len(low):]
    high = ireko.read_one_invariant()
    text = text.replace("\\dint"+low+high,"\\displaystyle\\int_"+low+"^"+high)
    text = transform_dint(text,startbr,endbr)
    # print(target[:20].replace(low+high,"\\displaystyle\\int_"+low+"^"+high))
    return text

import webbrowser


class Video(models.Model):
    """動画を表すモデル"""
    name = models.CharField(max_length=200, help_text='この動画名前を入力してください')
    data = models.JSONField(help_text='このFieldはYoutubeAPIによって読み込まれます。')
    title = models.CharField(max_length=200,blank=True, help_text='この動画のタイトルを入力してください')
    description = models.TextField(max_length=10000, blank=True, help_text='この動画の説明を入力してください')
    question = models.TextField(max_length=1000, blank=True, help_text='この動画の問題テキストを入力してください')
    table = ListCharField(base_field=models.CharField(max_length=50), max_length=(50 * 20), null=True, help_text='この動画の目次を入力してください')
    videoId = models.CharField(max_length=100,blank=True,help_text='解説動画のYoutubeIDを入力してください')
    problem = models.ForeignKey(Problem, on_delete = models.CASCADE, help_text='問題を指定してください')
    related_terms = models.ManyToManyField(Term, help_text='この記事に関連する用語を選んでください')
    pub = models.DateTimeField(default = timezone.now)

    def display_terms(self):
        terms = self.related_terms.all()
        terms = ",".join(map(lambda x: x.name,terms))
        return terms
    
    def make_name(self):
        category = Category.objects.get(name="テーマ別記事")
        for article in self.problem.articles.exclude(parent=category):
            name = "%s%s %s" % (name,article.parent.name,article.name)
            print("title: %s" % name)

    def make_youtube_url(self):
        return "https://youtu.be/%s" % self.videoId
    
    def make_studio_url(self):
        return "https://studio.youtube.com/video/%s/edit" % self.videoId
    
    def display_term_palylist(self):
        description = []
        for article in self.problem.articles.filter(type = "TER"):
            description.append("プレイリスト「%s」" % article)
            for i,v in enumerate(article.make_video_list()):
                if v.name == self.name:
                    description.append(" %s. %s" % (i+1,v))
                else:
                    url = v.make_youtube_url()
                    description.append(" %s. %s" % (i+1,url))
        return "\n".join(description)
    
    def open_youtube_sutudio(self):
        webbrowser.open(self.make_studio_url(),1)
        
    def display_table(self):
        if not self.table:
            return 
        return "\n".join(self.table)
    
    def make_next_videos_link(self):
        description = []
        for article in self.problem.articles.all():
            description.append("プレイリスト %s" % article.make_youtube_url())
            videos =  article.make_video_list()
            for i,v in enumerate(videos):
                if v!=self:continue
                if len(videos) == i+1:
                    description.append(" はじめから → %s" % videos[0].make_youtube_url())
                    break
                description.append( " 次の動画 → %s" % videos[i+1].make_youtube_url())
        return "\n".join(description)
    
    def make_from_data(self,data:object):
        self.data = data
        title =  data["snippet"]["title"]
        self.title = title
        self.name = TeX(title).videos_title_to_name()
        description = data["snippet"]["description"]
        description = description.replace("\r\n","\n")
        # description = re.sub("#\S*","",description)
        start_sign = ["問\d\s","問 ","問　","問.","問：","問 \n","問\n","問．\n"]
        for s in start_sign:
            description = description.replace(s,"問．")
        description = description.replace("． (","．(").replace(".(","．(").replace(". (","．(")
        questions = re.findall("問．(?:.+\n)*\n|問．(?:.+\n)*.+$",description)
        if questions: 
            self.question =  questions[0] ##プレーンテキストの状態で保持
        table = re.findall("\d*:\d\d\s.*",data["snippet"]["description"].replace(",","_"))
        if table:
            self.table = table
        self.videoId = data["id"]
        # self.save()
        print("new Video %s" % self)
        return self
    
    def make_terms_from_data(self,data:object):
        tags =[]
        t = re.compile("#\S*")
        tags += t.findall(data["snippet"]["title"])
        tags += t.findall(data["snippet"]["description"])
        newtages = []
        for tag in tags:
            newtages += [tag.replace("#","")]
        tags = newtages
        tags += data["snippet"]["tags"]
        for tag in tags:
            if not tag : continue
            if re.match("\d*$",tag) and len(tag)<4:continue
            t = Term.objects.filter(name = tag)
            if t:
                # print("Term: %s は すでにあります。" % tag)
                self.related_terms.add(t[0])
                continue;
            newTerm = Term.objects.create(
                name = tag,
                hurigana = conv.do(tag),
                # en_name = tr.translate(tag, dest="en").text,
            )
            print("new Term: %s (video:%s)" % (newTerm,self))
            self.related_terms.add(newTerm)
        terms = list(self.related_terms.all())
        for i,t in enumerate(terms[:-1]):
            for s in terms[i+1:]:
                t.related_terms.add(s)
        return self
    
    # class Meta:
    #     ordering = ["pub"]
            
    def get_absolute_url(self):
        return reverse('video-detail', args=[str(self.id)])

    def __str__(self):
        return self.name
    

    


    

### YoutubeVideo
    

class YoutubeChannel(models.Model):
    channelId = models.CharField(max_length=100,help_text='チャンネルのYoutubeIDを入力してください')

    def get_playlists(self):#,pagetoken)
        print("チャンネル「%s」のプレイリストをダウンロードします" % self.channelId)
        pageToken = ""
        playlists = []
        while True:
            res = youtube.playlists().list(
                channelId = self.channelId,
                part='snippet',
                maxResults = 100,
                pageToken = pageToken
            ).execute()
            playlists.extend(res["items"])
            try:
                pageToken = res["nextPageToken"]
                continue
            except:
                break
            
        return map(lambda data : YoutubePlaylist.objects.create(data = data),playlists)
    
    def get_uploads_playlistItems(self):
        print("チャンネル「%s」のアップロードプレイリストをダウンロードします" % self.channelId)
        res = youtube.channels().list(
            id = self.channelId,
            part="contentDetails"
        ).execute()
        channel_data = res["items"][0]
        print(channel_data)
        pageToken = ""
        playlistItems = []
        while True:
            print("チャンネル「%s」のアップロードプレイリストのページトークン「%s」をダウンロードします" % (self.channelId,pageToken))
            playlistItems_res = youtube.playlistItems().list(
                playlistId = channel_data["contentDetails"]["relatedPlaylists"]["uploads"],
                part='snippet',
                maxResults = 100,
                pageToken = pageToken
            ).execute()
            playlistItems.extend(playlistItems_res["items"])
            # if not playlistItems_res["nextPageToken"] : 
            try:
                pageToken = playlistItems_res["nextPageToken"]
                continue
            except:
                break
        return map(lambda data: YoutubePlaylistItem.objects.create(data = data), playlistItems)
    
class YoutubePlaylist(models.Model):
    data = models.JSONField(help_text='このFieldはYoutubeAPIによって読み込まれます。')

    def get_playlistId(self):
        return self.data["id"]

    def get_title(self):
        return self.data["snippet"]["title"]

    def get_description(self):
        return self.data["snippet"]["description"]
    
    def __str__(self):
        return self.get_title()
    
    def get_playlistItems(self):
        playlistItems = []
        pageToken = ""
        print("プレイリスト「%s」のプレイリストアイテムをダウンロード" % self)
        while True:
            res = youtube.playlistItems().list(
                playlistId = self.get_playlistId(),
                part='snippet',
                maxResults = 100,
                pageToken = pageToken
            ).execute()
            playlistItems.extend(res["items"])
            try:
                pageToken = res["nextPageToken"]
                continue
            except:
                break
        return map(lambda data: YoutubePlaylistItem.objects.create(data =data), playlistItems)
    
    def insert_on_youtube(self):
        response = youtube.playlists().insert(
            part="snippet,status",
            body=self.data
        ).execute()
        print("新しいプレイリストのid: %s" % response["id"])
        self.data = response
        self.save()
        return self
    
    def update_on_youtube(self):
        response = youtube.playlists().update(
            part="snippet,status",
            body=self.data
        ).execute()
        print("プレイリスト「%s」が更新されました" % response["snippet"]["title"])
        self.data = response
        self.save()
        return self
    
    def delete_on_youtube(self):
        response = youtube.playlists().delete(
            id=self.data["id"]
        ).execute()
        print("プレイリスト「%s」が削除されました" % response)
        self.delete()
    
    def update_title(self):
        old_data = self.data
        old_title = old_data["snippet"]["title"]
        title = old_title
        if not "セット" in title: return self;
        new_title = title.replace("セット","").replace("問題","").replace("事項","")
        print("Playlist:%s のtitleの変更：\n  「%s」\n   →→→「%s」" % (self,old_title,new_title))
        new_data = old_data
        new_data["snippet"]["title"] = new_title
        self.data = new_data
        # self.save()
        return self
    
    def update_description(self):
        old_data = self.data
        old_description = old_data["snippet"]["description"]
        title = old_data["snippet"]["title"]
        description = old_description.replace("\r\n","\n").replace("　"," ").replace("\n \n","\n")
        new_descriotion = description
        if not "セット" in title: return self;
        t = re.findall("(\S*)\s",title)
        if not t : 
            print("%sのタイトルにスペースがないのでテーマを検知できません。" % title)
            sys.exit()
        term = t[0]
        if "基本" in title:
            new_descriotion = "単元の勉強をしていて，「%sの基本から理解したい」と思った人向けの問題セットです。根底からじっくり、ゆっくり、%sについての理解を深めていきましょう。" % (term,term)
        if "典型" in title:
            new_descriotion = "定期テストに向けての勉強で，「%sの典型問題を押さえたい」と高校生向けの問題セットです。有効活用して、%sの全体像を掴みましょう。" % (term,term)
        if "応用" in title:
            new_descriotion = "「定期テストで%sの応用問題にチャレンジしたい」という高校生向けの問題セットです。%sを一段階レベルアップさせます。" % (term,term)
        if "強化" in title:
            new_descriotion = "受験に向けての勉強をしていて，「自分は%sが弱いなぁ」と感じた受験生向けの問題セットです。%sへの理解の度合いを、一段階、強化させます。" % (term,term)
        new_data = old_data
        new_data["snippet"]["description"] = new_descriotion
        print(new_descriotion)
        self.data = new_data
        # self.save()
        return self
    
class YoutubePlaylistItem(models.Model):
    data = models.JSONField(help_text='このFieldはYoutubeAPIによって読み込まれます。')

    def get_title(self):
        return self.data["snippet"]["title"]
    
    def get_videoId(self):
        return self.data["snippet"]['resourceId']["videoId"]
    
    def __str__(self):
        return self.get_title()
    
    def get_video(self):
        print("プレイリストアイテム「%s」のビデオを取得" % self)
        res = youtube.videos().list(
            id = self.get_videoId(),
            part='snippet',
        ).execute()
        return YoutubeVideo.objects.create(data = res["items"][0])
    
    def insert_on_youtube(self):
        response = youtube.playlistItems().insert(
            part="snippet",
            body=self.data
        ).execute()
        print("ビデオ「%s」をプレイリスト「%s」に追加しました。" % (response["snippet"]["resourceId"]["videoId"],response["snippet"]["playlistId"]))    

class YoutubeVideo(models.Model):
    data = models.JSONField(help_text='このFieldはYoutubeAPIによって読み込まれます。')
    caption = models.JSONField(null=True,blank = True,help_text='このFieldはYoutubeAPIによって読み込まれます。')

    def get_videoId(self):
        return self.data["id"]
    def get_title(self):
        return self.data["snippet"]["title"]
    def get_description(self):
        return self.data["snippet"]["description"]
    
    def __str__(self):
        return self.get_title()
    
    def update_title(self):
        old_data = self.data
        old_title = old_data["snippet"]["title"]
        new_data = old_data
        title = old_title
        title = join_diacritic(title)
        title = re.sub("(#\S+)","",title)
        title = re.sub("(【\S+】)","",title)
        title = title.replace("Ⅲ","III")
        title = re.sub("数学(\w*)\s.*","",title)
        title = re.sub("#\S*","",title)
        title = re.sub("【\w*】","",title)
        title = re.sub("＜\w*＞","",title)
        title = re.sub("\s$","",title)
        # title = re.sub("\s.*?大","",title)
        new_title = title
        new_data["snippet"]["title"] = new_title
        print("Video:%s のtitleの変更：%s" % (self,new_title))
        # description = old_data["snippet"]["description"]
        # new_data["snippet"]["description"] = "%s\n\nold_name:%s" % (description,old_title)
        self.data = new_data
        # self.save()
        return self
    

    def add_item_headline_of_description(self):
        old_data = self.data
        old_description = old_data["snippet"]["description"]
        description = old_description.replace("\r\n","\n").replace("　"," ").replace("\n \n","\n")
        
        for s in ["問\d\s","問\s","問\.","問：","問 \n","問\n","問．\n","問．"]:
            description = re.sub("%s" % s,"＜問題＞\n",description)
        description = re.sub(".＜問＞\n","問",description)
        description = description.replace("問．","問 ")
        description = re.sub("\\\\\[(.*)\\\\\]"," \\1",description)
        description = re.sub("問等差数列","＜問題＞等差数列",description)
        description = description.replace("． (","．(").replace(".(","．(").replace(". (","．(")
        description = description.replace("\n．","\n")
        description = description.replace("\n \n","\n\n").replace("\n　\n","\n\n")
        description = re.sub("\n\nold_name:.*","",description)
        description = re.sub("(?:\n\n|^)(00?:00)","\n\n＜目次＞\n\\1",description)
        description = re.sub("＜\s?(\d)\s?つの解法＞","(\\1つの解法)",description)
        description = re.sub("＜\s?(\d)\s?つの計算法＞","(\\1つの計算法)",description)
        description = re.sub("＜それぞれ\s(\d)\s?つの解法＞","(それぞれ\\1つの解法)",description)
        description = re.sub("＜\s?(\d)\s?つの証明＞","(\\1つの証明)",description)
        description = re.sub("\n＜問題PDF＞数III特訓全21題\n","\n\n＜PDF＞\n数III特訓全21題 ",description)
        description = re.sub("\((.{,10}大.{0,20})\)\n\n","\n\n＜ソース＞\n\\1\n\n",description)
        
        description = re.sub("\s1日目\s複素数の計算[\s\S]*?\n\n","\n",description)
        description = re.sub("\n\n解けない漸化式シリーズ[\s\S]*?\n\n","\n\n",description)
        description = re.sub("シリーズ「表現の自由は、解法の自由。?」\n(:?.+\n)*\n","\n",description)
        description = re.sub("\nGoodNotesの問題\/手書き解答はこちら↓\n","\n\n＜PDF＞\n本シリーズ手書き解答 ",description)
        description = re.sub("\n\s1日目：非隣接型の漸化式[\s\S]*?\n\n","\n\n＜PDF＞\n文系入試 数学IAIIBで手薄になりがちな4テーマ\nhttps://www.icloud.com/iclouddrive/0jHFRRGs3DaGgE9QE30x6810Q\n\n",description)
        description = re.sub("\n「平均値の定理」[\s\S]*?\n\n","\n\n＜PDF＞\n平均値の定理5題 https://sites.google.com/view/hayakutikaisetu/%E5%B9%B3%E5%9D%87%E5%80%A4%E3%81%AE%E5%AE%9A%E7%90%86\n\n",description)
        description = description.replace("このような自由度の高い","\n\nこのような自由度の高い")
        for c in Category.objects.filter(type__in = ["CHA","SUB"]):
            description = description.replace("#%s " % c,"")
            description = description.replace("#%s\n" % c,"\n")
            description = description.replace("#%s$" % c,"\n")
            description = description.replace("#%s" % c,"")
        description = description.replace("#ベクトル","").replace("#場合の数","").replace("#確率","").replace("#三角比","").replace("#式の計算","").replace("#複素数と方程式","")
        description = description.replace("を導け．\n\n","を導け．\n")
        
        description = re.sub("#\d\s\w[\s\S]*?\n\n","",description)
        
        description = re.sub("\n＜?今回のキーワード＞?","\n＜キーワード＞",description)
        description = re.sub("\nキーワード：","\n＜キーワード＞",description)
        description = re.sub("\n＜キーワード＞\n\n","\n＜キーワード＞\n",description)
        k = re.search("＜キーワード＞\n((:?.+\n)*)\n|＜キーワード＞\n((:?.+\n)*)$",description)
        if k:
            canmad_keywords =re.findall("(.+?)，",k.group())                                                          
            if canmad_keywords:
                keywords = "#"+" #".join(canmad_keywords)
                description = re.sub("＜キーワード＞\n(:?.+\n)*\n|＜キーワード＞\n((:?.+\n)*)$","＜キーワード＞\n%s\n\n" % keywords,description)

        description = re.sub("(?:\n\n|^)(せわしない)","\n\n＜じっくり解説とは＞\n\\1",description)
        description = re.sub("(?:\n\n|^)(かたくるしい)","\n\n＜おあそび解説とは＞\n\\1",description)
        description = re.sub("(?:\n\n|^)(言葉だらけの)","\n\n＜むくち解説とは＞\n\\1",description)
        description = re.sub("(?:\n\n|^)(工夫を凝らした)","\n\n＜ふつうの解説とは＞\n\\1",description)
        description = re.sub("(?:\n\n|^)(解法の丸暗記に)","\n\n＜ほんしつ解説とは＞\n\\1",description)

        description = re.sub("【ミニ講義】微分の計算工夫[\s\S]*","\n\n",description)
        description = re.sub("【集中講義】通過領域 7題[\s\S]*","\n\n",description)
        description = re.sub("【2つの解法】定積分の基本計算[\s\S]*","",description)
        description = re.sub("面積の組み換え むくち解説シリーズ\n(((?:(?:[^＜\n])+\n)+\n+)+)","\n\n",description)
        description = re.sub("【2つの解法】定積分の基本計算[\s\S]*","",description)
        description = description.replace("この問題が基礎編で，本問が応用編。ぜひ繋げて理解したい。","")
        description = description.replace("この問題の解説は動画が4本に分かれています．","")
            
        description = re.sub("\n\n集中講義「三角関数の利用編」","\n\n＜この問題について＞\n集中講義「三角関数の利用編」",description)
        description = description.replace("\n³+b³+c³+d³-3abc-3bcd-3cda-3dab","\na³+b³+c³+d³-3abc-3bcd-3cda-3dab")
        description = description.replace("　　　　","")
        description = description.replace("\n\n(1)","\n(1)")
        description = description.replace("問(Lv.1)","問\n(Lv.1)")
        description = description.replace("( Lv.2)","(Lv.2)")
        description = description.replace("\n\nsin3α","\nsin3α")
        description = re.sub("\n\n撮影機材","\n\n＜使用機材＞",description)
        description = re.sub("\n\nカメラ","\n\n＜使用機材＞\nカメラ",description)
        description = description.replace("Iw3WqcSN＜使用機材＞","Iw3WqcSN\n\n＜使用機材＞")
        description = re.sub("\n\n(#[\s\S]{10,})\n\n","\n\n＜キーワード＞\n\\1",description)
        description = description.replace("~関連~","").replace("前の動画↓.*\n","")
        description = re.sub("\n\n((?:(?:[^＜\n].+\n)+.*youtu.*(?:\n\n|$))+)","\n\n＜関連問題＞\n\\1\n",description)
        description = re.sub("＞\n\s\n","＞\n",description)
        description = re.sub("\n\n\n","\n\n",description)
        description = re.sub("\n\n\n","\n\n",description)

        description = re.sub("\n\s+\n","\n\n",description)
        description = re.sub("\n\n\n","\n\n",description)
        description = re.sub("\n\n\n","\n\n",description)
        description = re.sub("(.)＜問題＞\n","\\1問",description)
        description = re.sub("[\n\s]I[$\n\s]","",description)
        description = re.sub("^(かったるい)","＜はやくち解説とは＞\n\\1",description)
        description = re.sub("\n\n\s(かったるい)","\n\n＜はやくち解説とは＞\n\\1",description)
        description = description.replace("\n ","\n")
        description = description.replace("問\n次の式を展開せよ．","問題把握")
        description = description.replace(" 問 等差数列をなす3数","＜問題＞\n等差数列をなす3数")
        description = description.replace("6YIw3WqcSN＜使用機材＞","6YIw3WqcSN\n\n＜使用機材＞")
        description = description.replace("前の動画↓\n\n","前の動画↓\n")
        description = description.replace("関連問題↓","")
        description = description.replace("＜関連する過去動画＞","＜関連問題＞")
        description = description.replace("√2^{√2^{√2^{…}}}\n\n","√2^{√2^{√2^{…}}}\n")
        description = description.replace("円に内接する四角形を極める3問 (Lv.1)","円に内接する四角形を極める3問\n(Lv.1)")
        description = description.replace("＜関連問題＞\n","")
        
        description = re.sub("^第\d問\s","＜問題＞\n",description)
        description = re.sub("\n\n第4問 実数","\n\n＜問題＞\n実数",description)
        description = re.sub("第3問＜PDF＞","第3問\n\n＜PDF＞",description)

        description = description.replace("c⁴(a−b)\n(1)","c⁴(a−b)\n\n(1)")
        description = description.replace("《グローバル7/5》","＜はやくち解説とは＞\n")
        description = description.replace("\n\n\n","\n\n").replace("\n\n\n","\n\n").replace("\n\n\n","\n\n").replace("\n\n\n","\n\n")
        description = re.sub("^\n\n＜じっくり解説とは＞","＜じっくり解説とは＞",description)
        # description = re.sub("(\n\n|^)((?:[^＜\n#][\s\S]+?(?:\n\n|$))+)","\\1＜この動画について＞\n\\2",description)
        description = re.sub("\n\n((?:(?:[^＜\n].+\n)+.*youtu.*(?:\n\n|$))+)","\n\n＜関連問題＞\n\\1\n",description)
        description = re.sub("\n([^＜\n])","\n \\1",description)

        new_descriotion = description
        new_data = old_data
        new_data["snippet"]["description"] = new_descriotion
        self.data = new_data
        print(new_descriotion)
        # self.save()
        return self
    
    def read_item(self):
        # print("Video:%s のdescriptionの変更："% self)

        description = self.data["snippet"]["description"]
        youtu = re.findall("youtu",description)
        related = re.findall("関連問題",description)
        # if 1<len(related):
        print("%s"% description)


        questions = re.findall("＜問題＞\n([\s\S]*?)(?:\n\n|$)",description)
        sources = re.findall("＜ソース＞\n([\s\S]*?)(?:\n\n|$)",description)
        tables = re.findall("\n(\d\d?\:\d\d\s.*)",description)
        keywords = re.findall("＜キーワード＞\n([\s\S]*?)(?:\n\n|$)",description)
        related_videos = re.findall("\n((?:[^＜\n].+\n)+.*youtu.+)(?:\n\n|$)",description)
        pdfs = re.findall("＜PDF＞\n([\s\S]*?)(?:\n\n|$)",description)
        other_texts = re.findall("(?:\n\n|^)([^＜\n#][\s\S]+?)(?:\n\n|$)",description)
        # if not other_texts:
        #     print("この動画についてなし")
        #     print(new_descriotion)

        # print("【問題】\n%s\n\n"% "\n\n".join(questions))
        # if sources:
        #     print("【ソース】\n%s\n\n"% "\n\n".join(sources))
        # if keywords:
        #     text = "".join(keywords)
        #     text = text.replace("\n","")
        #     text = re.sub("(\S)#(\S)","\\1 #\\2",text)
        #     if not "#" in text:
        #         text = "#"+text
        #         text = re.sub("，\s?"," #",text)
        #     print("【キーワード】\n%s\n\n"% text)
        #     # print(text)
        # if tables:
        #     print("【目次】\n%s\n\n"% "\n".join(tables))
        # print("【この動画について】\n%s\n\n"% "\n\n".join(other_texts))
        # if pdfs:
        #     print("【PDF】\n%s\n\n"% "\n\n".join(pdfs))
        # if related_videos:
        #     print("【関連問題】\n%s\n\n"% "\n\n".join(related_videos))

    
    def update_on_youtube(self):
        response = youtube.videos().update(
            part="snippet,status",
            body=self.data
        ).execute()
        print("ビデオ「%s」が更新されました" % response["snippet"]["title"])
        self.data = response
        self.save()
        return self
    






from django.core.validators import MaxValueValidator, MinValueValidator

class Color(models.Model):
    hue = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(255)])
    saturation = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(255)])
    lightness = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(255)])

    def get_hsl(self):
        return "hsl(%s,%s,%s)" % (self.hue,self.saturation,self.lightness)

    def __str__(self):
        pass

    # class Meta:
    #     db_table = ''
    #     al = '背景色'