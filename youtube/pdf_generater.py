
    
from django.utils import timezone
from youtube.models import Video, ChannelSection
import subprocess


TEMPLATE_PATH = './notes/texs/templates/youtube_video_problems.tex'
CONTENT_PATH =  "./notes/texs/youtube_video_problems.tex"

class PDFGenerater:
    def make_texfile(self):
        sections = ChannelSection.objects.filter(data__snippet__type = "multipleplaylists")
        texts = []
        for section in sections:
            section_title = section.title()
            texts.append("\\section{%s}" % section_title)
            playlists = section.playlists()
            for playlist in playlists:
                playlist_title = playlist.title()
                texts.append("\\subsection{%s}" % playlist_title)
                items = playlist.playlistItems()
                for item in items:
                    video = item.video()
                    if not video:continue
                    text = self.to_tex(video)
                    texts.append(text)
                    # texts.append("\\newpage")
        t = open(TEMPLATE_PATH, 'r')
        template_text = t.read()
        f = open(CONTENT_PATH, 'w')#  % timezone.now()
        file_text = template_text.replace("{{template}}","\n\n".join(texts))
        f.write(file_text)
        f.close()

    def to_tex(self,video:Video):
        video_title = video.title()
        problem_text = video.extract_item("問題")
        if not problem_text:return ""
        text = """\n\n\\begin{question}{\\bf\\boldmath %s}\\\\\n%s\n\\end{question}""" % (video_title,problem_text)    
        return text