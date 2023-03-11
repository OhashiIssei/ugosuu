from django.db import models

from django.urls import reverse #Used to generate URLs by reversing the URL patterns


from django.utils import timezone
from django.contrib import admin


from django.db import models


import sys,os

import codecs
import openpyxl

import codecs
import re

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


import re
    
CATEGORY_TYPE_CHOICES = [
    ('SUB', '科目'), 
    ('CHA', '章'), 
    ('SEC', '節'), 
    ('SSE', '分節'), 
    ('TER', 'テーマ'), 
    ('OTH', 'その他'), 
]

class Category(models.Model):
    name = models.CharField(max_length=200, default="name", unique=True)
    description = models.TextField(max_length=10000, blank=True)

    class Meta:
        ordering = ['id']

    def get_absolute_url(self):
        return reverse('category-detail', args=[str(self.id)])

    def __str__(self):
        return self.name
    
    def children(self):
        children = list(Article.objects.filter(parent = self))
        children.extend(list(Category.objects.filter(parent = self)))
        return children

    def ancestors(self):##先祖(自分含まない)
        module = self
        ancestors = []
        while module.parent:
            ancestors.insert(0, module.parent)
            module = module.parent
        return ancestors
    
class Subject(models.Model):
    name = models.CharField(max_length=200, default="name")
    category = models.ForeignKey(Category, on_delete = models.CASCADE, null=True)
    
    def __str__(self):
        return self.name
    
class Chapter(models.Model):
    name = models.CharField(max_length=200, default="name")
    subject = models.ForeignKey(Subject, on_delete = models.CASCADE, null=True)
    # icon = models.CharField(max_length=10000,  blank=True, help_text='このカテゴリのアイコンSVG')
    
    def __str__(self):
        return self.name
    
class Section(models.Model):
    name = models.CharField(max_length=200, default="name")
    chapter = models.ForeignKey(Chapter, on_delete = models.CASCADE, null=True)
    
    def __str__(self):
        return self.name
    
class Subsection(models.Model):
    name = models.CharField(max_length=200, default="name")
    section =  models.ForeignKey(Section, on_delete = models.CASCADE, null=True)
    
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

class Article(models.Model):
    name = models.CharField(max_length=200, default="name")
    path = models.CharField(max_length=200,default="/" ,blank=True)
    description = models.TextField(max_length=1000, blank=True)
    content = models.TextField(max_length=2000, blank=True, help_text='記事の内容をHTML形式で入力してください')
    type =  models.CharField(max_length=200, default = "OTH", choices = ARTICLE_TYPE_CHOICES)
    # parent = models.ForeignKey(Category, on_delete = models.CASCADE, blank=True,null=True)
    section = models.ForeignKey(Section, on_delete = models.CASCADE, blank=True,null=True)
    
    # related_terms = models.ManyToManyField(Term, help_text='この記事に関連する用語を選んでください')

    created_date = models.DateTimeField(default=timezone.now)
    update_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('article-detail', args=[str(self.id)])
    
    def html(self):
        return "articles/%s.html" % self.name

    def __str__(self):
        return self.name
            
LEVEL_CHOICES = [
    ('BASIC', '基礎レベル'), 
    ('ADVANCED', '発展レベル'), 
    ('EXAM', '大学入試問題'), 
    ('MANIA', 'マニア向け'), 
]

import util.text_transform as text_transform

from printviewer.models import Folder,Print

class Problem(models.Model):
    """問題を表すモデル"""
    name = models.CharField(max_length=200)
    text = models.TextField(max_length=1000)
    articles = models.ManyToManyField(Article)
    prints = models.ManyToManyField(Print)
    source = models.CharField(max_length=50,null=True, blank=True)
    answer = models.TextField('example_answer', max_length=10000, null=True, blank=True)
    link = models.URLField(max_length=50,null=True, blank=True)

    def get_admin_url(self):
        return "http://127.0.0.1:8000/admin/ugosite/problem/%s/" % self.id
    
    def get_absolute_url(self):
        return reverse('problem-detail', args=[str(self.id)])

    def __str__(self):
        return self.name
    

from youtube.models import Playlist,Video
    
class Question(models.Model):
    """問題を表すモデル (Problemから移行を検討中)"""
    name = models.CharField(max_length=200)
    text = models.TextField(max_length=1000)
    source = models.CharField(max_length=50,null=True, blank=True)
    answer = models.TextField('example_answer', max_length=10000, null=True, blank=True)

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