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

from .models import Subject,Chapter,Section,Subsection

import util.text_transform as text_transform
from ugosite.models import Problem

MEDIA_LOCAL_PATH = "/Users/greenman/local_django_projects/ugosuu/media_local"

class TitleOfFourStep:
    def __init__(self,text:str):
        self.text = text.replace("　"," ")
        
    def type_of_article(self):
        if re.match("[０-９]\s|1[0-9]\s",self.text): return "BAS"
        if re.match("研究\s",self.text): return "STU"
        if re.match("発展\s",self.text): return  "DEV"
        if re.match("補\s",self.text): return "SUP"
        # if re.search("演習問題",self.text) : return "PRA"
        return ""
        
    def name_of_category(self):
        result = self.text
        result = re.sub("\s(\w)\s(\w)$"," \\1\\2",result)
        result = re.sub("(^第[０-９]章\s)","",result)
        result = re.sub("(^第[0-9]章\s)","",result)
        result = re.sub("(^第[０-９]節\s)","",result)
        result = re.sub("(^[０-９]\s)","",result)
        result = re.sub("(^研究\s)","",result)
        result = re.sub("(^補\s)","",result)
        result = re.sub("(^発展\s)","",result)
        return result
        
    def is_article_title(self):
        if self.type_of_article():return True
        return False
    
    def is_chapter_title(self):
        if re.match("第[０-９]章",self.text):return True
        return False
    
    def is_section_title(self):
        if re.match("第[０-９]節",self.text):return True
        return False
    
    def create_model(self):
        if self.is_chapter_title():
            chapter,created = Chapter.objects.get_or_create(
                name = self.name_of_category(),
                subject = Subject.objects.last()
            )
            if created:print(f"Chapter「{chapter}」をgetしました")
            else:print(f"Chapter「{chapter}」をcreateしました")
        if self.is_section_title():
            section,created = Section.objects.get_or_create(
                name = self.name_of_category(),
                chapter = Chapter.objects.last()
            )
            if created:print(f"Section「{section}」をgetしました")
            else:print(f"Section「{section}」をcreateしました")
        if self.is_article_title():
            article,created = Article.objects.get_or_create(
                name = self.text,
                section = Section.objects.last()
            )
            if created:print(f"Article「{article}」をgetしました")
            else:print(f"Article「{article}」をcreateしました")
        

FOUR_STEP_PATH =  f"{MEDIA_LOCAL_PATH}/four_step"

FOUR_STEP_DATA = [
    ["I","k4step_b1a.xlsx",0],
    ["A",'k4step_b1a.xlsx',1],
    ["II",'k4step_b2b.xlsx',0],
    ["B",'k4step_b2b.xlsx',1],
    ["III",'k4step_b3.xlsx',0]
]

def create_categories_form_four_step():
        
    def create_categorys_and_articles(worksheet):
        for i in range(1000):
            if i <3 : continue
            cell = worksheet.cell(i,2)
            cell_value = cell.value
            if not cell_value : continue
            TitleOfFourStep(cell_value).create_model()
    
    category,created = Category.objects.get_or_create(name = "高校数学")
    if created:print(f"Category「{category}」をgetしました")
    else:print(f"Category「{category}」をcreateしました")
    for data in FOUR_STEP_DATA:
        subject,created = Subject.objects.get_or_create(
            name = "数学%s" % data[0],
            category = category,
        )
        if created:print(f"Subject「{subject}」をgetしました")
        else:print(f"Subject「{subject}」をcreateしました")
        excel_file_path = '%s/%s' % (FOUR_STEP_PATH,data[1])
        loaded_workbook = openpyxl.load_workbook(excel_file_path)
        worksheet = loaded_workbook.worksheets[data[2]]
        create_categorys_and_articles(worksheet)
            
        
            
    

# ICONS_PATH =  "/Users/greenman/Desktop/web-projects/django_projects/ugosite/media_local/icons"

# def update_icons():
#     for file_name in os.listdir(ICONS_PATH):
#         if not ".svg" in file_name:continue
#         svgPath = "%s/%s" % (ICONS_PATH,file_name)
#         name = file_name.replace(".svg","")
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