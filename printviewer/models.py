from django.db import models

from django.urls import reverse #Used to generate URLs by reversing the URL patterns


# Create your models here.

class Folder(models.Model):
    name = models.CharField(max_length=200, default="no_name_folder")
    description = models.TextField(max_length=10000, blank=True)
    parent_folder = models.ForeignKey("Folder", on_delete = models.CASCADE, blank=True,null=True)

    class Meta:
        ordering = ['id']

    def get_absolute_url(self):
        return reverse('folder-detail', args=[str(self.id)])

    def __str__(self):
        return self.name
    
    def children(self):
        children = list(Folder.objects.filter(parent_folder = self))
        children.extend(list(Print.objects.filter(parent_folder = self)))
        return children

    def ancestors(self):##先祖(自分含まない)
        module = self
        ancestors = []
        while module.parent_folder:
            ancestors.insert(0, module.parent_folder)
            module = module.parent_folder
        return ancestors
    
    
class Print(models.Model):
    name = models.CharField(max_length=200, default="name")
    description = models.TextField(max_length=1000, blank=True)
    parent_folder = models.ForeignKey(Folder, on_delete = models.CASCADE, blank=True,null=True)

    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('print-detail', args=[str(self.id)])