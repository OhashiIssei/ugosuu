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

import video_search,youtube

urlpatterns += [
    # path('randomvideo/', youtube.views.VideoListView.as_view(), name='random_video'),
    path('video_search/<int:pk>', video_search.views.VideoSearchView.as_view(), name='video_search'),
]

urlpatterns += [
    path('video/<int:pk>', youtube.views.VideoDetailView.as_view(), name='video-detail'),
    path('video_type/<int:pk>', youtube.views.VideoTypeDetailView.as_view(), name='video_type-detail'),
    path('video_genre/<int:pk>', youtube.views.VideoGenreDetailView.as_view(), name='video_genre-detail'),
    path('playlist/<int:pk>', youtube.views.PlaylistDetailView.as_view(), name='playlist-detail'),
    path('channelSection/<int:pk>', youtube.views.ChannelSectionDetailView.as_view(), name='channelSection-detail'),
]

urlpatterns += [
    path('university-detail/<int:pk>', youtube.views.UniversityDetailView.as_view(), name='university-detail'),
    path('universitys/', youtube.views.UniversityListView.as_view(), name='universitys'),
]





