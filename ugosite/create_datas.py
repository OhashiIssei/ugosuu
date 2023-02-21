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

import util.text_transform as text_transform
from ugosite.models import Problem

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

class MyTeXfile:
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
        text = s.group().replace("\\sub{","\\subsection{")
        return TextOfMyTeX(text)
    
    def has_problem(self):
        my_tex = self.content_text()
        my_tex = my_tex.replace("bquu","bqu").replace("bQ","bqu").replace("begin{question}","bqu")
        return my_tex.has_in_regular_expression("\\\\bqu((?:.*\n)*?)\\\\equ")
    
    def subsections_num(self):
        return self.content_text().finded_num_in_regular_expression("\\\\sub")
    
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
    
    def has_in_regular_expression(self,regular_expression:str):
        if re.match(regular_expression,self.text):return True
        return False
    
    def finded_num_in_regular_expression(self,regular_expression:str):
        return len(re.findall(regular_expression,self.text))
        
TextOfMyTeX.test_translate_to_jax()

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
        result = result.replace("\\hfill","")
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
        return "%s 問題%s" % (article,num_in_article)
        
    def source(self):
        sources = re.findall("\\\\hfill\((.*)\)",self.text)
        if sources:return sources[0]
        return ""
        
    def answer(self):
        answers = re.findall("\n\\\\begin\{解答[\d]*\}[^\n]*\n([\s\S]+?)\\\\end\{解答[\d]*\}",self.text)
        if answers:return answers[0]
        return ""
    
    def create_model(self,article:Article):
        return Problem.objects.create(
            name = self.name(article),
            text = self.main_text(),
            source = self.source(),
            answer =  self.answer()
        ).articles.add(article)
    
TextOfOneProblemInMyTeX.test_main_text()

def create_from_my_texfiles():
    
    ### category
    
    def create_from_my_dir(dir_path:str,parent_category:Category):
        print("%sを読み込む" % dir_path)
        category_name = os.path.basename(dir_path)
        child_category = Category.objects.create(
            name = category_name,
            parent = parent_category
        )
        for base_name in os.listdir(dir_path):
            path = "%s/%s" % (dir_path,base_name)
            if base_name.startswith('.'): continue
            if "阪大" in base_name: continue
            if "旧帝大" in base_name: continue
            if "まとめ" in base_name: continue
            if base_name.endswith(".tex"):
                texfile = MyTeXfile(path)
                if texfile.has_problem():continue
                create_from_my_texfile(texfile,child_category)
                continue
            if os.path.isdir(path):
                create_from_my_dir(path,child_category)
                continue
        if not child_category.children():
            child_category.delete()
    
    ### article or category
    
    def create_from_my_texfile(texfile:MyTeXfile,parent_category:Category):
        
        if texfile.subsections_num()<2:
            article_name = texfile.name()
            text = texfile.content_text().translate_to_jax()
            new_article = make_article_with_problem(article_name,text,parent_category)
            print("new Article: %s (parent: %s)" % (new_article,new_article.parent))
            return new_article
        
        child_category = Category.objects.create(
            name = texfile.name(),
            parent =  parent_category
        )
        text_in_jax = texfile.content_text().translate_to_jax()
        subsections = re.split("\n\\\\subsection",text_in_jax)
        for text in subsections[1:]:
            article_name = make_name_of_article(text,child_category)
            article = make_article_with_problem(article_name,text,child_category)
            print("new Article: %s (parent: %s)" % (article,article.parent))
        return child_category
        
            
    def make_name_of_article(text:str,category:Category):
        n = re.findall("^\{\s*([\S]*?)[\s\}\n]",text)
        if n:return n[0]
        input(text[:50])
        return  "%s %s" % (category,len(category.children())+1)
                
    def make_article_with_problem(name:str,article_text:str,parent_category:Category):
        article = Article.objects.create(
            name = name,
            parent = parent_category
            )
        questions = re.findall("\\\\bqu((?:.*?\n)*?)\\\\equ",article_text)
        for text in questions:
            problem_in_my_tex = TextOfOneProblemInMyTeX(text)
            problem_in_my_tex.create_model(article)
        return article
    
    Category.objects.filter(name = "講師関係").delete()
    create_from_my_dir(KOUSIKANKEI_PATH,None)


KAKOMON_PATH = '/Users/greenman/Library/Mobile Documents/com~apple~CloudDocs/旧帝大過去問'

def create_form_kakomon_files():
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