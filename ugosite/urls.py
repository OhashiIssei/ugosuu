from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

urlpatterns += [
    path('article/<int:pk>', views.ArticleDetailView.as_view(), name='article-detail'),
    path('articles/', views.ArticleListView.as_view(), name='articles'),
]

urlpatterns += [
    path('term/<int:pk>', views.TermDetailView.as_view(), name='term-detail'),
    path('terms/', views.TermListView.as_view(), name='terms'),
]

urlpatterns += [
    path('category/<int:pk>', views.CategoryDetailView.as_view(), name='category-detail'),
    path('categorys/', views.CategoryListView.as_view(), name='categorys'),
]

urlpatterns += [
    path('problem/<int:pk>', views.ProblemDetailView.as_view(), name='problem-detail'),
    path('problems/', views.ProblemListView.as_view(), name='problems'),
]

from printviewer import views as printviewer

urlpatterns += [
    path('folder-detail/<int:pk>', printviewer.FolderDetailView.as_view(), name='folder-detail'),
    path('folders/', printviewer.FolderListView.as_view(), name='folders'),
]

urlpatterns += [
    path('print-detail/<int:pk>', printviewer.PrintDetailView.as_view(), name='print-detail'),
    path('prints/', printviewer.PrintListView.as_view(), name='prints'),
]



from video_search import views as video_search

urlpatterns += [
    # path('randomvideo/', youtube.views.VideoListView.as_view(), name='random_video'),
    path('video_search/<int:pk>', video_search.VideoSearchView.as_view(), name='video_search'),
]

from youtube import views as youtube

urlpatterns += [
    path('video/<int:pk>', youtube.VideoDetailView.as_view(), name='video-detail'),
    path('video_type/<int:pk>', youtube.VideoTypeDetailView.as_view(), name='video_type-detail'),
    path('video_genre/<int:pk>', youtube.VideoGenreDetailView.as_view(), name='video_genre-detail'),
    path('playlist/<int:pk>', youtube.PlaylistDetailView.as_view(), name='playlist-detail'),
    path('channelSection/<int:pk>', youtube.ChannelSectionDetailView.as_view(), name='channelSection-detail'),
]

urlpatterns += [
    path('university-detail/<int:pk>', youtube.UniversityDetailView.as_view(), name='university-detail'),
    path('universitys/', youtube.UniversityListView.as_view(), name='universitys'),
]





