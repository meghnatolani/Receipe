##models.py is used to store the database i.e. the tables and their attributes.

from paths import cpspath
from django import forms
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import os
from uuid import uuid4



#Custom function to return the Post type object's date_time (used for sorting)
def get_dt(p):
    return p.date_time

#To update the filename of the newly uploaded photo
def update_filename(instance, filename):
    path = cpspath + 'Receipe/media/propics/'
    format = instance.user.username + filename[filename.rfind('.'):]
    return os.path.join(path, format)

#Django provides a table called user that stores basic user information like username, password and email id.
#Author builds upon that basic table and fields required for the system. 

class Author(models.Model):
    #username
    user = models.OneToOneField(User)
        
    #path to default user image
    image = models.CharField(max_length=300, default="http://www.decorview.com/sites/default/files/styles/products-image/public/default_user_image.jpg")
    
    #image
    imageobj = models.ImageField(upload_to=update_filename)

    #for reset_password
    reset_pass = models.CharField(default="",max_length=32)
    
    
    def __unicode__(self):
        return self.user.username
        
class Recipe(models.Model):
    author = models.ForeignKey(Author, null=False, related_name='author')
    short_des = models.CharField(max_length=2000)
    image = models.CharField(max_length=300, default="http://www.decorview.com/sites/default/files/styles/products-image/public/default_user_image.jpg")
    imageobj = models.ImageField(upload_to=update_filename)
    ingredients = models.CharField(max_length=2000)
    calories = models.IntegerField(max_length=4)
    cost=models.IntegerField(max_length=4)
    steps=models.CharField(max_length=4000)
    share = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.author.user.username

    
class Ratings(models.Model):

    recipe = models.ForeignKey(Recipe, null=False, related_name='recipe')
    rater = models.ForeignKey(Author)
    rating = models.IntegerField(default=0)


