from django.db import models

from django.utils import timezone
from django.contrib import admin

import os

import openpyxl

import pathlib
import datetime

import re

# ユーティリティ
import util.normalize as normalize

from .models import Article,Category,Term

FOUR_STEP_DATA = [
    ["I","k4step_b1a.xlsx",0],
    ["A",'k4step_b1a.xlsx',1],
    ["II",'k4step_b2b.xlsx',0],
    ["B",'k4step_b2b.xlsx',1],
    ["III",'k4step_b3.xlsx',0]
]
    
MEDIA_LOCAL_PATH = "/Users/greenman/local_django_projects/ugosuu/media_local"

FOUR_STEP_PATH =  f"{MEDIA_LOCAL_PATH}/four_step"

def create_categories_form_four_step():
    
    def article_type(title:str):
        if re.match("[０-９]\s|1[0-9]\s",title): return "BAS"
        if re.match("研究\s",title): return "STU"
        if re.match("発展\s",title): return  "DEV"
        if re.match("補\s",title): return "SUP"
        if re.search("演習問題",title) : return "PRA"
        return ""
    
    def parent_of_article(title:str):
        type = article_type(title)
        if type == "PRA":
            return Category.objects.filter(type = "CHA").last()
        return Category.objects.filter(type__in = ["CHA","SEC"]).last()

    def article_from_title(title:str):
        result = Article(name = title)
        result.type = article_type(title)
        # if not result.type: return result
        result.parent = parent_of_article(result.type)
        print("new Article: %s (parent: %s)" % (result, result.parent))
        return result
    
    def type_of_category(title:str):
        if re.match("第[０-９]章",title):return "CHA"
        if re.match("第[０-９]節",title):return "SEC"
        
    def parent_of_category(title:str):
        type = type_of_category(title)
        if type=="CHA":return Category.objects.filter(type = "SUB").last()
        if type=="SEC":return Category.objects.filter(type = "CHA").last()
    
    def category_from_title(title:str):
        result = Category(name = title)
        result.type = type_of_category(title)
        result.parent = parent_of_category(title)
        name = title
        name = re.sub("\s(\w)\s(\w)$"," \\1\\2",name)
        name = re.sub("(^第[０-９]章\s)","",name)
        name = re.sub("(^第[0-9]章\s)","",name)
        name = re.sub("(^第[０-９]節\s)","",name)
        name = re.sub("(^[０-９]\s)","",name)
        name = re.sub("(^研究\s)","",name)
        name = re.sub("(^補\s)","",name)
        name = re.sub("(^発展\s)","",name)
        result.name = name
        return result
    
    Category.objects.filter(name = "高校数学").delete()
    # Category.objects.all().delete()
    parent_category = Category.objects.create(name = "高校数学")
    for data in FOUR_STEP_DATA:
        child_category = Category.objects.create(
            name = "数学%s" % data[0],
            parent = parent_category,
            type = "SUB",
        )
        print("new Category: %s (parent: %s)" % (child_category, child_category.parent))
        
        file_path = '%s/%s' % (FOUR_STEP_PATH,data[1])
        loaded_workbook = openpyxl.load_workbook(file_path)
        sheet_num = data[2]
        worksheet = loaded_workbook.worksheets[sheet_num]
    
        for i in range(1000):
            if i <3 : continue
            cell = worksheet.cell(i,2)
            if not cell.value : continue
            title = cell.value.replace("　"," ")
            sub_category = category_from_title(title)
            if sub_category.type in ["CHA","SEC"]:
                sub_category.save()
                print("new Category: %s (parent: %s)" % (sub_category, sub_category.parent))
                continue
            article_from_title(title).save()

KOUSIKANKEI_PATH = '/Users/greenman/Library/Mobile Documents/com~apple~CloudDocs/講師関係'

class TeXfile:
    def __init__(self,path:str):
        self.path = path
        
    def name(self):
        return os.path.basename(self.path)
        
    def content_text(self):
        with open(self.path) as f:
            result = f.read()
        result = normalize.clean_up_lines(result)
        s = re.search("\\\\begin{document}(.*\n)*\\\\end{document}",result)
        if not s: return ""
        return s.group().replace("\\sub{","\\subsection{")
    
    def isEmpty(self):
        if self.content_text():return True
        return False
    
    def subsections_num(self):
        f = re.findall("\\\\sub",self.content_text())
        return len(f)
        
        
    
        

def create_from_my_texfiles():
    parent_category = Category.objects.create(name = "講師関係")
    
    def make_from_my_texfile(texfile:TeXfile):
        if texfile.isEmpty():return
        
        if texfile.subsections_num()<2:
            new_article = Article.objects.create(
                name = texfile.name(),
                parent = parent_category
            )
            questions = re.findall("\n\\\\bqu((?:.*\n)*?)\\\\equ",texfile.content_text())
            if not questions: return
            print("new Article: %s (parent: %s)" % (new_article,new_article.parent))
            for text in questions:
                problem = Problem().make_from_my_tex(text)
                problem.articles.add(new_article)
            return new_article
        
        child_category = Category.objects.create(
            name = texfile.name(),
            parent = new_article.parent,
            path = texfile.path,
        )
        
        subsections = re.split("\n\\\\subsection",texfile.content_text())
        for subsection in subsections[1:]:
            n = re.findall("^{\\\\bb\s(.*)}",subsection)
            if n:
                name = n[0]
            else:
                name = "%s %s" % (child_category.name,len(child_category.children())+1)
            sub_article = Article.objects.create(
                name = name,
                parent = child_category,
            )
            print("new Article: %s (parent: %s)" % (sub_article,sub_article.parent))
            questions = re.findall("\n\\\\bqu((?:.*\n)*?)\\\\equ",subsection)
            for text in questions:
                problem = Problem().make_from_my_tex(text)
                problem.articles.add(sub_article)
                
    def update_my_folder(path:str):
        for fileName in os.listdir(path):
            if fileName.startswith('.'): continue
            if "阪大" in fileName: continue
            if "旧帝大" in fileName: continue
            file_path = "%s/%s" % (KOUSIKANKEI_PATH,fileName)
            if os.path.isdir(file_path):
                child_category = Category.objects.create(
                    name = fileName,
                    parent = parent_category,
                    path = file_path,
                )
                update_my_folder(file_path)
                continue
            if fileName.endswith(".tex"):
                make_from_my_texfile(TeXfile(file_path))
                
    update_my_folder(KOUSIKANKEI_PATH)

KAKOMON_PATH = '/Users/greenman/Library/Mobile Documents/com~apple~CloudDocs/旧帝大過去問'

def update_kakomon_folder():
    parent_category = Category.objects.create(name = "大学別62年過去問題集")
    for univ in sorted(os.listdir(KAKOMON_PATH)):
        if univ.startswith('.'): continue
        name = univ[3:]
        for r in [["hokudai","北大"],["kyoto","京大"],["tokyo","東大"],["kyushu","九大"],["nagoya","名大"],["osaka","阪大"],["titech","東工大"],["tohoku","東北大"]]:
            name = name.replace(r[0],r[1])
        child_category = Category.objects.create(
            name = name,
            type = "TER",
            parent = parent_category,
        )
        univ_path = "%s/%s" % (KAKOMON_PATH,univ)
        print("new Category: %s (parent: %s)" % (child_category,child_category.parent))
        for year in sorted(os.listdir(univ_path)):
            if year.startswith('.'):continue
            year_path = "%s/%s" % (univ_path,year)
            Article(parent = child_category).make_from_kakomon_folder(year_path)

# ICONS_PATH =  "/Users/greenman/Desktop/web-projects/django_projects/ugosite/media_local/icons"

# def update_icons():
#     for fileName in os.listdir(ICONS_PATH):
#         if not ".svg" in fileName:continue
#         svgPath = "%s/%s" % (ICONS_PATH,fileName)
#         name = fileName.replace(".svg","")
#         name = normalize.join_diacritic(name)
#         categorys = Category.objects.filter(name=name)

#         for category in categorys:
#             if not category.type in ["CHA","SEC"]:continue
#             with open(svgPath) as f:
#                 svg = f.read()
#             svg = re.findall("<svg[\s\S]*",svg)[0]
#             svg = re.sub("<svg","<svg class='icon'",svg)
#             svg = re.sub("stroke=.........\s","stroke='inherit' ",svg)
#             category.icon = svg
#             category.save()
#             print("Category: %sにiconを設定しました" % category)

# NOTES_PATH = '/Users/greenman/Desktop/web-projects/django_projects/ugosite/media_local/Notes'

# def update_note():
#     parent_category = Category.objects.create(name = "Notes")
#     for name in os.listdir(NOTES_PATH):
#         if name.startswith('.'):continue
#         if "attachments" in name:continue
#         p = pathlib.Path(NOTES_PATH)
#         filePath = "%s/%s" % (NOTES_PATH,name)
#         if os.path.isdir(filePath):
#             child_category = Category.objects.create(
#                 name = name,
#                 type = "OTH",
#                 created_date = datetime.datetime.fromtimestamp(p.stat().st_ctime),
#                 update_date = datetime.datetime.fromtimestamp(p.stat().st_mtime),
#                 parent = parent_category,
#                 path = filePath
#             )
#             child_category.update_note()
#             continue
#         with open(filePath) as f:
#             content = f.read()
#         Article.objects.create(
#             name = name.replace(".html",""),
#             title = name,
#             type = "NOT",
#             created_date = datetime.datetime.fromtimestamp(p.stat().st_ctime),
#             update_date = datetime.datetime.fromtimestamp(p.stat().st_mtime),
#             parent =  parent_category,
#             content = content
#         )