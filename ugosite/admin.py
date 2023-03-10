from django.contrib import admin


from .models import Category, Article, Problem, Term

class TermAdmin(admin.ModelAdmin):
    list_display = ('name','videos_num')

admin.site.register(Term, TermAdmin)


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id','name')

admin.site.register(Article, ArticleAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name')

admin.site.register(Category, CategoryAdmin)

class ProblemAdmin(admin.ModelAdmin):
    list_display = ('name' ,'text')

admin.site.register(Problem, ProblemAdmin)

# class ProblemsInline(admin.TabularInline):
#     model = Problem
    


from printviewer.models import Folder, Print

class PrintAdmin(admin.ModelAdmin):
    list_display = ('name' ,'parent_folder', 'description')
    # inlines = [ProblemsInline]

admin.site.register(Print, PrintAdmin)

class PrintsInline(admin.TabularInline):
    model = Print

class FolderAdmin(admin.ModelAdmin):
    list_display = ('name' ,'parent_folder', 'description')
    # inlines = [PrintsInline]

admin.site.register(Folder, FolderAdmin)




from youtube.models import Video,Playlist,PlaylistItem,ChannelSection

class VideoAdmin(admin.ModelAdmin):
    list_display = ('title','source','table_list','problem','point')

admin.site.register(Video, VideoAdmin)


class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('title','playlistId','description')

admin.site.register(Playlist, PlaylistAdmin)

class PlaylistItemAdmin(admin.ModelAdmin):
    list_display = ('playlist','position','video')
    # inlines = [ProblemsInline]

admin.site.register(PlaylistItem, PlaylistItemAdmin)

class ChannelSectionAdmin(admin.ModelAdmin):
    list_display = ('title','channelSectionId')
    # inlines = [ProblemsInline]

admin.site.register(ChannelSection, ChannelSectionAdmin)




from youtube.models import VideoType,VideoGenre

class VideoTypeAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    # inlines = [ProblemsInline]

admin.site.register(VideoType,VideoTypeAdmin)

class VideoGenreAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    # inlines = [ProblemsInline]

admin.site.register(VideoGenre,VideoGenreAdmin)




from video_search.models import VideoSearch

class VideoSearchAdmin(admin.ModelAdmin):
    list_display = ('id','keyword','display_video_types')
    # inlines = [ProblemsInline]

admin.site.register(VideoSearch, VideoSearchAdmin)

