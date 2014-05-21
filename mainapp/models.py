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
#Rider builds upon that basic table and fields required for the system. A rider could be a poster or reserver.

class Author(models.Model):
    #username
    user = models.OneToOneField(User)
    
    #gender
    #gender = models.CharField(max_length=1)
    #path to default user image
    image = models.CharField(max_length=300, default="http://www.decorview.com/sites/default/files/styles/products-image/public/default_user_image.jpg")
    
    #image
    imageobj = models.ImageField(upload_to=update_filename)
    
    #verification status
    #1 - unverified
    #any other number = verification code
    #verified = models.CharField(max_length=5)
    
    #authentication type
    #0 - PAN
    #1 - Driving License
    #2 - Voter Card
    #auth_type = models.CharField(max_length="20", default="None", null=False)
    #auth_token = models.CharField(max_length=200, default = "0", null=False)
    
    #user ratings
    #user_rating = models.IntegerField(default=0)
    #negative flags
    #neg_flags = models.IntegerField(default=0)

    #ratings on receipe

    #for reset_password
    reset_pass = models.CharField(default="",max_length=32)
    

    #Facebook ID
    #facebook_id = models.CharField(default="",max_length=200)
    
    #Facebook Friends
    #fbfriends = models.ManyToManyField("self")
    
    #Facebook Groups
    #fbgroups = models.CharField(default="", max_length=1000)
    
    #Last synced facebook datetime
    #last_fb_sync = models.DateTimeField('last_fb_sync', default = timezone.now())
    
    def __unicode__(self):
        return self.user.username
        
class Recipe(models.Model):
    author = models.ForeignKey(Author, null=False, related_name='author')
    text = models.CharField(max_length=2000)
    status = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.author.user.username

    
class Ratings(models.Model):

    recipe = models.ForeignKey(Recipe, null=False, related_name='recipe')
    rater = models.ForeignKey(Author)
    rating = models.IntegerField(default=0)


#Rating stores rating given to a rider by other riders

#class Rating(models.Model):
    
    ##Change primary key to combination of everything to prevent duplicates.
    ##Rating
    #rated = models.ForeignKey(Rider, related_name = 'rated')
    ##The rider that gives the rating
    #rater = models.ForeignKey(Rider, related_name = 'rater')
    
    #def __unicode__(self):
		#return self.rater.user.username + '->' + self.rated.user.username
    #given receipe
    
#Rating on receipes
#Post table stores details about posts
        
#class Post(models.Model):
    
    ##The owner of the post
    #owner = models.ForeignKey(Rider, null=False, related_name='owner')
    ##Car number
    #car_number = models.CharField(max_length=20)
    ##Total number of free seats in the vehicle
    #total_seats = models.IntegerField(default=1)
    ##Phone number
    #phone = models.IntegerField()
    ##From destination
    #fro = models.CharField(max_length=200)
    ##To destination
    ##Via Point 1
    #point1 = models.CharField(max_length=200)
    ##Via Point 2
    #point2 = models.CharField(max_length=200)
    #to = models.CharField(max_length=200)
    ##Date and time of trip
    #date_time = models.DateTimeField('date_time',default=timezone.now())
    
    ##status of post
    ##0 - scheduled
    ##1 - ongoing -> yet to be implemented
    ##2 - cancelled
    #status = models.IntegerField(default=0)
    #changed = models.IntegerField(default=0)
    
    ##Car AC status
    ##0 - No
    ##1 - Yes
    #ac = models.IntegerField(default=0)
    
    ##Whether the poster wants to auto accept requests.
    ##0 - No
    ##1 - Yes
    #autoaccept = models.IntegerField(default=0)
    
    ##0 - Both
    ##1 - Women only
    ##2 - Men only
    #men_women = models.IntegerField(default=0)
    
    
    ##0 - available to all
    ##1 - available to only friends
    #available_to = models.IntegerField(default=0)
    
    ##Cost of trip
    #cost = models.IntegerField(default=0)
    
    ##0 - Doesn't want notifications
    ##1 - Wants Notifications
    #sms_noti = models.IntegerField(default=1)
    
    ##Remarks for the trip
    #remarks = models.CharField(default="",max_length=100)
    
    #def __unicode__(self):
        #return self.owner.user.username
    

#Reserved stores details about reservations. Passengers and driver come from Riders, the post details come from Post.    
#Messages stores the message and sender/receiver information about messages that users send to each other.

#class Message(models.Model):
    
    ##Message sender
    #sender = models.ForeignKey(Rider, related_name = 'sender')
    ##Message receiver
    #receiver = models.ForeignKey(Rider, related_name = 'receiver')
    ##Actual message
    #message = models.CharField(max_length=200)
    ##Date and time of message
    #date_time = models.DateTimeField('date_time',default = timezone.now())
    
    
    ##The next two variables denote whether the message is present in the sender's and receiver's mailboxes or not.
    ##2 -> read: Not implemented yet
    ##1 -> present
    ##0 -> The user has deleted.
    ##As soon as both become 0, the message will be deleted from the database.
    #smailbox = models.IntegerField(default=1)
    #rmailbox = models.IntegerField(default=1)
    
##Temp check form
#class UploadFileForm(forms.Form):
    #first_name = forms.CharField(max_length=50)
    
