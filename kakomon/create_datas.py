from django.db import models

from django.utils import timezone
from django.contrib import admin

import os

from ugosite.models import Print,Problem
from printviewer.models import Folder,Print

from ugosite.create_datas import MEDIA_LOCAL_PATH
KAKOMON_PATH = f'{MEDIA_LOCAL_PATH}/旧帝大過去問'

class TeXYearFolderOfKakomon:
    def __init__(self,path:str):
        self.path = path
        
    def create_print(self,parent_folder:Folder):
        kakomon_print,created = Print.objects.get_or_create(
            name = "%s %s" % (parent_folder.name,os.path.basename(self.path)),
            parent_folder = parent_folder
        )
        if created:print(f"Folder「{parent_folder}」内にPrint「{kakomon_print}」をcreateしました．")
        for file in sorted(os.listdir(self.path)):
            if not file.endswith('.tex'):continue
            problem = TeXFileOfKakomon("%s/%s" % (self.path,file)).make_from_kakomon_texfile(kakomon_print)
            problem.prints.add(kakomon_print)
        
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
    
    def create_univ_folder(self,folder:Folder):
        univ_folder,created = Folder.objects.get_or_create(
            name = self.univ_name(),
            parent_folder = folder,
        )
        if created:print(f"Folder「{folder}」Folder「{univ_folder}」をcreateしました．")
        return univ_folder
        
    def create_prints(self,folder:Folder):
        for year in sorted(os.listdir(self.path)):
            if year.startswith('.'):continue
            TeXYearFolderOfKakomon(f"{self.path}/{year}").create_print(folder)
            
            
import re,codecs,sys


# ユーティリティ
import util.text_transform as text_transform
            
class TeXFileOfKakomon:
    def __init__(self,path:str):
        self.path = path
        
    def name(self):
        return os.path.basename(self.path)
    
    def make_from_kakomon_texfile(self,kakomon_print:Print):
        with codecs.open(self.path, 'r', encoding='shift_jis') as f:
            text = f.read()
        t = re.findall("{\\\\huge\s\d.*}\r\n([\s\S]*?)\\\\end{flushleft}",text)
        if not t:
            print(text)
            sys.exit()
        atricleName = kakomon_print.name
        num =  re.findall("_(\w+).tex",os.path.basename(self.path))[0]
        if re.match("\d_\d",num):
            division = "文"
            num = num[2:]
        else:
            division = "理"
        text = t[0]
        text = text.replace("<","&lt;").replace(">","&gt;")
        text = text.replace("\r","")
        text = text_transform.itemize_to_ol(text)
        text = text_transform.item_to_li(text)
        # print(text)
        text = re.sub("\\\\hspace{\dzw}","",text)
        text = text.replace("\\hspace{1zw}","~").replace('\\ding{"AC}',"&#9312;").replace('\\ding{"AD}',"&#9313;").replace('\\ding{"AE}',"&#9314;")
        text = re.sub("\$([\s\S]+?)\$"," $\\1$ ",text)
        text = text.replace("$ ，","$，")
        text = text.replace("\\\\","<br>")
        name = "%s %s系 第%s問" % (atricleName,division,num)
        problem,created = Problem.objects.get_or_create(
            name = name,
            source = name,
            text = text
        )
        if created: print(f"Problem「{problem}」をcreateしました．")
        return problem

def create_form_kakomon_files():
        
    parent_folder,created = Folder.objects.get_or_create(name = "大学別62年過去問題集")
    if created: print(f"Folder「{parent_folder}」をcreateしました．")
    
    for univ in sorted(os.listdir(KAKOMON_PATH)):
        if univ.startswith('.'): continue
        tex_univ_folder = TeXUnivFolderOfKakomon("%s/%s" % (KAKOMON_PATH,univ))
        univ_folder = tex_univ_folder.create_univ_folder(parent_folder)
        tex_univ_folder.create_prints(univ_folder)
            