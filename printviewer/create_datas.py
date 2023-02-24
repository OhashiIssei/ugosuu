from django.db import models

from django.utils import timezone
from django.contrib import admin

import os

import openpyxl

import re

# ユーティリティ
import util.normalize as normalize

from .models import Folder,Print

import util.text_transform as text_transform
from ugosite.models import Problem

MEDIA_LOCAL_PATH = "/Users/greenman/local_django_projects/ugosuu/media_local"
            
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
        
    def create_from_my_dir(self,parent_folder:Folder):
        print("%sを読み込む" % self.path)
        category_name = os.path.basename(self.path)
        child_category = Folder.objects.create(
            name = category_name,
            parent_folder = parent_folder
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
    
    def create_model(self,parent_folder:Folder):
        if self.subsections_num()<2:
            my_text = TextOfOnePrintInMyTeX(self.content_text().translate_to_jax())
            new_print = my_text.create_model(parent_folder)
            new_print.name = self.name()
            new_print.save()
            print("new Print: %s (parent_folder: %s)" % (new_print,new_print.parent_folder))
            return new_print
        self.create_category(parent_folder)
        
    def create_category(self,parent_folder:Folder):
        child_category = Folder.objects.create(
            name = self.name(),
            parent_folder =  parent_folder
        )
        self.create_subprints(child_category)
        
    def create_subprints(self,category:Folder):
        text_in_jax = self.content_text().translate_to_jax().replace("\\sub{","\\subsection{")
        subsections = re.split("\n\\\\subsection",text_in_jax)
        
        for subsection_text in subsections[1:]:
            aticle_text = TextOfOnePrintInMyTeX(subsection_text)
            myprint = aticle_text.create_model(category)
            print("new Print: %s (parent_folder: %s)" % (myprint,myprint.parent_folder))
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

class TextOfOnePrintInMyTeX:
    def __init__(self,text:str):
        self.text = text
        
    def make_name(self,category:Folder):
        n = re.findall("^\{\s*([\S]*?)[\s\}\n]",self.text)
        if n:return n[0]
        # input(self.text[:50])
        return  "%s %s" % (category,len(category.children())+1)
                
    def create_model(self,parent_folder:Folder):
        name = self.make_name(parent_folder)
        print = Print.objects.create(
            name = name,
            parent_folder = parent_folder
            )
        questions = re.findall("\\\\bqu((?:.*?\n)*?)\\\\equ",self.text)
        for text in questions:
            TextOfOneProblemInMyTeX(text).create_model(print)
        return print

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
            
    def name(self,print:Print):
        names = re.findall("^[\s]*\{[\s]*(.+)\}",self.text)
        if names:return names[0].replace("\\fi","").replace("\\ifkaisetu","")
        num_in_print = print.problem_set.count()+1
        return "%s 問題%s" % (print.name,num_in_print)
        
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
    
    def create_model(self,print:Print):
        return Problem.objects.create(
            name = self.name(print),
            text = self.main_text(),
            source = self.source(),
            answer = self.answer(),
            link = self.link()
        ).prints.add(print)
    
    
def create_from_my_texfiles():
    TextOfMyTeX.test_translate_to_jax()
    TextOfOneProblemInMyTeX.test_main_text()
    
    Folder.objects.filter(name = "講師関係").delete()
    MyTeXFolder(KOUSIKANKEI_PATH).create_from_my_dir(None)