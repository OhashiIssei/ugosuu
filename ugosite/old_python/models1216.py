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

# ユーティリティ
from util.normalize import join_diacritic

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
# youtube_with_auth = get_authenticated_service()
youtube = build('youtube', 'v3', developerKey='AIzaSyD-ohN5V0dlXYHjP7lSrUgKcCgXDkjpR14')



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
            for r in [["hokudai","北大"],["kyoto","京大"],["tokyo","東大"],["kyushu","九大"],["nagoya","名大"],["osaka","阪大"],["titech","東工大"],["tohoku","東北大"]]:
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
    
    def get_youtube_url(self):
        return "https://youtube.com/playlist?list=%s" % self.playlistId
    
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
    
FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER = []
FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER += [["｛","\\{"],["｝","\\}"]]
superNum = ["⁰","¹","²","³","⁴","⁵","⁶","⁷","⁸","⁹"]
subNum = ["₀","₁","₂","₃","₄","₅","₆","₇","₈","₉"]
cricNum = ["⓪","①","②","③","④","⑤","⑥","⑦","⑧","⑨"]
for i,n in enumerate(superNum):
    FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER += [[n,"^%s" % i]]
for i,n in enumerate(subNum):
    FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER += [[n,"_%s" % i]]
for i,n in enumerate(cricNum):
    FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER += [[n,"\\raise0.2ex\hbox{\\textcircled{\\scriptsize{%s}}}" % i]]
FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER += [["ⁿ","^n"],["⁻","^-"],["⁺","^+"],["ₓ","_x"],["ₐ","_a"]]
FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER += [["′","'"],["∗","*"],["□","\\fbox{\\phantom{J}}"]]
FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER += [["≦","\\leqq "],["≧","\\geqq "],["≠","\\neq "],["→","\\to "],["−","-"]]
FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER += [["\\vec","\\overrightarrow "],["⇔","\iff"]]
FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER += [["π","\\pi "],["α","\\alpha "],["β","\\beta "],["γ","\\gamma"],["θ","\\theta "]]
FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER += [["∠","\\angle "],["△","\\triangle "],["◦","^\\circ "],["°","^\\circ "]]
FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER += [["log","\\log "],["sin","\\sin "],["cos","\\cos "],["tan","\\tan "]]
FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER += [["lim","\\displaystyle\\lim"],["∫","\\displaystyle\\int"],["∑","\\displaystyle\\sum"],["Σ","\\displaystyle\\sum"],["∞","\\infty "]]
FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER += [["nCr","_n\\text{C}_r"],["nCk","_n\\text{C}_k"]]
FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER += [["•••","\\cdots "],["•","\\cdot "],["·","\\cdot "],["・・・","\\cdots "],["・","\\cdot "],["…","\\cdots "]]


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
        # print(lines)
        text = "\n".join(lines)
        text = text.replace("<li>[(＊)]","<li class ='unorder'>(*) ")
        text = re.sub("<li>\[\([\d]\)\]","<li> ",text)
        text = re.sub("<li>\[([^\s]+)\]","<li class='unorder'> \\1 ",text)
        if not len(re.findall("<li.*>",text))==len(re.findall("</li>",text)):
            print("liの数が一致しません\n%s" % text)
            sys.exit()
        self.text = text
        return self.text
    
    def transform_frac(self):
        text = self.text
        f = re.search("/",text)
        if not f: return self
        # print(self.text)
        if text[f.start()-1] == "}" or text[f.end()+1] == "{":
            # print(text)
            ireko = Ireko(text=text,startbr="{",endbr="}")
        else:
            ireko = Ireko(text=text,startbr="(",endbr=")")
        mom = ireko.read_mom()
        child = ireko.read_child()
        frac = "\\displaystyle\\frac{%s}{%s}" % (child,mom)
        # print(frac)
        self.text = text.replace("%s/%s" % (child,mom),frac)
        # print("transform_frac を適用します")
        return self.transform_frac()
    
    def remove_displaystyle(self):
        text = self.text
        if not re.search("(?:\^|\_)\{\s*-?\\\\displaystyle",text):
            return self
        self.text = re.sub("(\^|\_)\{\s*-?\\\\displaystyle","\\1{",text)
        return self.remove_displaystyle()

    def transform_sqrt(self):
        text = self.text
        s = re.search("√",text)
        if not s: return self
        superNum = ["³","⁴","⁵","⁶","⁷","⁸","⁹"]
        for i,n in enumerate(superNum):
            text = text.replace("%s√" % n,"\\sqrt[%s]" % str(i+3))
        text = text.replace("√","\\sqrt ")
        self.text = text
        return self
    
    def add_left_right(self):
        text = self.text
        s = re.search("(?<!left)\([^ぁ-んァ-ヶ一-龠]*?\)",text)
        if not s: return self
        # print(self.text)
        ireko = Ireko(text=text,startbr="(",endbr=")")
        ireko.text = ireko.text[s.start():]
        inv = ireko.read_one_invariant()
        # print(inv)
        content = inv[1:-1]
        # print(content)
        # input("Please enter")
        added_left_right = "\\left(%s\\right)" % content
        # print(added_left_right)
        self.text = self.text.replace(inv,added_left_right)
        return self.add_left_right()
    
    def translate(self,rule):
        text = self.text
        for r in rule:
            text = text.replace(r[0],r[1])
        return self.text
    
    def text_to_tex(self):
        text = self.text
        text = re.sub("([0-9]{2,})","{\\1}",text)
        text = text.replace("　","").replace(" ","")
        text = text.replace("\r","")
        text = text.replace("\n ","\n")
        text = text.replace("\n\n","\n")
        texts = re.split("(?:\n|^)\([\d\w]\)",text)
        # texts = re.split("\n",text)
        newtexts = []
        for text in texts:
            lines = text.split("\n")
            newlines = [
                TeX(line).line_to_tex().text
                for line in lines
            ]
            newtexts += ["\n".join(newlines)]
        question = newtexts[0]
        if len(newtexts)>1:
            question = newtexts[0]
            for i,text in enumerate(newtexts[1:]):
                question += "\n(%s) %s" % (i+1,text)
        self.text = question
        return self.text
    
    def line_to_tex(self):
        line = self.text
        line = line.replace("　","").replace(" ","")
        line = join_diacritic(line)
        line = re.sub("([^ぁ-んァ-ヶ一-龠ー])(?:，|\,)", "\\1,\\\;",line)
        line = re.sub("([ぁ-んァ-ヶ一-龠々ー]),", "\\1，",line)
        line = re.sub("([ぁ-んァ-ヶ一-龠々ー])\.", "\\1．",line)
        line = re.sub("([ぁ-んァ-ヶ一-龠々ー])。", "\\1．",line)
        line = re.sub("([^ぁ-んァ-ヶ一-龠々ー．，。、]+)", " $\\1$ ",line)

        line = re.sub("([A-Z]{2,})","\\\\text{\\1}",line)
        line = re.sub("([A-Z^P])\s?\(","\\\\text{\\1}(",line)
        line = re.sub("点(.?)\s\$([A-Z])","点\\1 $\\\\text{\\2}",line)
        line = re.sub("心(.?)\s\$([A-Z])","心\\1 $\\\\text{\\2}",line)
        line = re.sub("ベクトル\s?\$(\\\\text\{[A-Z]{2}\})","$\\\\overrightarrow{\\1} ",line)
        line = re.sub("ベクトル\s?\$([a-z])"," $\\\\overrightarrow{\\1}",line)
        line = re.sub("(_\{.*\})C(_\{.*\})","\\1\\\\text{C}\\2",line)
        line = re.sub("\|([^ぁ-んァ-ヶ一-龠々ー]*?)\|","\\\\left|\\1\\\\right|",line)
        line = re.sub("\$Lv\.(\d)\$","Lv.\\1",line)
        line = TeX(line).transform_frac().text
        line = TeX(line).transform_sqrt().text
        line = TeX(line).add_left_right().text
        line = TeX(line).remove_displaystyle().text
        for r in FROM_VIDEO_DESCRIPTION_TO_TEX_LETTER:
            line = line.replace(r[0],r[1])
        line = re.sub("\^(.)\^(.)\^(.)\^(.)", "^{\\1\\2\\3\\4}",line)
        line = re.sub("\^(.)\^(.)\^(.)", "^{\\1\\2\\3}",line)
        line = re.sub("\^(.)\^(.)", "^{\\1\\2}",line)
        line = re.sub("\_(.)\_(.)\_(.)", "_{\\1\\2\\3}",line)
        line = re.sub("\_(.)\_(.)", "_{\\1\\2}",line)
        self.text = line
        return self
    
    def transform_to_html_list(self):
        text = self.text
        text = text.replace("＜","&lt;").replace("＞","&gt;")
        texts = re.split("\n\([\d\w]\)",text)
        question = texts[0]
        if len(texts)>1:
            question = texts[0]+"\n<ol class = 'small-question'>"
            for text in texts[1:]:
                question += "\n <li>%s</li>" % text
            question += "\n</ol>"
        self.text = question
        return question
    
    def transform_to_enumerate_list(self):
        text = self.text
        texts = re.split("\n\([\d\w]\)",text)
        question =  texts[0]
        if len(texts)==1:return question
        items = "\n".join(["\\item%s" % text for text in texts[1:]])
        item_max_length = max(len(re.findall("[\d\wぁ-んァ-ヶ一-龠々ー]",texts[i+1])) for i in range(len(texts)-1))
        item_num = len(texts)-1
        if item_max_length<10:
            question = """%s\n\\begin{edaenumerate}<%s>\n%s\n\\end{edaenumerate}\n""" % (texts[0],item_num,items)
        else:
            question = """%s\n\\begin{enumerate}\n%s\n\\end{enumerate}\n""" % (texts[0],items)
        return question
    
    def take_linebraek_if_list(self):
        text = self.text
        texts = re.split("(?:\n|^)\([\d\w]\)",text)
        print("text:%s" % text)
        if len(texts)==1:return text
        items = "\n".join(["(%s) %s\\\\" % (i+1,text) for i,text in enumerate(texts[1:])])
        if not texts[0]:
            return "%s\n" % items
        return "%s\\\\\n%s\n" % (texts[0],items)
    
    def make_math_line(self):
        text = self.text
        lines =  text.split("\n")
        for i,line in enumerate(lines):
            if re.match("\s\$\([\d\w]\)",line):continue
            if not re.match("\s\$([^ぁ-んァ-ヶ一-龠々ー]+)\$\s$",line):continue
            lines[i] = re.sub("\s\$([^ぁ-んァ-ヶ一-龠々ー]+)\$\s$","\\[\\1\\]",line)
        question = "\n".join(lines)
        self.text = question
        return question

class Problem(models.Model):
    """問題を表すモデル"""
    name = models.CharField(max_length=200, help_text='問題名を入力してください')
    text = models.TextField(max_length=1000, help_text='この問題の内容をJax形式で入力してください')
    articles = models.ManyToManyField(Article,help_text='この問題が含まれる記事を選んでください')
    source = models.ForeignKey(Source, on_delete = models.CASCADE,null=True, help_text='この問題のソースを選んでください')
    answer = models.TextField('example_answer', max_length=10000, null=True, blank=True, help_text='この問題の解答例をTeX形式で入力してください')

    def get_admin_url(self):
        return "http://127.0.0.1:8000/admin/ugosite/problem/%s/" % self.id
    
    def get_absolute_url(self):
        return reverse('problem-detail', args=[str(self.id)])

    def __str__(self):
        return self.name
    
    def make_from_my_tex(self,text:str):
        self.text = text
        FROM_MYTEX_DESCRIPTION_TO_JAX = []
        FROM_MYTEX_DESCRIPTION_TO_JAX += [["<","&lt;"],[">","&gt;"],["\\bunsuu","\\displaystyle\\frac"],["\\dlim","\\displaystyle\\lim"],["\\dsum","\\displaystyle\\sum"]]
        FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\vv","\\overrightarrow"],["\\bekutoru","\\overrightarrow"],["\\doo","^{\\circ}"],["\\C","^{\\text{C}}","\\sq{","\\sqrt{"]]
        FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\barr","\\left\\{\\begin{array}{l}"],["\\earr","\\end{array}\\right."]]
        FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\PP","^{\\text{P}}"],["\\QQ","^{\\text{Q}}"],["\\RR","^{\\text{R}}"]]
        FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\NEN","\\class{arrow-pp}{}"],["\\NEE","\\class{arrow-pm}{}"],["\\SES","\\class{arrow-mm}{}"],["\\SEE","\\class{arrow-mp}{}"]]
        FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\NE","&#x2197;"],["\\SE","&#x2198;"],["\\xlongrightarrow","\\xrightarrow"]]
        FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\hfill □","<p class = 'end'>□</p>"]]
        FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\bf\\boldmath", "\\bb"],["\n}\n","\n"],["\\bf", "\\bb"]]
        for r in FROM_MYTEX_DESCRIPTION_TO_JAX:
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
    parent = None
    
    def __init__(self,text,startbr,endbr):
        self.text = text
        self.startbr = startbr
        self.endbr = endbr

    def __str__(self):
        return self.text

    def new_child(self,text):
        child = Ireko(
            text = text,
            startbr = self.startbr,
            endbr = self.endbr
        )
        child.parent = self
        child.depth = self.depth+1
        return child
    
    def read_one_invariant(self):
        text = self.text
        invs = [self]
        length = len(text)
        for i,c in enumerate(text):
            if c in self.startbr:
                invariant = invs[0].new_child(text[i:])
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
        ireko = Ireko(
            text = self.text[::-1],
            startbr = self.endbr,
            endbr =  self.startbr,
        )
        ireko.parent = self.parent
        ireko.depth = self.depth
        return ireko
    
    def copy(self):
        ireko = Ireko(
            text = self.text,
            startbr = self.startbr,
            endbr = self.endbr,
        )
        ireko.parent = self.parent
        ireko.depth = self.depth
        return ireko
    
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
        reversed_Ideko = before_Ireko.reversed()
        mom = reversed_Ideko.read_mom()
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

### YoutubeVideo

class YoutubeChannel(models.Model):
    channelId = models.CharField(max_length=100,help_text='チャンネルのYoutubeIDを入力してください')

    def download_sections(self):#,pagetoken)
        print("チャンネル「%s」のセクションをダウンロードします" % self.channelId)
        res = youtube.channelSections().list(
            channelId = self.channelId,
            part='snippet,contentDetails',
        ).execute()
        print(res)
        for data in res["items"]:
            new_section = YoutubeChannelSection.objects.create(data = data)
            print("YoutubeChannelSection「%s」を新たに追加しました。" % new_section)


    def download_playlists(self):#,pagetoken)
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
        for data in playlists:
            YoutubePlaylist.objects.create(data = data)
    
    def download_uploads_playlistItems(self):
        print("Cannnel「%s」のアップロードプレイリストをダウンロードします" % self.channelId)
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
        
        return [YoutubePlaylistItem(data = data) for data in playlistItems]

            
    
class YoutubePlaylist(models.Model):
    data = models.JSONField(help_text='このFieldはYoutubeAPIによって読み込まれます。')

    def playlistId(self):
        return self.data["id"]

    def title(self):
        return self.data["snippet"]["title"]

    def description(self):
        return self.data["snippet"]["description"]
    
    def __str__(self):
        return self.title()
    
    def playlistItems(self):
        playlistId = self.playlistId()
        items = YoutubePlaylistItem.objects.filter(data__snippet__playlistId = playlistId)
        if not items:
            print("Playlist「%s」" % (self,len(items)))
            sys.exit()
        return list(items)
    
    def download_playlistItems(self):
        playlistItems = []
        pageToken = ""
        print("プレイリスト「%s」のプレイリストアイテムをダウンロード" % self)
        while True:
            res = youtube.playlistItems().list(
                playlistId = self.playlistId(),
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
        for data in playlistItems:
            YoutubePlaylistItem.objects.create(data = data)
    
    def update_on_youtube(self):
        response = youtube_with_auth.playlists().update(
            part="snippet,status",
            body=self.data
        ).execute()
        print("プレイリスト「%s」が更新されました" % response["snippet"]["title"])
        self.data = response
        self.save()

    def rewrite_title(self):
        title = self.title()
        data = self.data
        data["snippet"]["title"] = title
        self.data = data
    
class YoutubePlaylistItem(models.Model):
    data = models.JSONField(help_text='このFieldはYoutubeAPIによって読み込まれます。')

    def title(self):
        return self.data["snippet"]["title"]
    
    def videoId(self):
        return self.data["snippet"]['resourceId']["videoId"]
    
    def playlistId(self):
        return self.data["snippet"]["playlistId"]
    
    def __str__(self):
        return self.title()
    
    def download_video(self):
        print("プレイリストアイテム「%s」のビデオをダウンロード" % self)
        res = youtube.videos().list(
            id = self.videoId(),
            part='snippet',
        ).execute()
        new_data = res["items"][0]
        try:
            old_video = YoutubeVideo.objects.get(data__id = new_data["id"])
            old_video.data = new_data
            old_video.save()
            print("YoutubeVideo「%s」のデータを更新しました" % old_video)
            return old_video
        except:
            new_video = YoutubeVideo.objects.create(data = new_data)
            print("YoutubeVideo「%s」を新たに追加しました。" % new_video)
            return 
        
    def video(self):
        try:
            return YoutubeVideo.objects.get(data__id = self.videoId())
        except:
            videos = YoutubeVideo.objects.filter(data__id = self.videoId())
            if len(videos)==0:
                print("Video「%s」は存在しません！" % self)
                if input("ダウンロードしますか？y/n")=="n": return
                return self.download_video()
            if len(videos)>1:
                print("Video「%s」は複数存在します！" % self)
                if input("ダウンロードしなおしますか？y/n")=="n": return
                videos.delete()
                return self.download_video()
            
        # print("Video「%s」を取得" % videos[0])
        

class YoutubeVideo(models.Model):
    data = models.JSONField(help_text='このFieldはYoutubeAPIによって読み込まれます。')
    new_data = models.JSONField(null=True,blank = True,help_text='補正後のデータです。')

    def videoId(self):
        return self.data["id"]
    
    def title(self):
        return self.data["snippet"]["title"]
    
    def set_title(self,title:str):
        self.new_data = self.data
        self.new_data["snippet"]["title"] = title
        return self
    
    def extract_title_in_mytex(self):
        text = TeX(self.title()).line_to_tex().text
        return text.replace("$ ","$").replace(" $","$")
    
    def description(self):
        return self.data["snippet"]["description"]
    
    def set_description(self,text):
        self.new_data = self.data
        self.new_data["snippet"]["description"] = text
        return self
    
    def set_problem(self,text):
        self.new_data = self.data
        description = self.description()
        if not "＜問題＞" in description: return self
        description = re.sub("＜問題＞\n[\s\S]*?(\n\n|$)","＜問題＞\n%s\\1" % text,description)
        # description = description.replace("\r","").replace("\n\n\n","\n\n")
        self.new_data["snippet"]["description"] = description
        return self
    
    def __str__(self):
        return self.title()
    
    def description(self):
        return self.data["snippet"]["description"]
    
    def extract_problem(self):
        problems = re.findall("＜問題＞\n([\s\S]*?)(?:\n\n|$)",self.description())
        if len(problems)==0:return
        if len(problems)>1:
            print("%sは複数の問題が記述されています" % self)
            # sys.exit()
        problem = problems[0]
        return problem
    
    def extract_problem_in_tex(self):
        problem_text = self.extract_problem()
        if not problem_text:return
        text = problem_text
        text = TeX(text).text_to_tex()
        # text = TeX(text).transform_to_enumerate_list()
        text = TeX(text).take_linebraek_if_list()
        text = TeX(text).make_math_line()
        return text
    
    def extract_problem_in_mytex(self):
        text = self.extract_problem_in_tex()
        if not text:return
        # text = text.replace("\n","\\\\\n")
        text = text.replace("＜","<").replace("＞",">")
        text = text.replace("$ ","$").replace(" $","$")
        text = text.replace("\\displaystyle\\frac","\\bunsuu")
        text = text.replace("\\overrightarrow","\\vv")
        text = re.sub("\\\\left\|(.*?)\\\\right\|","\\\\zettaiti{\\1}",text)
        text = re.sub("\\\\\[(.*?)\\\\\]","\n\\\\vspace{0.3zw}\n\\\\hspace{0.5zw}$\\1\\\\vspace{0.3zw}$\n\n",text)
        return text
    
    def rewrite_title(self):
        title = self.title()
        old_title = title
        title = re.sub("\s?〜初級〜"," Lv.1",title)
        title = re.sub("\s?〜中級〜"," Lv.2",title)
        title = re.sub("\s?〜上級〜"," Lv.3",title)
        new_title =  title
        if old_title == new_title : return self
        self.set_title(title)
        print(title)
        return self
    
    def rewrite_problem(self):
        if not self.extract_problem():return self
        old_text = self.extract_problem()
        text = old_text
        a = re.search("\\\\vec\{[a-z]\}",text)
        if not a: return self
        text = re.sub("\\\\vec\{([a-z])\}","ベクトル\\1",text)
        new_text = text
        if new_text == old_text: return self
        self.set_problem(text)
        print("\n「%s」の問題文を変更しました:\n%s\n" % (self,self.description()))
        return self
    
    def youtube_studio_url(self):
        return "https://studio.youtube.com/video/%s/edit" % self.videoId()
    
    def update_on_youtube(self):
        response = youtube_with_auth.videos().update(
            part="snippet,status",
            body=self.new_data
        ).execute()
        print("ビデオ「%s」が更新されました" % response["snippet"]["title"])
        self.data = response
        self.new_data  = None
        self.save()
        return self
    
    def video_on_app(self):
        return VideoOnApp.objects.get(youtube_video = self)
    
    def playlists(self):
        id = self.videoId()
        return [
            YoutubePlaylist.objects.get(data__id = item.playlistId())
            for item in YoutubePlaylistItem.objects.all()
            if item.videoId() == id
        ]
    
    def main_playlist(self):
        playlists = self.playlists()
        if len(playlists)==1:
            return playlists[0]
        else:
            # playlist_list = ["%s:%s" % (i,playlist.title()) for i,playlist in enumerate(playlists)]
            # select_num = int(input("Please select num playlist:%s" % ",".join(playlist_list)))
            select_num = 0
            return playlists[select_num]
        
    
class VideoOnApp(models.Model):
    youtube_video = models.OneToOneField(YoutubeVideo,on_delete = models.CASCADE)

    def videoId(self):
        return self.youtube_video.videoId()

    def title(self):
        return self.youtube_video.title()
    
    def description(self):
        return self.youtube_video.description()

    def extract_problem(self):
        return self.youtube_video.extract_problem()
    
    def __str__(self):
        return self.title()
    
    def extract_table(self):
        description = self.description()
        items = re.findall("＜目次＞\n([\s\S]*?)(?:\n\n|$)",description)
        if len(items)==0:return
        if len(items)>1:
            print("%sは複数の目次が記述されています" % self)
            sys.exit()
        item = items[0]
        return item.split("\n")
    
    def extract_source(self):
        description = self.description()
        items = re.findall("＜ソース＞\n([\s\S]*?)(?:\n\n|$)",description)
        if len(items)==0:return
        if len(items)>1:
            print("%sは複数のソースが記述されています" % self)
            sys.exit()
        item = items[0]
        return item
    
    def extract_problem_in_jax(self):
        if not self.extract_problem():return
        text = TeX(self.extract_problem()).text_to_tex()
        return TeX(text).transform_to_html_list()
    
    def extract_related_videos(self):
        description = self.description()
        items = re.findall("＜関連問題＞\n((?:[\s\S]*?(?:\n\n|$))*)",description)
        if len(items)==0:return
        if len(items)>1:
            print("%sは複数の関連問題が記述されています" % self)
            sys.exit()
        item = items[0]
        return item.split("\n\n")
    
    def youtube_url(self):
        return "https://youtu.be/%s" % self.videoId()
    
class YoutubeChannelSection(models.Model):
    data = models.JSONField(help_text='このFieldはYoutubeAPIによって読み込まれます。')

    def title(self):
        return self.data["snippet"]["title"]

    def __str__(self):
        return self.title()

    def playlists(self):
        playlistIds = self.data["contentDetails"]["playlists"]
        playlists = []
        for playlistId in playlistIds:
            filtered_playlists = YoutubePlaylist.objects.filter(data__id = playlistId)
            if len(filtered_playlists)>1:
                print("プレイリスト「%s」は複数存在します！" % filtered_playlists[0])
                sys.exit()
            if len(filtered_playlists)==0:
                print("プレイリスト「%s」は存在しません！" % playlistId)
                return []
            playlists.append(filtered_playlists[0])
        return playlists
    
class Question(models.Model):
    """問題を表すモデル (Problemから移行を検討中)"""
    name = models.CharField(max_length=200, help_text='問題名を入力してください')
    text = models.TextField(max_length=1000, help_text='この問題の内容をJax形式で入力してください')
    source = models.ForeignKey(Source, on_delete = models.CASCADE,null=True, help_text='この問題のソースを選んでください')
    answer = models.TextField('example_answer', max_length=10000, null=True, blank=True, help_text='この問題の解答例をTeX形式で入力してください')

    def admin_url(self):
        return "http://127.0.0.1:8000/admin/ugosite/problem/%s/" % self.id
    
    def get_absolute_url(self):
        return reverse('problem-detail', args=[str(self.id)])

    def __str__(self):
        return self.name
    
    def make_from_video(self,video:VideoOnApp):
        question = Question(
            name = video.title(),
            text = video.extract_problem_in_jax(),
            source = video.extract_source()
        )
        print(" Question「%s」を作成しました" % question)
        return question
    
class QuestionSet(models.Model):
    title = models.CharField(max_length=200, help_text='問題セットのタイトルを入力してください')
    problems = models.ManyToManyField(Question)

    def __str__(self):
        return self.title
    
    def make_from_playlist(self,playlist:YoutubePlaylist):
        items = playlist.playlistItems()
        problems = [Question().make_from_video(item.video().video_on_app()) for item in items]
        question_set = QuestionSet(
            title = playlist.title(),
            problems = problems
        )
        print("QuestionSet「%s」を作成しました" % question_set)
        return question_set
    

import subprocess
import os
import imagesize

TEMPLATE_PATH = './thumbnails/templates/texs/thumbnail_template.tex'
BACKGROUND_IMAGE_DIR = "./thumbnails/templates/smart_background"
THUMNAIL_FOR_EACH_VIDEO_DIR =  "./thumbnails/for_each_video"

class YoutubeThumbnail(models.Model):
    youtube_video = models.ForeignKey(YoutubeVideo,on_delete = models.CASCADE)
    tex_text = models.TextField(null = True)

    def __str__(self):
        return "「%s」のサムネイル" % self.youtube_video.title()

    def videoId(self):
        return self.youtube_video.videoId()

    def make_texfile(self):
        text = self.make_tex_text_from_description()
        t = open(TEMPLATE_PATH, 'r')
        template_text = t.read()
        path = self.texfile_path()
        f = open(path, 'w')#  % timezone.now()
        file_text = template_text.replace("{{template}}",text)
        f.write(file_text)
        f.close()

    def make_tex_text_from_description(self):
        video = self.youtube_video
        video_title = video.extract_title_in_mytex()
        problem_text = video.extract_problem_in_mytex()
        if not problem_text:
            problem_text = video.description()
        title_size = self.calc_title_size_name()
        text_size = self.calc_text_size_name()
        image_path = self.background_image_path()
        width, height = imagesize.get(image_path)
        genre = self.extract_genre_from_playlist()
        level = self.extract_level_from_playlist()
        genre_name = genre.replace("数III","数Ⅲ").replace("数II","数Ⅱ").replace("数I","数Ｉ").replace("数A","数Ａ").replace("数B","数Ｂ")
        background_image = "\n\n\\at(0cm,0cm){\\includegraphics[width=8cm,bb=0 0 %s %s]{%s}}\n" % (width, height,image_path)
        text = "{\\color{orange}\\bf\\boldmath%s\\underline{%s}}\\vspace{0.3zw}\n\n%s \n\\bf\\boldmath 問．%s\n" % (title_size,video_title,text_size,problem_text)
        xpos_list = [7.2,7.2,7.2,7.2,7.0,6.8,6.6,6.4,6.2,6.0]
        xpos = xpos_list[len(genre_name)]
        genre_mark = "\\at(%scm,0.2cm){\\small\\color{%s}$\\overset{\\text{%s}}{\\text{%s}}$}\n" % (xpos,"bradorange",genre_name,level)
        tex_text = background_image+text+genre_mark
        self.tex_text = tex_text
        return tex_text
    
    def background_image_path(self):
        if not self.extract_genre_from_playlist():
            return ""
        image_path = "%s/%s.jpeg" % (BACKGROUND_IMAGE_DIR,self.extract_genre_from_playlist())
        if os.path.isfile(image_path):
            return image_path
        return "%s/黒板風.jpeg" % BACKGROUND_IMAGE_DIR
    
    def calc_evaluation(self,text:str):
        if not text:
            input("%sはどこかおかしい？" % self)
        zenkaku_num = len(re.findall("[ぁ-んァ-ヶ一-龠々ー〜．，]",text))
        hankaku_num = len(re.findall("[a-zA-Z\.\s\+\-\(\)\=\,0-9\|\<\>]",text))
        linesep_num = len(re.findall("\n",text))
        evaluation = zenkaku_num + hankaku_num/2 + linesep_num*8
        return evaluation
    
    def calc_text_size_name(self):
        video = self.youtube_video
        raw_text = video.extract_problem()
        evaluation = self.calc_evaluation(raw_text)
        # print(evaluation)
        if evaluation>=200: return "\\scriptsize"
        if evaluation>=150: return "\\small"
        if evaluation>=100: return "\\normalsize"
        if evaluation>=80:  return "\\large"
        if evaluation>=50:  return "\\Large"
        if evaluation>=30:  return "\\LARGE"
        if evaluation>=15:  return "\\huge"
        return "\\HUGE"
        
    def calc_title_size_name(self):
        video = self.youtube_video
        title = video.title()
        evaluation = self.calc_evaluation(title)
        # print(evaluation)
        if evaluation>=18:  return "\\normalsize"
        if evaluation>=15:  return "\\large"
        if evaluation>=12:  return "\\Large"
        if evaluation>=9:   return "\\LARGE"
        return "\\huge"
        
    def extract_genre_from_playlist(self):
        video = self.youtube_video
        playlist = video.main_playlist()
        s = re.findall("(.*?)\s",playlist.title())
        if not s:return playlist.title()
        genre_name = s[0]
        return genre_name

    def extract_level_from_playlist(self):
        video = self.youtube_video
        playlist = video.main_playlist()
        s = re.findall("\s(.*?)\d",playlist.title())
        if not s:return
        level_name = s[0]
        return level_name
    
    def get_level_color(self):
        if self.extract_level_from_playlist()=="計算": return "bradorange"#"mizu"
        if self.extract_level_from_playlist()=="基本": return "bradorange"#"yellow"
        if self.extract_level_from_playlist()=="典型": return "bradorange"
        if self.extract_level_from_playlist()=="応用": return "bradorange"#"pink"
        if self.extract_level_from_playlist()=="強化": return "bradorange"#"red"

    def make_image(self):
        texfile = self.texfile_path()
        FileTranformer().ptex2pdf(texfile,"./thumbnails/texs")
        pdffile =  self.pdf_path()
        jpegfile = self.jpeg_path()
        FileTranformer().pdf2jpeg(pdffile,jpegfile)
        if not os.path.isfile(jpegfile):return
        return jpegfile

class YoutubeVideoUpdateSet(models.Model):
    name = models.CharField(max_length=50)
    videos = models.ManyToManyField(YoutubeVideo)

    def __str__(self):
        return self.name
    
    def main_dir(self):
        return "./thumbnails//%s" % self
    
    def texs_dir(self):
        return "%s/texs" % self.main_dir()
    
    def jpegs_dir(self):
        return "%s/jpegs" % self.main_dir()

    def texfile_path(self):
        return "%s/thumbnails.tex" % self.texs_dir()
    
    def pdf_path(self):
        return "%s/thumbnails.pdf" % self.texs_dir()
    
    def jpeg_path(self):
        return "%s/thumbnails.jpeg" % self.jpegs_dir()
    
    def jpeg_with_num_path(self,i):
        return "%s/thumbnails-%s.jpeg" % (self.jpegs_dir(),i)

    def make_from_playlist(self,playlist:YoutubePlaylist):
        items = playlist.playlistItems()
        video_set = YoutubeVideoUpdateSet.objects.create(name = playlist.title().replace(" ","_"))
        for item in items:
            video_set.videos.add(item.video())
        return video_set
    
    def join(self,video_sets,set_name:str):
        new_video_set = YoutubeVideoUpdateSet.objects.create(name = set_name)
        for video_set in video_sets:
            for video in video_set.videos.all():
                new_video_set.videos.add(video)
        return new_video_set
    
    def make_dirs(self):
        main_dir_path = self.main_dir()
        texs_path = self.texs_dir()
        jpegs_path = self.jpegs_dir()
        if not os.path.isdir(main_dir_path):
            os.mkdir(main_dir_path)
            print("新たにディレクトリを作成しました:\n %s" % main_dir_path)
        if not os.path.isdir(texs_path):
            os.mkdir(texs_path)
            print("新たにディレクトリを作成しました:\n %s" % texs_path)
        if not os.path.isdir(jpegs_path):
            os.mkdir(jpegs_path)
            print("新たにディレクトリを作成しました:\n %s" % jpegs_path)
    
    def make_texfile(self):
        videos = self.videos.all()
        content_texts = []
        for video in videos:
            try:
                thumbnail = YoutubeThumbnail.objects.filter(youtube_video=video).last()
                content_texts.append(thumbnail.tex_text)
            except:
                thumbnail = YoutubeThumbnail(youtube_video=video)
                content_texts.append(thumbnail.make_tex_text_from_description())
        content_path = self.texfile_path()
        t = codecs.open(TEMPLATE_PATH, 'r','utf-8')
        template_text = t.read()
        f = codecs.open(content_path, 'w', 'utf-8')#  % timezone.now()
        file_text = template_text.replace("{{template}}","\n\n\\newpage\n\n".join(content_texts))
        f.write(file_text)
        f.close()

    def save_each_data_form_texfile(self):
        content_path = self.texfile_path()
        f = codecs.open(content_path, 'r','utf-8')#  % timezone.now()
        all_text = f.read()
        t = re.findall("\\\\begin\{document\}([\S\s]*?)\\\\end\{document\}",all_text)
        document_text = t[0]
        document_text = document_text.replace("\r","")
        document_text = document_text.replace("\n\n\n","\n\n").replace("\n\n\n","\n\n").replace("\n\n\n","\n\n").replace("\n\n\n","\n\n")
        texts = re.split("\n*\\\\newpage\n*",document_text)
        videos = self.videos.all()
        for i,video in enumerate(videos):
            thumbnail = YoutubeThumbnail.objects.create(youtube_video=video,tex_text =  texts[i])
            print("%sを再利用可能データとして新規登録しました" % thumbnail)

    def ptex2pdf(self):
        dir = "./thumbnails/%s/texs" % self
        tex_path = self.texfile_path()
        FileTranformer().ptex2pdf(tex_path,dir)

    def pdf2jpeg(self):
        FileTranformer().pdf2jpeg(self.pdf_path(),self.jpeg_path())

    def set_on_youtube(self):
        for i,video in enumerate(self.videos.all()):
            path = self.jpeg_with_num_path(i)
            if not os.path.isfile(path):
                input("次のファイルが見つかりません:%s" % path)
            videoId = video.videoId()
            response = youtube_with_auth.thumbnails().set(
                videoId=videoId,
                media_body=path
            ).execute()
            print("ビデオ「%s」が更新されました：\n%s" % (video,response))