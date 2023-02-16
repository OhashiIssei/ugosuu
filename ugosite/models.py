from django.db import models

from datetime import date
from django.urls import reverse #Used to generate URLs by reversing the URL patterns
from django.contrib.auth.models import User #Blog author or commenter


from django.utils import timezone
from django.contrib import admin


from django.db import models
from django_mysql.models import ListCharField


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
import util.normalize as normalize

class Term(models.Model):
    """用語を表すモデル"""
    name = models.CharField(max_length=200, help_text='用語名を入力してください')
    # hurigana = models.CharField(max_length=200, default="ふりがな" , help_text='ふりがなを入力してください')
    # en_name = models.CharField(max_length=200, blank=True, help_text='英語名を入力してください')
    # description = models.TextField(max_length=1000, blank=True, help_text='この用語の説明を入力してください')
    # related_terms = models.ManyToManyField("Term",help_text='この用語に関連する用語を選んでください')

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('term-detail', args=[self.id])
    
    def __str__(self):
        return self.name
    
    def videos_num(self):
        return self.video_set.count()
    
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
            name = normalize.join_diacritic(name)
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
        file_text = normalize.clean_up_lines(file_text)
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
    
    def isChapter(self):
        return self.type=="CHA"
            
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

import util.text_transform as text_transform

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
        text = text_transform.transform_dint(text,"{","}")
        text = re.sub("%+[^\n]*\n","\n",text)
        text = text.replace("\r","")
        text = text_transform.itemize_to_ol(text)
        text = text_transform.item_to_li(text)
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
        text = text_transform.itemize_to_ol(text)
        text = text_transform.item_to_li(text)
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
    

from youtube.models import Playlist,Video
    
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
    
class QuestionSet(models.Model):
    title = models.CharField(max_length=200, help_text='問題セットのタイトルを入力してください')
    problems = models.ManyToManyField(Question)

    def __str__(self):
        return self.title
    
    def make_from_playlist(self,playlist:Playlist):
        items = playlist.playlistItems()
        problems = [Question().make_from_video(item.video().video_on_app()) for item in items]
        question_set = QuestionSet(
            title = playlist.title(),
            problems = problems
        )
        print("QuestionSet「%s」を作成しました" % question_set)
        return question_set
    


# def display_statue():
#     print("Playlistの個数: %s" % len(Playlist.objects.all()))
#     print("Videoの個数: %s" % len(Video.objects.all()))
#     print("Termの個数: %s" % len(Term.objects.all()))

# display_statue()