from django.shortcuts import render

from django.views import generic

# Create your views here.

import sys,os

from printviewer.models import Folder,Print



class FolderDetailView(generic.DetailView):
    model = Folder
    
class FolderListView(generic.ListView):
    model = Folder

class PrintDetailView(generic.DetailView):
    model = Print

class PrintListView(generic.ListView):
    model = Print