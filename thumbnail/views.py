from django.shortcuts import render

from .models import ThumbnailContent,ThumbnailUpdateSet,Thumbnail

class ThumbnailGenerator:
    def generate(self,video_set:ThumbnailUpdateSet):
        video_set.make_dirs() # 初めてセットを作った時だけ必要
        # video_set.redownload() # Youtubeにある最新の状態を反映したいときだけONに
        video_set.make_texfile() # すでに保存されているThumbnailモデルがなければ、Video.dataから生成する。texfileを手動で編集するときはOFFにする。
        # video_set.ptex2pdf() 
        # video_set.open_pdf() # ビューワーで見たい時だけONにするとスムーズ。

        # video_set.pdf2jpeg() # 少し時間がかかります。
        # video_set.set_on_youtube() # youtube_with_auth が必要
        # video_set.save_each_data_form_texfile() # Thumbnailモデルとして保存する。
        # video_set.back_up() # saved_setsディレクトリに保存。復元するメソッドはまだない。

    def all_video(self):
        for video_set in  ThumbnailUpdateSet().create_all_video_set_list(1000):
            self.generate(video_set)

    def by_keyword(self,keyword:str):
        self.generate(ThumbnailUpdateSet().create_from_keyword(keyword))

    def save_thumbnails(self):
        for content in ThumbnailContent.objects.all():
            Thumbnail.objects.create(
                youtube_video = content.youtube_video,
                tex_text=content.tex_text
            )


# ThumbnailGenerator().by_keyword("典型")
# ThumbnailGenerator().all_video()
# ThumbnailGenerator().save_thumbnails()




def display_status():
    print("Thumbnailの個数: %s" % len(Thumbnail.objects.all()))
    print("ThumbnailContentの個数: %s" % len(ThumbnailContent.objects.all()))

display_status()