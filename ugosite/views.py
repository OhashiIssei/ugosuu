# from types import NoneType
from django.shortcuts import render

# Create your views here.

from django.views import generic

from ugosite.models import Category, Article, Term,Problem
from youtube.models import Video
from printviewer.models import Folder,Print
from .models import Subject,Chapter,Section,Subsection

# from googletrans import Translator
# tr = Translator()
# tr.raise_Exception = True

def index(request):
    """View function for home page of site."""
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_articles': Article.objects.all().count(),
        'num_problems' : Problem.objects.all().count(),
        'num_prints' : Print.objects.all().count(),
        'num_terms': Term.objects.all().count(),
        'num_visits': num_visits,
        'num_videos' : Video.objects.all().count(),
        'article_list' : Article.objects.all()[:3],
        'category_list' : Category.objects.all(),
        'folder_list' : Folder.objects.filter(parent_folder__isnull = True),
        'playlist_list' : Playlist.objects.all()[:3],
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class ArticleDetailView(generic.DetailView):
    model = Article

class ArticleListView(generic.ListView):
    model = Article
    paginate_by = 500


class TermDetailView(generic.DetailView):
    model = Term


class TermListView(generic.ListView):
    def get_context_data(self, **kwargs):
        context = super(TermListView,self).get_context_data(**kwargs)
        terms = context["term_list"]
        
        context["term_list"] = filter(lambda term: term.videos_num()>1, terms)
        return context
    model = Term


class CategoryDetailView(generic.DetailView):
    model = Category

class CategoryListView(generic.ListView):
    model = Category
    def get_context_data(self, **kwargs):
        context = super(CategoryListView,self).get_context_data(**kwargs)
        context["category_list"] = Category.objects.all()
        return context


class ProblemDetailView(generic.DetailView):
    model = Problem
    # def get_context_data(self, **kwargs):
    #     context = super(ProblemDetailView,self).get_context_data(**kwargs)
    #     problem = context["problem"]
    #     category = problem.categorys.all()[0]
    #     context["category"] = category
    #     problems = Problem.objects.filter(categorys = category) 
    #     index = list(problems).index(problem)
    #     if not len(problems) == index+1:
    #         context['next'] = problems[index+1].get_absolute_url()
    #     if not index-1<0:
    #         context['prev'] = problems[index-1].get_absolute_url()
    #     context['up'] = problem.get_absolute_url()
    #     context['ancestors'] =  category.ancestors()+[category]
    #     context['self'] = problem
    #     return context

class ProblemListView(generic.ListView):
    model = Problem
    paginate_by = 100





### ????????????????????????????????????

from ugosite.create_datas import create_categories_form_four_step

from printviewer.create_datas import create_from_my_texfiles
from kakomon.create_datas import create_form_kakomon_files

from youtube.create_datas import download_Id_and_res,create_Models,add_Relation
from youtube.create_datas import ChannelSectionResponse,PlaylistResponse,PlaylistItemResponse,VideoResponse
from youtube.id import VideoId,PlaylistItemId,PlaylistId,ChannelSectionId,ChannelId
from youtube.models import VideoGenre,VideoType,University,Source

def reflesh_Models():
    # create_categories_form_four_step()
    # create_from_my_texfiles()
    # create_form_kakomon_files()
    
    # download_Id_and_res()
    # create_Models()
    add_Relation()

    print("reflesh_Models????????????")

# reflesh_Models()




import certifi
certifi.where()

from youtube.models import ChannelSection,Playlist,PlaylistItem

from .models import QuestionSet

class ArticleGenerater:
    # def make_from_playlist(self):
    def test(self):
        sections = ChannelSection.objects.filter(data__snippet__type = "multipleplaylists")
        for k,section in enumerate(sections):
            print("\n\n%s:%s" % (k+1,section))
            playlists = section.playlists()
            for i,playlist in enumerate(playlists):
                print(" %s:%s" % (i+1,playlist))
                playlistItems = playlist.playlistItems()
                for j,playlistItem in enumerate(playlistItems):
                    print("  %s:%s" % (j+1,playlistItem))
                    video = playlistItem.video()

    def make_from_playlists(self):
        for i,playlist in enumerate(Playlist.objects.all()):
            print(" %s:%s" % (i+1,playlist))
            QuestionSet().make_from_playlist(playlist)


# ArticleGenerater().test()






    


def display_status():
    print("Category?????????: %s" % Category.objects.count())
    print("")
    
    print("Subject?????????: %s" % Subject.objects.count())
    print("Chapter?????????: %s" % Chapter.objects.count())
    print("Section?????????: %s" % Section.objects.count())
    print("Subsection?????????: %s" % Subsection.objects.count())
    print("Article?????????: %s" % Article.objects.count())
    print("")
    
    print("Folder?????????: %s" % Folder.objects.count())
    print("Print?????????: %s" % Print.objects.count())
    print("")
    
    print("Problem?????????: %s" % Problem.objects.count())
    print("")
    
    print("ChannelId?????????: %s" % ChannelId.objects.count())
    print("ChannelSectionId?????????: %s" % ChannelSectionId.objects.count())
    print("PlaylistId?????????: %s" % PlaylistId.objects.count())
    print("VideoId?????????: %s" % VideoId.objects.count())
    print("")

    print("ChannelSectionResponse?????????: %s" % ChannelSectionResponse.objects.count())
    print("PlaylistResponse?????????: %s" % PlaylistResponse.objects.count())
    print("PlaylistItemResponse?????????: %s" % PlaylistItemResponse.objects.count())
    print("VideoResponse?????????: %s" % VideoResponse.objects.count())
    print("")

    print("Video?????????: %s" % Video.objects.count())
    print("Playlist?????????: %s" % Playlist.objects.count())
    print("PlaylistItem?????????: %s" % PlaylistItem.objects.count())
    print("ChannelSection?????????: %s" % ChannelSection.objects.count())
    print("")

    print("VideoType?????????: %s" % VideoType.objects.count())
    print("VideoGenre?????????: %s" % VideoGenre.objects.count())
    print("")

    print("University?????????: %s" % University.objects.count())
    print("Source?????????: %s" % Source.objects.count())
    print("")


# display_status()