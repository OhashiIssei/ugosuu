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
            
            
            
FROM_MYTEX_DESCRIPTION_TO_JAX = [["\r",""]]
FROM_MYTEX_DESCRIPTION_TO_JAX += [["<","&lt;"],[">","&gt;"],["\\bunsuu","\\displaystyle\\frac"],["\\dlim","\\displaystyle\\lim"],["\\dsum","\\displaystyle\\sum"]]
FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\vv","\\overrightarrow"],["\\bekutoru","\\overrightarrow"],["\\doo","^{\\circ}"],["\\C","^{\\text{C}}"]]
FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\barr","\\left\\{\\begin{array}{l}"],["\\earr","\\end{array}\\right."]]
FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\PP","^{\\text{P}}"],["\\QQ","^{\\text{Q}}"],["\\RR","^{\\text{R}}"]]
FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\NEN","\\class{arrow-pp}{}"],["\\NEE","\\class{arrow-pm}{}"],["\\SES","\\class{arrow-mm}{}"],["\\SEE","\\class{arrow-mp}{}"]]
FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\NE","&#x2197;"],["\\SE","&#x2198;"],["\\xlongrightarrow","\\xrightarrow"]]
FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\hfill □","<p class = 'end'>□</p>"]]
FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\bf\\boldmath", "\\bb"],["\n}\n","\n"],["\\bf", "\\bb"]]
FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\newpage",""],["\\iffigure",""],["\\fi",""],["\\ifkaisetu",""],["\\begin{mawarikomi}{}{",""],["\\end{mawarikomi}",""],["\\vfill",""],["\\Large",""]]
FROM_MYTEX_DESCRIPTION_TO_JAX += [["normalsize",""],["\\large",""],["\\Large",""],["\\LARGE",""],["\\huge",""],["\\Huge",""]]
FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\bf",""],["\\bb",""],["\\boldmath",""]]
FROM_MYTEX_DESCRIPTION_TO_JAX += [["bquu","bqu"],["equu","equ"],["bQ","bqu"],["eQ","equ"]]
for j in range(10):
    FROM_MYTEX_DESCRIPTION_TO_JAX += [["\\MARU{%s}" % str(j),str("&#931%s;" % str(j+1))]]
    

KOUSIKANKEI_PATH = '/Users/greenman/Library/Mobile Documents/com~apple~CloudDocs/講師関係'

class MyTeXFolder:
    def __init__(self,path:str):
        self.path = path
        
    def create_from_my_dir(self,parent_category:Category):
        print("%sを読み込む" % self.path)
        category_name = os.path.basename(self.path)
        child_category = Category.objects.create(
            name = category_name,
            parent = parent_category
        )
        for base_name in os.listdir(self.path):
            path = "%s/%s" % (self.path,base_name)
            if base_name.startswith('.'): continue
            if "阪大" in base_name: continue
            if "旧帝大" in base_name: continue
            if "まとめ" in base_name: continue
            if base_name.endswith(".tex"):
                texfile = MyTeXFile(path)
                if not texfile.has_problem():continue
                texfile.create_model(child_category)
                continue
            if os.path.isdir(path):
                my_tex_folder = MyTeXFolder(path)
                my_tex_folder.create_from_my_dir(child_category)
                continue
        if not child_category.children():
            child_category.delete()
        
    

class MyTeXFile:
    def __init__(self,path:str):
        self.path = path
        
    def name(self):
        return os.path.basename(self.path).replace(".tex","")
        
    def content_text(self):
        with open(self.path) as f:
            text = f.read()
        text = normalize.clean_up_lines(text)
        text = re.sub("\%.*?\n","",text)
        s = re.search("\\\\begin{document}(.*\n)*\\\\end{document}",text)
        if not s: return TextOfMyTeX("")
        text = s.group()
        return TextOfMyTeX(text)
    
    def has_problem(self):
        my_tex = self.content_text()
        my_tex = my_tex.replace("bquu","bqu").replace("bQ","bqu").replace("begin{question}","bqu")
        return my_tex.match_in_regular_expression("\\\\bqu")
    
    def subsections_num(self):
        return self.content_text().finded_num_in_regular_expression("\\\\sub")
    
    def create_model(self,parent_category:Category):
        if self.subsections_num()<2:
            my_text = TextOfOneArticleInMyTeX(self.content_text().translate_to_jax())
            new_article = my_text.create_model(parent_category)
            new_article.name = self.name()
            new_article.save()
            print("new Article: %s (parent: %s)" % (new_article,new_article.parent))
            return new_article
        self.create_category(parent_category)
        
    def create_category(self,parent_category:Category):
        child_category = Category.objects.create(
            name = self.name(),
            parent =  parent_category
        )
        self.create_subarticles(child_category)
        
    def create_subarticles(self,category:Category):
        text_in_jax = self.content_text().translate_to_jax().replace("\\sub{","\\subsection{")
        subsections = re.split("\n\\\\subsection",text_in_jax)
        
        for subsection_text in subsections[1:]:
            aticle_text = TextOfOneArticleInMyTeX(subsection_text)
            article = aticle_text.create_model(category)
            print("new Article: %s (parent: %s)" % (article,article.parent))
        return category
    
class TextOfMyTeX:
    def __init__(self,text:str):
        self.text = text
        
    def translate_to_jax(self):
        result = self.text
        for r in FROM_MYTEX_DESCRIPTION_TO_JAX:
            result = result.replace(r[0],r[1])
        result = re.sub("\\\\sq([^r])","\\\\sqrt\\1",result)
        return result
    
    def test_translate_to_jax():
        test_input = "\\sq3+\\sqrt3+\\sq{3}+\\sqrt{3}"
        test_output = TextOfMyTeX(test_input).translate_to_jax()
        correct_output = "\\sqrt3+\\sqrt3+\\sqrt{3}+\\sqrt{3}"
        if correct_output == test_output:
            print("text_in_jax:OK")
            return
        input(f"text_in_jax\n:{test_input}\n→{test_output}\n⇄{correct_output}")
        
    def replace(self,target_string:str,replace_string:str):
        return TextOfMyTeX(self.text.replace(target_string,replace_string))
    
    def match_in_regular_expression(self,regular_expression:str):
        m = re.findall(regular_expression,self.text)
        if m:return True
        return False
    
    def finded_num_in_regular_expression(self,regular_expression:str):
        return len(re.findall(regular_expression,self.text))

class TextOfOneArticleInMyTeX:
    def __init__(self,text:str):
        self.text = text
        
    def make_name(self,category:Category):
        n = re.findall("^\{\s*([\S]*?)[\s\}\n]",self.text)
        if n:return n[0]
        # input(self.text[:50])
        return  "%s %s" % (category,len(category.children())+1)
                
    def create_model(self,parent_category:Category):
        name = self.make_name(parent_category)
        article = Article.objects.create(
            name = name,
            parent = parent_category
            )
        questions = re.findall("\\\\bqu((?:.*?\n)*?)\\\\equ",self.text)
        for text in questions:
            TextOfOneProblemInMyTeX(text).create_model(article)
        return article

class TextOfOneProblemInMyTeX:
    def __init__(self,text:str):
        self.text = text
        
    def main_text(self):
        result = self.text
        result = text_transform.transform_dint(result,"{","}")
        result = re.sub("%+[^\n]*\n","\n",result)
        result = text_transform.itemize_to_ol(result)
        result = text_transform.item_to_li(result)
        result = re.sub("\$([\s\S]+?)\$"," $\\1$ ",result)
        result = re.sub("\\\\vspace{.*?}","",result)
        
        result = re.sub("^\s*\{.+\}.*\n","",result)
        result = re.sub("\\\\hfill\((.*)\)","",result)
        result = re.sub("\\\\hfill","",result)
        result = re.sub("\n\\\\begin{解答[\d]*}[^\n]*\n([\s\S]+?)\\\\end{解答[\d]*}","",result)
        
        # result = result.replace("\\\\","\n")
        result = result.replace("\\ "," ")
        return result
    
    def test_main_text():
        test_self = TextOfOneProblemInMyTeX("$\sum_{k=1}k^2$")
        test_output = test_self.main_text()
        correct_output = " $\sum_{k=1}k^2$ "
        if correct_output==test_output:
            print("problem_text:OK")
            return 
        input("problem_text\n:%s\n→%s\n⇄%s" % (test_self.text,test_output,correct_output))
            
    def name(self,article:Article):
        names = re.findall("^[\s]*\{[\s]*(.+)\}",self.text)
        if names:return names[0].replace("\\fi","").replace("\\ifkaisetu","")
        num_in_article = article.problem_set.count()+1
        return "%s 問題%s" % (article.name,num_in_article)
        
    def source(self):
        sources = re.findall("\\\\hfill\((.*)\)",self.text)
        if sources:return sources[0]
        return ""
        
    def answer(self):
        answers = re.findall("\n\\\\begin\{解答[\d]*\}[^\n]*\n([\s\S]+?)\\\\end\{解答[\d]*\}",self.text)
        if answers:return answers[0]
        return ""
    
    def link(self):
        links = re.findall("\\\\fbox\{\\\\qrcode\[.*\]\{(.*)\}\}",self.text)
        if links:return links[0]
        return ""
    
    def create_model(self,article:Article):
        return Problem.objects.create(
            name = self.name(article),
            text = self.main_text(),
            source = self.source(),
            answer = self.answer(),
            link = self.link()
        ).articles.add(article)
    
    
def create_from_my_texfiles():
    TextOfMyTeX.test_translate_to_jax()
    TextOfOneProblemInMyTeX.test_main_text()
    
    Category.objects.filter(name = "講師関係").delete()
    MyTeXFolder(KOUSIKANKEI_PATH).create_from_my_dir(None)


KAKOMON_PATH = '/Users/greenman/Library/Mobile Documents/com~apple~CloudDocs/旧帝大過去問'

class TeXYearFolderOfKakomon:
    def __init__(self,path:str):
        self.path = path
        
    def create_article(self,parent_category:Category):
        article = Article.objects.create(
            name = "%s %s" % (parent_category.name,os.path.basename(self.path)),
            type = "TER",
            path = self.path,
            parent = parent_category
        )
        for file in sorted(os.listdir(self.path)):
            if not file.endswith('.tex'):continue
            problem = Problem().make_from_kakomon_texfile("%s/%s" % (self.path,file))
            problem.articles.add(article)
        print("new Article: %s (parent: %s)" % (article,article.parent))
        
class TeXUnivFolderOfKakomon:
    def __init__(self,path:str):
        self.path = path
        
    def name(self):
        return os.path.basename(self.path)
    
    def univ_name(self):
        result = self.name()[3:]
        for r in [["hokudai","北大"],["kyoto","京大"],["tokyo","東大"],["kyushu","九大"],["nagoya","名大"],["osaka","阪大"],["titech","東工大"],["tohoku","東北大"]]:
            result = result.replace(r[0],r[1])
        return result
    
    def create_univ_category(self,category:Category):
        univ_category = Category.objects.create(
            name = self.univ_name(),
            type = "TER",
            parent = category,
        )
        print("new Category: %s (parent: %s)" % (univ_category,univ_category.parent))
        return univ_category
        
    def create_artcles(self,category:Category):
        for year in sorted(os.listdir(self.path)):
            if year.startswith('.'):continue
            TeXYearFolderOfKakomon(f"{self.path}/{year}").create_article(category)

def create_form_kakomon_files():
        
    parent_category = Category.objects.create(name = "大学別62年過去問題集")
    
    for univ in sorted(os.listdir(KAKOMON_PATH)):
        if univ.startswith('.'): continue
        univ_folder = TeXUnivFolderOfKakomon("%s/%s" % (KAKOMON_PATH,univ))
        univ_category = univ_folder.create_univ_category(parent_category)
        univ_folder.create_artcles(univ_category)
            
    

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