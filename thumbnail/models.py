
from django.db import models

import os,re,sys
import imagesize

from youtube.models import Video,Playlist

# ユーティリティ
import util.normalize as normalize
import util.text_transform as text_transform
import util.file_transform as file_transform

import codecs,shutil,subprocess
from django.utils import timezone
import  util.list_edit as list_edit

THUMBNAIL_DIR = "./thumbnail/thumbnails"
TEMPLATE_PATH = THUMBNAIL_DIR + "/templates/texs/thumbnail_template.tex"
BACKGROUND_IMAGE_DIR = THUMBNAIL_DIR + "/templates/smart_background"

class Thumbnail(models.Model):
    tex_text = models.TextField(null = True)
    youtube_video = models.ForeignKey(Video,null=True, on_delete = models.SET_NULL)

class ThumbnailContent(models.Model):
    youtube_video = models.ForeignKey(Video,null=True, on_delete = models.CASCADE)
    tex_text = models.TextField(null = True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "「%s」のサムネイル" % self.youtube_video.title()

    def make_raw_text(self):
        video = self.youtube_video
        point_text = video.extract_item("要点")
        if point_text :
            return point_text
        problem_text = video.extract_item("問題")
        if problem_text:
            return problem_text
        return video.title()
    
    def title_in_mytex(self):
        video = self.youtube_video
        return video.title_in_mytex()
        
    def make_tex_page_from_description(self):
        genre_mark = self.genre_mark()
        background_image = self.background_image()
        text = self.make_tex_text_from_description()
        return background_image+genre_mark+text
    
    def background_image(self):
        image_path = self.background_image_path()
        width, height = imagesize.get(image_path)
        return "\n\n\\at(0cm,0cm){\\includegraphics[width=8cm,bb=0 0 %s %s]{%s}}\n" % (width, height,image_path)
    
    def genre_mark(self):
        video = self.youtube_video
        type = video.video_type()
        genre = video.video_genre()
        genre_name = genre.name.replace("数III","数Ⅲ").replace("数II","数Ⅱ").replace("数I","数Ｉ").replace("数A","数Ａ").replace("数B","数Ｂ")
        xpos_list = [7.2,7.2,7.2,7.2,7.0,6.8,6.6,6.4,6.2,6.0]
        xpos = xpos_list[len(genre_name)]
        return "\\at(%scm,0.2cm){\\small\\color{%s}$\\overset{\\text{%s}}{\\text{%s}}$}\n" % (xpos,"bradorange",genre_name,type)
    
    def make_tex_text_from_description(self):
        text = self.make_raw_text()
        text = text_transform.text_to_tex(text)
        text = text_transform.take_linebraek_if_list(text)
        text = text_transform.make_math_line(text)
        text = text_transform.make_array(text)
        text = text_transform.tex_to_mytex(text)
        video_title = self.title_in_mytex()
        title_size = self.calc_title_size_name()
        text_size = self.calc_text_size_name()
        return "{\\color{orange}%s\\underline{%s}}\\vspace{0.3zw}\n\n%s \n問．%s\n" % (title_size,video_title,text_size,text)
    
    def background_image_path(self):
        video_genre = self.youtube_video.video_genre()
        if not video_genre:
            return ""
        image_path = "%s/%s.jpeg" % (BACKGROUND_IMAGE_DIR,video_genre)
        if os.path.isfile(image_path):
            return image_path
        return "%s/黒板風.jpeg" % BACKGROUND_IMAGE_DIR
    
    def calc_evaluation(self,text:str):
        if not text: return 0
        zenkaku_num = len(re.findall("[ぁ-んァ-ヶ一-龠々ー〜．，\+「 」αβγ]",text))
        hankaku_num = len(re.findall("[a-zA-Z\.\s\-\(\)\=\,0-9\|\<\>]",text))
        linesep_num = len(re.findall("\n",text))
        frac_num = len(re.findall("/",text))
        evaluation = zenkaku_num + hankaku_num*2/3 + linesep_num*8 +  frac_num*5
        return evaluation
    
    def calc_text_size_name(self):
        raw_text = self.make_raw_text()
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
    
    def set_on_youtube(self):
        video = self.youtube_video
        path = self.jpeg_with_videoId(video)
        if not os.path.isfile(path):
            input("次のファイルが見つかりません:%s" % path)
        response = youtube_with_auth.thumbnails().set(
            videoId=video.videoId(),
            media_body=path
        ).execute()
        print("ビデオ「%s」が更新されました：\n%s" % (video,response))

class ThumbnailUpdateSet(models.Model):
    name = models.CharField(max_length=50)
    videos = models.ManyToManyField(Video)

    def __str__(self):
        return self.name
    
    def main_dir(self): return THUMBNAIL_DIR + "/" +self.name
    
    def texs_dir(self): return self.main_dir() + "/texs"
    def jpegs_dir(self): return self.main_dir() + "/jpegs"
    def texfile_path(self):return self.texs_dir() + "/thumbnails.tex"
    
    def old_texfile_path(self):
        return THUMBNAIL_DIR + f"/old_texs/thumbnail_{self}.tex"
    
    def pdf_path(self): return self.texs_dir()+ "/thumbnails.pdf"
    
    def jpeg_path(self):
        return self.jpegs_dir() + "/thumbnails.jpeg"
    
    def jpeg_with_num_path(self,i):
        return self.jpegs_dir() + f"/thumbnails{i}-%s.jpeg" 
    
    def jpeg_with_videoId(self,video:Video):
        return self.jpegs_dir() + f"/{video.videoId()}.jpeg"

    def make_from_playlist(self,playlist:Playlist):
        items = playlist.playlistItems()
        video_set = ThumbnailUpdateSet.objects.create(name = playlist.title().replace(" ","_"))
        for item in items:
            video_set.videos.add(item.video())
        return video_set
    
    def join(self,video_sets,set_name:str):
        new_video_set = ThumbnailUpdateSet.objects.create(name = set_name)
        for video_set in video_sets:
            new_video_set.videos.add(*video_set.videos.all())
        return new_video_set
    
    def make_dirs(self):
        os.makedirs(self.texs_dir(), exist_ok=True)
        os.makedirs(self.jpegs_dir(), exist_ok=True)
    
    def make_texfile(self):
        videos = self.videos.all()
        content_texts = []
        for video in videos:
            try:
                thumbnail = ThumbnailContent.objects.filter(youtube_video=video).last()
                text = thumbnail.tex_text.replace("./thumbnails",THUMBNAIL_DIR)
                content_texts.append(text)
                print("「%s」は保存されたデータを使用します" % video)
            except:
                thumbnail = ThumbnailContent(youtube_video=video)
                content_texts.append(thumbnail.make_tex_page_from_description())
                print("「%s」はdescriptionから抽出します" % video)
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
        t = re.search("\\\\begin\{document\}([\S\s]*?)\\\\end\{document\}",all_text)
        document_text = normalize.clean_up_lines(t[0])
        texts = re.split("\n*\\\\newpage\n*",document_text)
        
        videos = self.videos.all()
        if not len(texts)==len(videos):
            input("「%s」はold_tex(%s)とplaylist(%s)の問題数が一致しません．" % (self,len(texts),len(videos)))
            sys.exit()
        for i,video in enumerate(videos):
            old_thumbnails = ThumbnailContent.objects.filter(youtube_video=video)
            if old_thumbnails:
                old_thumbnails.delete()
                print("サムネイルデータを上書きしました")
                continue
            thumbnail = ThumbnailContent.objects.create(youtube_video=video, tex_text=texts[i])
            print("%sを再利用可能データとして新規登録しました" % thumbnail)

    def back_up(self):
        print("VideoSet「%s」のバックアップファイルを作成しました" % self)
        shutil.copytree(self.main_dir(), THUMBNAIL_DIR + '/saved_sets/%s_%s' % (self,timezone.now()))

    def save_each_data_form_old_texfile(self):
        content_path = self.old_texfile_path()
        f = codecs.open(content_path, 'r','utf-8')#  % timezone.now()
        all_text = f.read()
        t = re.findall("\\\\begin\{document\}([\S\s]*?)\\\\end\{document\}",all_text)
        document_text = t[0]
        document_text = normalize.clean_up_lines(document_text)
        texts = re.split("\n*\\\\newpage\n*",document_text)
        videos = self.videos.all()
        if not len(texts)==len(videos):
            input("「%s」はold_tex(%s)とplaylist(%s)の問題数が一致しません．" % (self,len(texts),len(videos)))
        for i,video in enumerate(videos):
            text =texts[i].replace("./media_local",f"{THUMBNAIL_DIR}/templates")
            # if input("%s\n 上記を「%s」ののサムネイルTeXとして、保存していいですか？y/n\n:" % (text,video))=="n":return
            thumbnail = ThumbnailContent.objects.create(youtube_video=video,tex_text =  text)
            print("%sを個別データとして保存しました" % thumbnail)

    def ptex2pdf(self):
        dir = "./youtube/thumbnails/%s/texs" % self
        tex_path = self.texfile_path()
        file_transform.ptex2pdf(tex_path,dir)

    def open_pdf(self):
        subprocess.Popen(["open", "-a", "Preview.app",  self.pdf_path()])

    def pdf2jpeg(self):
        file_transform.pdf2jpeg(self.pdf_path(),self.jpeg_path())
        for i,video in enumerate(self.videos.all()):
            old_file_path = self.jpeg_with_num_path(i)
            new_file_path = self.jpeg_with_videoId(video)
            os.rename(old_file_path,new_file_path)

    def set_on_youtube(self):
        for video in self.videos.all():
            thumbnail = ThumbnailContent.objects.get(youtube_video = video)
            thumbnail.set_on_youtube()

    def redownload(self):
        for video in self.videos.all():
            video.download()



    def create_all_video_set_list(self,max_num):
        video_list = [thumbnail.youtube_video for thumbnail in ThumbnailContent.objects.all()]
        video_set_list = []
        for i,video_list in enumerate(list_edit.split_with_max_number(video_list,max_num)):
            video_set = ThumbnailUpdateSet.objects.create(name = "all_thumbnail-%s" % i)
            video_set.videos.add(*video_list)
            video_set_list.append(video_set)
        return video_set_list
    
    def create_from_keyword(self,keyword:str):
        playlists = Playlist.objects.filter(data__snippet__title__icontains = keyword)
        if not playlists:
            sys.exit()
        video_sets = [ThumbnailUpdateSet().make_from_playlist(playlist) for playlist in playlists]
        file_name = keyword.replace(" ","_")
        return ThumbnailUpdateSet().join(video_sets,file_name)
    
