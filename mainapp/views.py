import math
from paths import cpspath
from facebook import GraphAPI
import json
from django.http import HttpResponse
from django.utils import timezone
from mainapp.models import *
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.db.models import Count, Min, Sum, Avg, Max
import uuid
import jinja2
import smtplib
from mainapp.checker import check
import thread
from django.http import *
from jinja2.ext import loopcontrols
import os
import urllib
import urllib2
#from pymaps import *
#from var import *

#def fb_notif(userid, message):
    #url = 'https://graph.facebook.com/%s/notifications' % (userid)
    #user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    #header = { 'User-Agent' : user_agent }
    #values = {'access_token':"%s|%s" % (FB_APP_ID, FB_APP_SECRET), 'template':message, 'href':'' }
    #data = urllib.urlencode(values)
    #req = urllib2.Request(url, data, header)
    #response = urllib2.urlopen(req)
    #return response


def split_space(x):
    return x.strip().split()

jinja_environ = jinja2.Environment(loader=jinja2.FileSystemLoader([cpspath + '/carpoolsen/ui']), extensions=[loopcontrols])
jinja_environ.filters['split_space'] = split_space

month=["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
website = "http://localhost:8000"

#Function to remove old posts of user. Everytime a user logs in, his/her posts which have expired within one hour will be deleted.
#def remove_old_posts(user):
    #for x in Post.objects.filter(owner=user.author):
        #if (timezone.now() - x.date_time).total_seconds() > POST_TIMEOUT:
            #if x.changed == 1:
                #for y in x.reserved_set.all():
                    #if y.reserved_set.all().aggregate(Sum('edited'))['edited__sum'] == 0:
                        #if user.author.neg_flags > 0:
                            #user.author.neg_flags -= 1
                    #dumptofile(y)
                    #y.delete()
            #dumptofile(x)
            #x.delete()

#Function to send emails using google smtplib. Takes email id and message as input.            
#def send_email(msg, email):
    #gmailLogin = 'carpoolsen'
    #gmailPas = 'qwertqwert!'
    #fro = gmailLogin + "@gmail.com"
    
    #to = email
    
    #server = smtplib.SMTP_SSL('smtp.googlemail.com',SMTP_PORT)
    #a = server.login( gmailLogin, gmailPas)
    #server.sendmail(fro, to,msg)
    #return (1,1)

##Function to send verification mail to user's email after he signs up.
#def send_verification_email(request):
    #if not request.user.is_authenticated():
        #return HttpResponse(jinja_environ.get_template('index.html').render({"author":None}))

    #try:
        #request.user.author
    #except:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              #"text":'No Author associated!. Please go back or click  to go to the homepage' , "link": '/'}))
    #entry=request.user
    #subject = 'Knorre Verification Email'
    #msg = 'Subject: %s \n\nYour email has been registered on <site>.\nPlease\
    #click on the following link to verify (or copy paste it in your browser if needed)\n\n\
    #%s/verify?code=%s\n\nIf you have not registered on our website, please ignore.' % (subject, website, entry.author.verified)
    
    #x = send_email(msg, entry.email)
    #if x[0]==0:
        #return x[1]
    
    #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author, "text":'<p>Verification Email sent! Please Check your email inbox.</p><p>To re-send verification email, click <a href=\'/send_verification_email/\'>here</a>.</p><p>Click <a href=\'/logout_do/\'>here</a> to go to the homepage and log-in again</p>', "link":'0'}))

#Calls index page
def index(request):
    return HttpResponse(jinja_environ.get_template('index.html').render({"author":None}))
    
#Calls the signup page. If the user us already logged in, s/he will be redirected to dashboard.
def signup_page(request):
    if request.user.is_authenticated():
        redirect_url = "/"
        if 'redirect_url' in request.REQUEST.keys():
            redirect_url = request.REQUEST['redirect_url']
        return HttpResponse(jinja_environ.get_template('redirect.html').render({"author":None,"redirect_url":redirect_url}))

    else:
        return HttpResponse(jinja_environ.get_template('signup.html').render({"author":None}))
#Calls the login page
def login_page(request):
    author = None
    if request.user.is_authenticated():
        author = request.user.author
    return HttpResponse(jinja_environ.get_template('loginverify.html').render({"author":author, "redirect": request.REQUEST['redirect']}))
    
#Calls the contact us page.
def contactus(request):
    author = None
    if request.user.is_authenticated():
        author = request.user.author
    return HttpResponse(jinja_environ.get_template('ContactUs.html').render({"author":author}))

#Calls the user manual page
#def usermanual(request):
    #author = None
    #if request.user.is_authenticated():
        #author = request.user.author
    #return HttpResponse(jinja_environ.get_template('manual.html').render({"author":author}))

#Calls the FAQ page.
#def faq(request):
    #author = None
    #if request.user.is_authenticated():
        #author = request.user.author
    #return HttpResponse(jinja_environ.get_template('FAQs.html').render({'author':author}))
    
#Calls the About Us page.
def aboutus(request):
    author = None
    if request.user.is_authenticated():
        author = request.user.author
    return HttpResponse(jinja_environ.get_template('AboutUs.html').render({"author":author}))
    
#Calls the edit profile page. The autofill data is sent too.
#def edit_profile_page(request):
    #if not request.user.is_authenticated():
        #return HttpResponse(jinja_environ.get_template('index.html').render({"author":None}))
    ##Check if user has an associated author
    ##(This will be false if the admin logs in)
    #try:
        #request.user.author
    #except:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              #"text":'No Author associated!.\
                                                                                  #Please go back or click OK to go to the homepage',"link":'/'}))
    #return HttpResponse(jinja_environ.get_template('pref.html').render({"author":request.user.author}))


#To display the Google Map of a post
#def postmap(request):
    #retval = check(request)
    #if retval <> None:
        #return retval
    #return HttpResponse(jinja_environ.get_template('postmap.html').render({"author":request.user.author, "post":Post.objects.get(pk=int(request.REQUEST['id']))}))

#Calls the edit post page. Also, sends the autofill form data.    
#def edit_post_page(request):
    #retval = check(request)
    #if retval <> None:
        #return retval

    #try:
        #author=request.user.author
        #key=request.REQUEST['key']
        #postobj=Post.objects.get(id=key)
        #return HttpResponse(jinja_environ.get_template('postedit.html').render({"author":request.user.author, 'post':postobj, 'reserved_list':postobj.reserved_set.all()}))
    #except Exception as e:
        #return HttpResponse(e)

#Call to open user's profile page.Sends data to be displayed.        
#def profile(request):
    #if not request.user.is_authenticated():
        #return HttpResponse(jinja_environ.get_template('index.html').render({"author":None}))

    ##Check if user has an associated author
    ##(This will be false if the admin logs in)
    #try:
        #request.user.author
    #except:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              #"text":'<p>No Author associated!.</p><p>Please go back or click OK to go to the homepage</p>',"link":'/'}))

    #try:
        #authorid = request.REQUEST['id']
        #if authorid == request.user.author.pk:
            #return HttpResponse(jinja_environ.get_template('profile.html').render({"author":request.user.author, "profiler":request.user.author}))
        #else:
            #return HttpResponse(jinja_environ.get_template('profile.html').render({"author":request.user.author, "profiler":Author.objects.get(pk=authorid)}))
    #except:
        #return HttpResponse(jinja_environ.get_template('profile.html').render({"author":request.user.author, "profiler":request.user.author}))

##Call for the invite friends page. Also sends default message to be displayed.
#@csrf_exempt
#def invite_page(request):
    #retval = check(request)
    #if retval <> None:
        #return retval
    
    #message = "Hey! Check out this amazing site, we can travel together now!"

    #try :
      #request.user.author
      #return HttpResponse(jinja_environ.get_template('invite.html').render({"author": request.user.author,
                                        #"message": message}))
    #except Exception as e:
      #return HttpResponse(e)
    
##Call function for the inbox page.Sends the user's valid messages as a list, ordered by date and time
#def inbox_page(request):   

    #retval = check(request)
    #if retval <> None:
        #return retval
    
    #try:
        #results = Message.objects.filter(receiver=request.user.author).extra(order_by = ['-date_time'])
        #max_mid = 0
        #for x in results:
            #if x.id > max_mid:
                #max_mid = x.id
        #return HttpResponse(jinja_environ.get_template('inbox.html').render({"author":request.user.author,
                                                                             #"messages":results,
                                                                             #"max_mid": max_mid,}))
    #except:
        #return HttpResponse(jinja_environ.get_template('inbox.html').render({"author":request.user.author,
                                                                             #"messages":None,
                                                                             #"max_mid": 0,}))

##Function to generate a receipt, after a reservation has been confirmed. 
#def receipt(request):
    #retval = check(request)
    #if retval <> None:
        #return retval
    
    #try:
        #return HttpResponse(jinja_environ.get_template('receipt.html').render({"author":request.user.author,
                                                                               #"post":Post.objects.get(pk=request.REQUEST['key'])}))
        
    #except:
        #return HttpResponse(jinja_environ.get_template('receipt.html').render({"post":None}))

##Main dashboard call function, the homepage for a user after he has logged in. The data of a user's posts, reserves and inbox messages.
#def dashboard(request):
    
    #retval = check(request)
    #if retval <> None:
        #return retval
    
    ##Delete old threads
    #remove_old_posts(request.user)
    
    #posts = Post.objects.filter(owner=request.user.author, status__lte=1)
    #fbpost_list = []
    #post_list = []
    #fbgroup_list = []
    
    ##Check if user has enabled facebook sync:
    #if len(request.user.author.facebook_id) > MIN_FBID_LEN:
        ##Update facebook friends if more than a week
        #if (timezone.now() - request.user.author.last_fb_sync).total_seconds > FB_SYNC_TIMEOUT:
            ##Update friendlist
            #friendlist = []
            #try:
                #friendlist = GraphAPI(str(request.user.author.facebook_id.split()[1])).get_connections("me","friends")['data']
            #except:
                #pass
            #for x in friendlist:
                #for y in Author.objects.filter(facebook_id__contains=x['id']):
                    #request.user.author.fbfriends.add(y)
            #request.user.author.save()
        
        ##get groups of user
        #grouplist = []
        #try:
            #grouplist = GraphAPI(str(request.user.author.facebook_id.split()[1])).get_connections("me","groups")['data']
        #except:
            #pass
        #for x in grouplist:
            #fbgroup_list += [x['name']]
            #request.user.author.fbgroups += "|" + x['name']
        #request.user.author.save()
        
        ##Add posts from fbfriends to fbpost_list
        ##for x in posts:
            ##text1 = "You have a <a href=\"/post_page?key=%s\">trip</a> from %s to %s with " % (str(x.id), x.fro, x.to)
            ##text2 = " on %s at %s" % (str(x.date_time.date()), str(x.date_time.time()))
            ##text12 = ""
            ##for y in x.reserved_set.all():
                ##if y in request.user.author.fbfriends.all():
                    ##text12 += " <a href=\"/profile?id=%s\">%s %s</a>," % (str(y.id), y.user.first_name, y.user.last_name)
            ##if len(text12) > 0:
                ##text12 = text12[:-1]
            ##text = text1 + text12 + text2
            ##fbpost_list += [text]
        
        ##for x in Reserved.objects.filter(reserver=request.user.author)[::-1]:
            ##text1 = "You have a <a href=\"/post_page?key=%s\">trip</a> from %s to %s with " % (str(x.post.id), x.post.fro, x.post.to)
            ##text2 = " on %s at %s" % (str(x.post.date_time.date()), str(x.post.date_time.time()))
            ##text12 = ""
            ##for y in x.post.reserved_set.all():
                ##if y in request.user.author.fbfriends.all():
                    ##text12 += " <a href=\"/profile?id=%s\">%s %s</a>," % (str(y.id), y.user.first_name, y.user.last_name)
            ##if x.post.owner in request.user.author.fbfriends.all():
                ##y = x.post.owner
                ##text12 += " <a href=\"/profile?id=%s\">%s %s</a>," % (str(y.id), y.user.first_name, y.user.last_name)
            ##if len(text12) > 0:
                ##text12 = text12[:-1]
            ##text = text1 + text12 + text2
            ##fbpost_list += [text]
            
        
        ##Add posts of facebook friends to fbpost_list
        #for x in request.user.author.fbfriends.all():
            #fbpost_list += Post.objects.filter(owner=x)
    #messages = Message.objects.filter(receiver = request.user.author)
    
    ##Generate list of reserved objects for posts made by user.
    #for x in posts:
        #post_list.append([x,len(x.reserved_set.all()), len(x.reserved_set.filter(status=1))])
    
    
    ##create jinja template values
    #retval = check(request)
    #if retval <> None:
        #return retval
    #date_time1 = None
    #date_time2 = None
    #l_p_obj = Post.objects.filter(owner=request.user.author, date_time__gte = timezone.now(), status__lte=1)
    #l_r_obj = Reserved.objects.filter(reserver=request.user.author, status__lte=1)
    #resobj = None
    #pobj = None
    #if len(l_p_obj) <> 0:
        #l_p_obj = l_p_obj.aggregate(Min('date_time'))
        #date_time1 = l_p_obj['date_time__min']
        #pobj = Post.objects.filter(owner=request.user.author, date_time=date_time1)[0]
    #if len(l_r_obj) <> 0:
        #mindt = None
        #for x in l_r_obj:
            #if x.post.date_time < timezone.now():
                #continue
            #if mindt == None:
                #resobj = x
                #mindt = x.post.date_time
            #if mindt > x.post.date_time:
                #resobj = x
                #mindt = x.post.date_time
        #date_time2 = mindt
    #if date_time1 <> None:
        #if (date_time1-timezone.now()).total_seconds() > 1800:
            #date_time1=None
    #if date_time2 <> None:
        #if (date_time2-timezone.now()).total_seconds() > 1800:
            #date_time2=None
    #template_values = {'author' : request.user.author,
                    #'messages' : messages[::-1],
                    #'post_list' : post_list[::-1],
                    #'reserved_list' : Reserved.objects.filter(reserver=request.user.author)[::-1],
                    #"date_time1":date_time1,
                    #"date_time2":date_time2,
                    #"reserved_obj":resobj,
                    #"post_obj": pobj,
                    #"nowtime": timezone.now(),
                    #"fbpost_list": sorted(fbpost_list, key=get_dt),
                    #"fbgroup_list": fbgroup_list,
                    #}
    #return HttpResponse(jinja_environ.get_template('dashboard2.html').render(template_values)) 

#The call function for the settings page.
#def settings_page(request):
    #if not request.user.is_authenticated():
        #return HttpResponse(jinja_environ.get_template('index.html').render({"author":None}))

    ##Check if user has an associated author
    ##(This will be false if the admin logs in)
    #try:
        #request.user.author
    #except:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              #"text":'<p>No Author associated!.</p><p>Please go back or click OK to go to the homepage</p>',"link":'/'}))
    #return HttpResponse(jinja_environ.get_template('pref.html').render({"author":request.user.author, 'owner':request.user.author}))
    
#The call function for new post form.    
def post_form(request):
    retval = check(request)
    if retval <> None:
        return retval
    return HttpResponse(jinja_environ.get_template('post.html').render({"author":request.user.author, 'author':request.user.author}))

#The call function for a post page.    
def post_page(request):
    retval = check(request)
    if retval <> None:
        return retval
        
    recipeobj=Recipe.objects.filter(pk=request.REQUEST['key'], status__lte=1)[0]
    #reserved=postobj.reserved_set.aggregate(Sum('status'))['status__sum']
    
    #friendlist = []
    #if len(request.user.author.facebook_id.split()) > 0:
        #friendlist += [request.user.author.facebook_id.split()[0]]
    #try:
        #if len(request.user.author.facebook_id.split()) > 0:
            #templist = GraphAPI(request.user.author.facebook_id.split()[1]).get_connections("me","friends")['data']
            #for x in templist:
                #friendlist += [x['id']]
    #except:
        #pass
    
    #if postobj.available_to == 1 and postobj.owner.facebook_id.split()[0] not in friendlist:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'<p>You are not allowed to view this page.</p>\
                                                                                  #<p>Click OK to go to the homepage</p>',"link":'/'}))
    
    #x=postobj.date_time
    
    #date=x.date()
    #time=x.time()
    
    #reserved_obj = None
    #for x in postobj.reserved_set.all():
        #if x.reserver.user.username == request.user.username:
            #reserved_obj = x
            #break
    
    #if(reserved>0):
      #template_values={'post':postobj, 
               #'minus':postobj.total_seats-reserved,
               #'date':date,
               #'time':time,
               #'author':request.user.author,
               #'reserved_obj': reserved_obj,
               #'reserved_list': postobj.reserved_set.all(),
               #"nowtime":timezone.now(),
                  #}
                  
    #else: 
      #template_values={'post':postobj, 
               #'minus':postobj.total_seats,
               #'time':time,
               #'date':date,
               #'author':request.user.author,
               #'reserved_obj': reserved_obj,
               #'reserved_list': postobj.reserved_set.all(),
               #"nowtime":timezone.now(),
                  #}
              
    return HttpResponse(jinja_environ.get_template('postpage.html').render(recipeobj))

#Forgot Password page call function.
#def forgot_pass_page(request):
    #if request.user.is_authenticated():
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'<p>Please log out before requesting reset in password.</p>\
                                                                                  #<p>Click OK to go to the homepage</p>',"link":'/'}))
    #return HttpResponse(jinja_environ.get_template('forgot_password.html').render({"author":None}))

##Reset Password page call function.
#@csrf_exempt
#def reset_pass_page(request):
    #if request.user.is_authenticated():
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'<p>Please log out before requesting reset in password.</p>\
                                                                                  #<p>Click OK to go to the homepage</p>',"link":'/'}))
    #if "reset_pass" not in request.REQUEST.keys() or 'email' not in request.REQUEST.keys():
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              #"text":'<p>Invalid Request</p>\
                                                                                  #Click OK to go to the homepage</p>', "link":'/'}))
    #reset_pass = request.REQUEST['reset_pass']
    #if reset_pass == "":
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              #"text":'<p>Invalid Request</p>\
                                                                                  #<p>click OK to go to the homepage</p>', "link":'/'}))
    #user = Author.objects.filter(reset_pass=reset_pass)
    #if len(user)==0:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                                #"text":'Invalid Request. Please go back or click OK to go to the homepage',"link":'/'}))
    
    #user = user[0].user
    
    #if user.email <> request.REQUEST['email']:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                                #"text":'Invalid Email. Please go back or click OK to go to the homepage',"link":'/'}))
    #return HttpResponse(jinja_environ.get_template('reset_password.html').render({'author':None, 'reset_pass':reset_pass}))

##Change password page call function    
#def change_pass_page(request):
    #retval = check(request)
    #if retval <> None:
        #return retval
    #return HttpResponse(jinja_environ.get_template('ChangePass.html').render({"author":request.user.author}))
        

#Edit profile function. Called after a user presses done in edit profile. New data is requested from frontend and stored.
#@csrf_exempt
#def edit_profile(request):
    #if not request.user.is_authenticated():
        #return HttpResponse(jinja_environ.get_template('index.html').render({"author":None}))

    ##Check if user has an associated author
    ##(This will be false if the admin logs in)
    
    #try:
        #request.user.author
    #except:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              #"text":'<p>No Author associated!.</p><p>Please go back or click OK to go to the homepage</p>', "link":'/'}))
    
    
    ##To remove profile picture
    #if 'reset_image' in request.REQUEST.keys():
        #request.user.author.image = "http://vfcstatic.r.worldssl.net/assets/car_icon-e0df962a717a5db6ebc8b37e80b05713.png"
        #if str(request.user.author.imageobj) <> '':
            #path = cpspath + 'media/propics/' + request.user.username + request.user.author.imageobj.url[request.user.author.imageobj.url.rfind('.'):]
            #if os.path.isfile(path):
                #os.remove(path)
        #request.user.author.save()
        #return edit_profile_page(request)
    
    
    #if 'image' in request.FILES.keys():
        ##delete old file
        #if str(request.user.author.imageobj) <> '':
            #path = cpspath + 'media/propics/' + request.user.username + request.user.author.imageobj.url[request.user.author.imageobj.url.rfind('.'):]
            #if os.path.isfile(path):
                #os.remove(path)
        #request.user.author.imageobj = request.FILES['image']
        #request.user.author.image = '/fonts/' + request.user.username + request.user.author.imageobj.url[request.user.author.imageobj.url.rfind('.'):]
    
    
    
    #request.user.author.gender = request.REQUEST['gender']
    
    #request.user.author.phone = request.REQUEST['phone']
    #request.user.author.car_number = request.REQUEST['car_number']
    #request.user.author.auth_type = request.REQUEST['auth_type']
    #request.user.author.auth_token = request.REQUEST['auth_token']
    #if request.user.author.auth_type <> "None" and request.user.author.auth_token == "0":
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                          #"text":'Please enter valid authentication ID.',"link":'/settings_page/'}))
    
    #request.user.author.save()
    
    #request.user.first_name = request.REQUEST['first_name']
    #request.user.last_name = request.REQUEST['last_name']
    
    #if '@' not in request.REQUEST['email'] or '.' not in request.REQUEST['email']:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                          #"text":'Please enter valid email.',"link":'/settings_page/'}))
    
    #if request.user.email <> request.REQUEST['email']:
        #request.user.email = request.REQUEST['email']
        #request.user.author.verified = uuid.uuid4().hex
        #request.user.author.save()
        #send_verification_email(request)
    
    #request.user.save()
    
    #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                          #"text":'Profile edit successful. Please go back or click OK to go to the homepage',"link":'/'}))
    
#Called when a user clicks submit button in signup. Here a verification mail is also sent to the user.
@csrf_exempt
def signup_do(request):
    if request.user.is_authenticated():
        logout(request)
        redirect_url = "/"
        if 'redirect_url' in request.REQUEST.keys():
            redirect_url = request.REQUEST['redirect_url']
        return HttpResponse(jinja_environ.get_template('redirect.html').render({"author":None,"redirect_url":redirect_url}))
    
    username = request.REQUEST['username']
    password = request.REQUEST['password']
    confirmpassword = request.REQUEST['confirmpassword']
        
    if password <> confirmpassword:
      return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                            "text":'<p>Passwords don\'t match. Please Enter again.</p><p>Click OK to go back to signup page.</p>',"link":'/signup_page/'}))
    
    first_name = request.REQUEST['first_name']
    last_name = request.REQUEST['last_name']
    #phone = request.REQUEST['phone']
    #email = request.REQUEST['email']
    #gender = request.REQUEST['gender']

    try:
        if len(User.objects.filter(email=email))<>0:
            return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                                  "text":'<p>Someone has already registered using this email.</p><p>If you have forgotten your password, click <a href=\'/forgot_pass/\'</p><p>Click <a href=\'/signup_page/\'>here</a> to go back to signup page.</p>',"link":'0'}))
    except:
        pass
    
    if '@' not in email or '.' not in email:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              "text":'<p>Invalid email, please Enter again.</p><p>Go Back or click OK to go to signup page.</p>',"link":"/signup_page/"}))
    
    #car_number = request.REQUEST['car_number']
    
    if first_name == "":
        first_name = username
    
    try:
        user = User.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        entry = Author(user=user)
        
        entry.save()
        #send email to user
        login_do(request)
        #return send_verification_email(request)
        return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author, "text":'Signup Successful. Click OK to go to dashboard', "link":'/'}))
        
    except Exception as e:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              "text":'<p>Username already exists. Please enter some other username.</p><p>Go Back or click OK to go to signup page.</p>',"link":'/signup_page/'}))
    

#Called when a user enters verification code and clicks on submit. Checks the verification code with database.
#def verify(request):
    #if not request.user.is_authenticated():
        #return HttpResponse(jinja_environ.get_template('loginverify.html').render({"author":1,
                                                                                   #"code":request.REQUEST['code']}))
    #try:
        #request.user.author
    #except:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                             #"text":'<p>No Author associated.</p><p>Please go back or click OK to go to the homepage</p>',"link":'/'}))
    
    #code = request.REQUEST['code']
    #author = request.user.author
    #if author.verified == '1':
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'<p>Verification successful.</p><p>Click OK to go to the homepage</p>',"link":'/'}))
    #elif code == author.verified:
        #author.verified = '1'
        #author.save()
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'<p>Verification successful.</p><p>Click OK to go to the homepage</p>',"link":'/'}))
    
    #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                          #"text":'<p>Verification Failed.</p><p>Please go back or click OK to go to the homepage</p>',"link":'/'}))


#Called when a user clicks logout button.
def logout_do(request):
    logout(request)
    redirect_url = "/"
    if 'redirect_url' in request.REQUEST.keys():
        redirect_url = request.REQUEST['redirect_url']
    return HttpResponse(jinja_environ.get_template('redirect.html').render({"author":None,"redirect_url":redirect_url}))
    
#Called when a user clicks login button. 
@csrf_exempt
def login_do(request):
    username = request.REQUEST['username']
    password = request.REQUEST['password']
    user = authenticate(username=username, password=password)
    
    if user is not None:
        if user.is_active:
            login(request, user)
            if 'redirect' in request.REQUEST.keys():
                return HttpResponse(jinja_environ.get_template('redirect.html').render({"author":None,"redirect_url":request.REQUEST['redirect'].replace("!!__!!","&")}))
            return HttpResponse(jinja_environ.get_template('redirect.html').render({"author":None,"redirect_url":"/"}))
        else:
            # Return a 'disabled account' error message
            if "js" in request.REQUEST.keys():
                return HttpResponse("disabled")
            return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                                "text":'<p>Disabled Account.</p><p>Please go back or click OK to go to the homepage</p>',"link":'/'}))
        
    else:
        # Return an 'invalid login' error message.
        if "js" in request.REQUEST.keys():
            if len(User.objects.filter(username=request.REQUEST['username'])) == 0:
                return HttpResponse("inv_user")
            return HttpResponse("inv_pass")
        return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              "text":'Invalid Login. Please go back or click OK to go to the homepage',"link":'/'}))
    

#Called when the user clicks forgot password after the data is validated. This sends a verification mail to the user.
#@csrf_exempt
#def forgot_pass(request):
    #if request.user.is_authenticated():
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              #"text":'<p>Please log out in order to request for a password reset.</p>\
                                                                                  #<p>Please go back or click OK to go to the homepage</p>',"link":'/'}))
    #if 'username' not in request.REQUEST.keys() or 'email' not in request.REQUEST.keys():
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              #"text":'Invalid Request. Please go back or click OK to go to the homepage',"link":'/'}))
    #user = User.objects.filter(username=request.REQUEST['username'])
    #if len(user) == 0:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              #"text":'User Does not exist. Please go back or click OK to go to the homepage',"link":'/'}))
    #user = user[0]
    #if user.email <> request.REQUEST['email']:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              #"text":'Invalid email. Please go back or click OK to go to the homepage',"link":'/'}))
    #user.author.reset_pass = uuid.uuid4().hex
    #user.author.save()
    
    #subject = "Password Reset Request"
    #msg = 'Subject: %s \n\nYou have requested for a password reset on RideBuddy\n\
    #Please click on the following link (or copy paste in your browser) to reset your password.\n\n\
    #%s/reset_pass_page/?reset_pass=%s&email=%s\n\n\
    #If you have not requested for a reset of password, please ignore.' % (subject, website, user.author.reset_pass, user.email)
    
    #x = send_email(msg, user.email)
    #if x[0] == 0:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              #"text":'Could not process request, please try again later by going back or clicking OK to go to the homepage', "link":'/'}))
    #else:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                              #"text":'<p>An email has been sent to your regestered email address.</p>\
                                                                                  #<p>Check your email and click on the link to reset your password.</p>\
                                                                                  #<p>Click OK to go to the homepage</p>',"link":'/'}))
    
##Called when the user clicks change password button. Checks if the previous password is valid or not.
#@csrf_exempt
#def change_pass(request):
    #if "reset_pass" in request.REQUEST.keys():
        #reset_pass = request.REQUEST['reset_pass']
        #if reset_pass == "":
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                                  #"text":'<p>Invalid Request</p>\
                                                                                      #<p>click OK to go to the homepage</p>',"link":'/'}))
        #user = Author.objects.filter(reset_pass=reset_pass)
        #if len(user)==0 or 'pass' not in request.REQUEST.keys():
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                                  #"text":'Invalid Request. Please go back or click OK to go to the homepage',"link":'/'}))
        #user = user[0].user
        #user.set_password(request.REQUEST['pass'])
        #user.save()
        #user.author.reset_pass = ""
        #user.author.save()
        #logout(request)
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":1,
                                                                              #"text":'Password Changed. Please click OK to go to the homepage and log in again.',"link":'/logout_do/'}))
    #else:
        #retval = check(request)
        #if retval <> None:
            #return retval
        #if "pass" not in request.REQUEST.keys() or "oldpass" not in request.REQUEST.keys():
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                                  #"text":'Invalid Request. Please go back or click OK to go to the homepage',"link":'/'}))
        #if not request.user.check_password(request.REQUEST['oldpass']):
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                                  #"text":'Invalid Old Password. Click OK to go to the homepage',"link":'/'}))
        #request.user.set_password(request.REQUEST['pass'])
        #request.user.save()
        #logout(request)
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":1,
                                                                              #"text":'Password Changed. Please click OK to go to the homepage and log in again.',"link":'/logout_do/'}))
        
##Called when a user cancels his post. Here all the reserved users are sent a notification and the owner gets a negative flag if there are confirmed users on that post.
#@csrf_exempt
#def cancel_post(request):
    #retval = check(request)
    #if retval <> None:
        #return retval
    #user = request.user

    ##Not allowed to delete if user is not logged in. Not called, but to take edge cases into consideration.
    #postid = request.REQUEST['postid']

    #try:
        #entry = Post.objects.filter(pk=int(postid))[0]
        #if entry.owner.user.pk == user.pk:
            #if entry.reserved_set.aggregate(Sum('status'))['status__sum'] > 0:
                #owner=entry.owner
                #if owner.neg_flags<5:
                    #owner.neg_flags += 1
                    #owner.save()
            #entry.status = 2
            #entry.changed = 1
            #try:
                #for x in entry.resetved_set.filter(status=1):
                    #send_email("Subject:Post Cancelled\n\nYour trip from " + entry.fro + " to " + entry.to + " on " + str(entry.date_time.date()) + " at " + str(entry.date_time.time()) + " has been cancelled by the owner.\n Click " + website + " to go to the home page.", x.reserver.user.email)
                    #if len(x.reserver.facebook_id) > MIN_FBID_LEN:
                        #fb_notif(x.reserver.facebook_id.split()[0], "Your trip from " + entry.fro + " to " + entry.to + " on " + str(entry.date_time.date()) + " at " + str(entry.date_time.time()) + " has been cancelled by the owner")
            #except:
                #pass
            #entry.save()
            
        #else:
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                                #"text":'<p>Not enough permissions.</p>\
                                                                                    #<p>Please go back or click OK to go to the homepage</p>',"link":'/'}))
    #except Exception as e:
        #return HttpResponse(e)

    
    #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                          #"text":'Post Cancelled successfully. Please go back or click OK to go to the homepage',"link":'/'}))

#Called when a user clicks submit on new post form.                                                                          
@csrf_exempt
def post_new(request):
    global month
    #check for user login
    retval = check(request)
    if retval <> None:
        return retval
    owner = request.user.author
    #car_number = request.REQUEST['car_number']
    #total_seats = int(request.REQUEST['total_seats'])
    #phone = request.REQUEST['phone']
    #fro = request.REQUEST['fro']
    #to = request.REQUEST['to']
    #point1 = request.REQUEST['point1']
    #point2 = request.REQUEST['point2']
    
    
    ##Date and time format: dd mm yyyy - hh:mm
    #date_time=request.REQUEST['date_time']
    #date_time=date_time.split(' ')
    #date=date_time[0:3]
    #time=date_time[4]
    #time=time.split(':')
    
    #date_time = datetime.datetime(day=int(date[0]),
                                  #month=month.index(date[1]), 
                                  #year=int(date[2]), 
                                  #hour=int(time[0]),
                                  #minute=int(time[1]), 
                                  #second=0, 
                                  #microsecond=0,)
        
    #ac = int(request.REQUEST['ac'])
    #men_women = 0
    #men_women = int(request.REQUEST['men_women'])
    
    #available_to = int(request.REQUEST['available_to'])
    
    #autoaccept = 0
    #try:
        #autoaccept += int(request.REQUEST['autoaccept'])
    #except:
        #pass
    
    #cost = int(request.REQUEST['cost'])
    
    #sms_noti = 0
    #try:
        #sms_noti += int(request.REQUEST['sms_noti'])
    #except:
        #pass
    
    ##Check for empty car number
    #if car_number.strip() == '':
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'Invalid Car number. Click OK to go back to the Post Your Trip form',"link":'/post_form/'}))
    
    #tempres = Post.objects.filter(owner=owner, status__lte=1)
    #for x in tempres:
        #if math.fabs((x.date_time.replace(tzinfo=None)-date_time.replace(tzinfo=None)).total_seconds()) < 1800:
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                                  #"text":'<p>You already have a post within 30 minutes of this post.</p><p>The only way you can take care of both posts is by driving too fast</p><p>And we do not promote that.</p><p>Please go back or click OK to go to the homepage</p>',
                                                                                  #"link":'/'
                                                                                  #}))
    
    #for x in Reserved.objects.filter(reserver=owner):
            #if math.fabs((x.post.date_time.replace(tzinfo=None)-date_time.replace(tzinfo=None)).total_seconds()) < 1800 and x.post.status <= 1:
                #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                                      #"text":'<p>You already have a trip within 15 minutes of this request.</p>\
                                                                                      #<p>Please go back or click OK to go to the homepage</p>',"link":"/"}))
    #remarks = ""
    
    #if 'remarks' in request.REQUEST.keys():
        #remarks=request.REQUEST['remarks']
        
    entry = Recipe(owner=owner, 
                 short_des=request.REQUEST['short_des'], 
                 ingredients=request.REQUEST['ingredients'],
                 calories=request.REQUEST['calories'],
                 cost=request.REQUEST['cost'],
                 steps=request.REQUEST['steps'],
                 share=request.REQUEST['share'],
                 )
    entry.save()
    return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                          "text":'<p>Post successful. </p>Please go back or click OK to go to the homepage',
                                                                          "link": '/'}))

#Called when a user clicks the reserved button on a post. Here the gender preferences are checked. If there already a post/reserve within given timeframe, then an error is thrown.                                                                          
#def reserve(request):
    ##check for user login
    #retval = check(request)
    #if retval <> None:
        #return retval
        
    #reserver = request.user.author
    #postid = request.REQUEST['postid']
    #postobj = Post.objects.filter(pk=postid)[0]
    
    #if reserver == postobj.owner:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                        #"text":'<p>You can\'t reserve your own post.</p>\
                                                                            #<p>Please go back or click OK to go to the homepage</p>', "link":'/'}))
    
    #if postobj.date_time < timezone.now():
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                        #"text":'<p>Trip already started, cannot reserve now.</p>\
                                                                            #<p>Please go back or click OK to go to the homepage</p>', "link":'/'}))
    
    #if (reserver.gender=='m' and postobj.men_women==1) or (reserver.gender=='f' and postobj.men_women==2):
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                                #"text":'<p>You are not allowed to reserve this post due to gender preferences of the owner.</p>\
                                                                                    #<p>Please go back or click OK to go to the homepage</p>',"link":'/'}))
    
    #friendlist = []
    #if len(request.user.author.facebook_id.split()) > 0:
        #friendlist += [request.user.author.facebook_id.split()[0]]
    #try:
        #if len(request.user.author.facebook_id.split()) > 0:
            #templist = GraphAPI(request.user.author.facebook_id.split()[1]).get_connections("me","friends")['data']
            #for x in templist:
                #friendlist += [x['id']]
    #except:
        #pass
    #if postobj.available_to == 1 and postobj.owner.facebook_id.split()[0] not in friendlist:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                                #"text":'<p>You are not allowed to reserve this post.</p>\
                                                                                    #<p>Please go back or click OK to go to the homepage</p>',"link":'/'}))
    #tempres = Reserved.objects.filter(reserver=reserver, post=postobj)
    
    #for x in Post.objects.filter(owner=reserver, status__lte=1):
        #if math.fabs((x.date_time.replace(tzinfo=None)-postobj.date_time.replace(tzinfo=None)).total_seconds()) < 900:
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                                    #"text":'<p>You already have a trip within 15 minutes of this request.</p>\
                                                                                    #<p>Please go back or click OK to go to the homepage</p>', "link":'/'}))
    #entry = Reserved(post = postobj, reserver = reserver)
    
    
    ##Check if automatic accept is on
    #if postobj.autoaccept==1:
        ##Check if there are seats available
        #if postobj.total_seats > postobj.reserved_set.aggregate(Sum('status'))['status__sum']:
            #entry.status = 1

    #tempres = Reserved.objects.filter(reserver=reserver)
    #for x in tempres:
        #if x.post == entry.post:
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                                    #"text":'<p>You have already reserved this post.</p>\
                                                                                        #<p>Please go back or click OK to go to the homepage</p>',"link":'/'}))
        #if math.fabs((x.post.date_time.replace(tzinfo=None)-postobj.date_time.replace(tzinfo=None)).total_seconds()) < 900 and x.status<=1:
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                                    #"text":'<p>Reservation request successfully</p>\
                                                                                        #<p><h5 style="color:red">Note: You already have a reservation within 15 minutes of this request. If any reservation of yours gets confirmed, all other reservations within 15 minutes of this reservation will get cancelled.</h5></p>\
                                                                                        #<br>\
                                                                                    #<p>Please go back or click OK to go to the homepage</p>',"link":'/'}))
            #entry.save()
    #entry.save()
    #if len(entry.post.owner.facebook_id) > MIN_FBID_LEN:
        #fb_notif(entry.post.owner.facebook_id.split()[0], request.user.first_name + " " + request.user.last_name + " has requested to travel with you from " + entry.post.fro + " to " + entry.post.to + " on " + str(entry.post.date_time.date()) + " at " + str(entry.post.date_time.time()))
    #send_email("Subject:New Reservation Request\n\n" + request.user.first_name + " " + request.user.last_name + " has requested to travel with you from " + entry.post.fro + " to " + entry.post.to + " on " + str(entry.post.date_time.date()) + " at " + str(entry.post.date_time.time()) + ".\n Click " + website + "/post_page?key=" + str(entry.post.pk) + " to go to the post.", postobj.owner.user.email)
    
        
    
    #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                          #"text":'<p>Reservation request successfully sent.</p>\
                                                                              #<p>Please go back or click OK to go to the homepage</p>', "link":'/'}))

##Called when a user's reservation request is accepted. An email is also sent to him apart from featuring on his dashboard. After this, the user can print receipt.                                                                               
#def accept(request):
    ##check for user login
    #retval = check(request)
    #if retval <> None:
        #return retval
    #resid = request.REQUEST['resid']
    #owner = request.user.author
    #resobj = Reserved.objects.get(pk=resid)
    
    #postobj = resobj.post
    #if postobj.total_seats > postobj.reserved_set.aggregate(Sum('status'))['status__sum']:
        #resobj.status = 1
        #for x in Reserved.objects.filter(reserver=resobj.reserver):
            #if math.fabs((x.post.date_time-resobj.post.date_time).total_seconds()) < 900 and x.post.status <= 1:
                #dumptofile(x)
                #x.delete()
        #resobj.save()
        #send_email("Subject:Reservation Confirmed\n\nYour reservation with " + postobj.owner.user.first_name + " " + postobj.owner.user.last_name + " from " + postobj.fro + " to " + postobj.to + " on " + str(postobj.date_time.date()) + " at " + str(postobj.date_time.time()) + " has been confirmed.\n Click " + website + "/post_page?key=" + str(postobj.pk) + " to go to the post.", resobj.reserver.user.email)
        #if len(resobj.reserver.facebook_id) > MIN_FBID_LEN:
            #fb_notif(resobj.reserver.facebook_id.split()[0], "Your reservation with " + postobj.owner.user.first_name + " " + postobj.owner.user.last_name + " from " + postobj.fro + " to " + postobj.to + " on " + str(postobj.date_time.date()) + " at " + str(postobj.date_time.time()) + " has been confirmed")
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author, "text":'Accepted request. Click OK to go back to the post.',"link":'/post_page/?key=' + str(postobj.pk)}))
    #else:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                                #"text":'Seats full. Please go back or click OK to go to the homepage',"link":'/'}))
   
##Called when a user cancels a reserver's request. Opposite of accept.
#def revoke(request):
    ##check for user login
    #retval = check(request)
    #if retval <> None:
        #return retval
    
    #try:
        #owner = request.user.author
        #resid = request.REQUEST['resid']
        #try:
            #Reserved.objects.get(pk=resid)
        #except Exception as e:
            #return HttpResponse(e)
        #resobj = Reserved.objects.get(pk=resid)
        #if resobj.post.date_time < timezone.now():
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                           #"text":'<p>Trip already started, cannot reserve now.</p>\
                                                                               #<p>Please go back or click OK to go to the homepage</p>',"link":'/'}))
        
        #postobj = resobj.post
        #dumptofile(resobj)
        #resobj.delete()
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                            #"text":'<p>Cancelled reservation successfully.</p>\
                                                                                #<p>Click OK to go back to the post.</p>',"link":'/post_page/?key=' + str(resobj.post.pk)}))
        
    #except Exception as e:
        #return HttpResponse(e)

##Called when a user cancels his reservation or reservation request.                                                                              
#def cancel_res(request):
    ##check for user login    
    #retval = check(request)
    #if retval <> None:
        #return retval

    #try:
        #reserver = request.user.author
        #resid = request.REQUEST['resid']
        #resobj = Reserved.objects.get(pk=resid)
        
        #if resobj.reserver.pk == reserver.pk:
            #dumptofile(resobj)
            #resobj.delete()
        #else:
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                                  #"text":'Invalid User. Please go back or click OK to go to the homepage',"link":'/'}))
        #if resobj.post.date_time < timezone.now():
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                           #"text":'<p>Trip already started, cannot reserve now.</p>\
                                                                               #<p>Please go back or click OK to go to the homepage</p>',"link":'/'}))
        
    #except Exception as e:
        #return HttpResponse(e)
    #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                          #"text":'<p>Reservation cancelled successfully.</p>\
                                                                              #<p>Please go back or click OK to go to the homepage</p>', "link":'/'}))

#Called when a user searches for a particular trip.                                                                              
@csrf_exempt
def search_do(request):
    global month
    #check for user login
    author = None
    if request.user.is_authenticated():
        author = request.user.author
    
    #Get batch number. Results are displayed in batches. Not all results are displayed on same page.
    #batch = 0
    #if 'batch' in request.REQUEST.keys():
        #batch = int(request.REQUEST['batch'])
    
    ##batch length
    #batchlen=100
    #if 'batchlen' in request.REQUEST.keys():
        #batchlen = int(request.REQUEST['batchlen'])
    
    #fbgroup = ""
    #if "fbgroup" in request.REQUEST.keys():
        #fbgroup = request.REQUEST.keys()
    
    name = request.REQUEST['name']
    #to = request.REQUEST['to']

    #Date and time format: dd mm yyyy - hh:mm
    #start_date_time=Post.objects.filter(status__lte=1).aggregate(Min('date_time'))['date_time__min']
    #if request.REQUEST['start_date_time']<>'':
        #start_date_time=request.REQUEST['start_date_time']
        #start_date_time=start_date_time.split(' ')
        #startdate=start_date_time[0:3]
        #starttime=start_date_time[4]
        #starttime=starttime.split(':')
        #start_date_time = datetime.datetime(day=int(startdate[0]),
                                            #month=month.index(startdate[1]), 
                                            #year=int(startdate[2]), 
                                            #hour=int(starttime[0]),
                                            #minute=int(starttime[1]), 
                                            #second=0, 
                                            #microsecond=0,)

    #end_date_time=Post.objects.filter(status__lte=1).aggregate(Max('date_time'))['date_time__max']
    #if request.REQUEST['end_date_time']<>'':
        #end_date_time=request.REQUEST['end_date_time']
        #end_date_time=end_date_time.split(' ')
        #enddate=end_date_time[0:3]
        #endtime=end_date_time[4]
        #endtime=endtime.split(':')
        #end_date_time = datetime.datetime(day=int(enddate[0]),
                                          #month=month.index(enddate[1]), 
                                          #year=int(enddate[2]), 
                                          #hour=int(endtime[0]),
                                          #minute=int(endtime[1]), 
                                          #second=0, 
                                          #microsecond=0,)
    
    #men_women=request.REQUEST['men_women']
    result=Recipe.objects.filter(name=name)
    #def iterate(fro,to,men_women,start_date_time,end_date_time,pobject):
        #results=[]
        #if men_women <> "0":
            #if end_date_time==None and start_date_time==None:
                #results = pobject.filter(fro__icontains=fro, to__icontains=to, men_women=int(men_women), status__lte=1)
            #elif end_date_time==None and not start_date_time==None:
                #results = pobject.filter(fro__icontains=fro, to__icontains=to, date_time__gte=start_date_time, men_women=int(men_women), status__lte=1)
            #elif (not end_date_time==None) and start_date_time==None:
                #results = pobject.filter(fro__icontains=fro, to__icontains=to, date_time__lte=end_date_time, men_women=int(men_women), status__lte=1)
            #else:
                #results = pobject.filter(fro__icontains=fro, to__icontains=to, date_time__lte=end_date_time, date_time__gte=start_date_time, men_women=int(men_women), status__lte=1)
        #else:
            #if end_date_time==None and start_date_time==None:
                #results = pobject.filter(fro__icontains=fro, to__icontains=to, status__lte=1)
            #elif end_date_time==None and not start_date_time==None:
                #results = pobject.filter(fro__icontains=fro, to__icontains=to, date_time__gte=start_date_time, status__lte=1)
            #elif (not end_date_time==None) and start_date_time==None:
                #results = pobject.filter(fro__icontains=fro, to__icontains=to, date_time__lte=end_date_time, status__lte=1)
            #else:
                #results = pobject.filter(fro__icontains=fro, to__icontains=to, date_time__lte=end_date_time, date_time__gte=start_date_time, status__lte=1)
        #return results

    #resultlist=[]
    ##Exact string match search
    #resultlist+=iterate(fro,to,men_women,start_date_time,end_date_time,Post.objects)
    #fro1=fro.split(', ')
    #to1=to.split(', ')
    #if len(fro1) <3 or len(to1) <3 :
        #if author <> None:
            #return HttpResponse(jinja_environ.get_template('notice.html').render({'author':request.user.author, "text":'Please be more specific in your search. Click OK to go back to homepage',"link":'/'}))
        #else:
            #return HttpResponse(jinja_environ.get_template('notice.html').render({'author':None, "text":'Please be more specific in your search. Click OK to go back to homepage', "link":'/'}))

    #fro2=fro1[-3] +", "+ fro1[-2] +", "+ fro1[-1]
    #to2=to1[-3] +", "+ to1[-2] +", "+ to1[-1]

    #pobject=iterate(fro2,to2,men_women,start_date_time,end_date_time,Post.objects)
    
    ##In the following lines all results are searched based not only on exact string but on area and city too.
    #if len(fro1)>3 and len(to1)>3:
        #resultlist+=iterate(fro1[0],to1[0],men_women,start_date_time,end_date_time,pobject)
    #elif len(fro1)>3 and len(to1)<3:
        #resultlist+=iterate(fro1[0],to1[0],men_women,start_date_time,end_date_time,pobject)
    #elif len(fro1)<3 and len(to1)>3:
        #resultlist+=iterate(fro1[0],to1[0],men_women,start_date_time,end_date_time,pobject)
        
    #if len(fro1)>4 and len(to1)>4:
        #resultlist+=iterate(fro1[1],to1[1],men_women,start_date_time,end_date_time,pobject)
    #elif len(fro1)>4 and len(to1)<4:
        #resultlist+=iterate(fro1[1],to1[1],men_women,start_date_time,end_date_time,pobject)
    #elif len(fro1)<4 and len(to1)>4:
        #resultlist+=iterate(fro1[1],to1[1],men_women,start_date_time,end_date_time,pobject)
        
    #if len(fro1)>5 and len(to1)>5:
        #resultlist+=iterate(fro1[2],to1[2],men_women,start_date_time,end_date_time,pobject)
    #elif len(fro1)>5 and len(to1)<5:
        #resultlist+=iterate(fro1[2],to1[2],men_women,start_date_time,end_date_time,pobject)
    #elif len(fro1)<5 and len(to1)>5:
        #resultlist+=iterate(fro1[2],to1[2],men_women,start_date_time,end_date_time,pobject)
    
    ##add2results(fro,to)
    ##add2results(fro,point1)
    ##add2results(fro,point2)
    ##add2results(point1,point2)
    ##add2results(point1,to)
    ##add2results(point2,to)
    ##resultlist = list(set(resultlist))
    
    ##friendlist = []
    ##if author <> None:
        ##if len(request.user.author.facebook_id.split()) > 0:
            ##friendlist += [request.user.author.facebook_id.split()[0]]
        ##if len(request.user.author.facebook_id.split()) > 0:
            ##templist = []
            ##try:
                ##templist = GraphAPI(request.user.author.facebook_id.split()[1]).get_connections("me","friends")['data']
            ##except:
                ##pass
            ##for x in templist:
                ##friendlist += [x['id']]
        
    ##resultlist+=pobject
    ##resultlist=list(set(resultlist))
    #template_values = {
    #"author":author,
    #'result_list':resultlist[batch*batchlen:(batch+1)*batchlen],
    #'searched':Post(to=to, fro=fro),
    #'batch':batch,
    #'batchlen':batchlen,
    #'friendlist':friendlist,
    #'facebook_only': 'facebook_only' in request.REQUEST.keys(),
    #'fbgroup': fbgroup,
    #}
    
    return HttpResponse(jinja_environ.get_template('searchresult.html').render(result))
     
#Called when a user edits his/her post. If there already are reservers, the user gets a negative flag.
#@csrf_exempt
#def edit_post(request):
    #retval = check(request)
    #if retval <> None:
        #return retval
    
    #owner = request.user.author
    #postid = request.REQUEST['postid']
    #postobj = None
    #try:
        #postobj = Post.objects.get(pk=postid, status__lte=1, date_time__gte=timezone.now())
    #except Exception as e:
        #return HttpResponse(e)
    
    #if postobj.owner.user.username <> owner.user.username:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author, 
                                                                              #"text":'Invalid User. Please go back or click OK to go to the homepage',"link": '/'}))
    #if postobj.date_time < timezone.now():
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'The trip has started, cannot edit post anymore. Please go back or click OK to go to the homepage', "link":'/'}))

    #car_number = request.REQUEST['car_number']
    #if car_number.strip() == '':
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'Invalid Car number. Please go back or click OK to go to the homepage', "link":'/'}))
    #total_seats = int(request.REQUEST['total_seats'])
    #phone = request.REQUEST['phone']
    #remarks = request.REQUEST['remarks']
    #autoaccept = 0
    #try:
        #autoaccept += int(request.REQUEST['autoaccept'])
    #except:
        #pass
    
    #date_time=request.REQUEST['date_time']
    #date_time=date_time.split(' ')
    #date=date_time[0:3]
    #time=date_time[4]
    #time=time.split(':')
    
    #date_time = datetime.datetime(day=int(date[0]),
                                  #month=month.index(date[1]), 
                                  #year=int(date[2]), 
                                  #hour=int(time[0]),
                                  #minute=int(time[1]), 
                                  #second=0, 
                                  #microsecond=0,)
    
    #ac = int(request.REQUEST['ac'])
    #men_women = int(request.REQUEST['men_women'])
    #available_to = int(request.REQUEST['available_to'])
    
    #if total_seats < postobj.reserved_set.aggregate(Sum('status'))['status__sum']:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'You already have more reserved users than seats. So, you can\'t change now. Please go back or click OK to go to the homepage',"link":'/'}))
    
    #postobj.car_number = car_number
    #postobj.total_seats = total_seats
    #postobj.phone = phone
    #postobj.date_time = date_time
    #postobj.ac = ac
    #postobj.men_women = men_women
    #postobj.available_to = available_to
    #postobj.autoaccept = autoaccept
    #postobj.remarks = remarks
    
    #postobj.save()
    #neg = 0
    #for x in postobj.reserved_set.all():
        #if x.edited == 0:
            #if x.status == 1:
                #neg = 1
        #x.edited = 1
        #x.save()
        #send_email("Subject:Post Edited\n\nYour trip from " + postobj.fro + " to " + postobj.to + " on " + str(postobj.date_time.date()) + " at " + str(postobj.date_time.time()) + " has been edited by the owner.\n Click " + website + "/post_page/?key=" + str(postobj.pk) + " to go to post.", x.reserver.user.email)
        #if len(x.reserver.facebook_id) > MIN_FBID_LEN:
            #fb_notif(x.reserver.facebook_id.split()[0], "Your trip from " + postobj.fro + " to " + postobj.to + " on " + str(postobj.date_time.date()) + " at " + str(postobj.date_time.time()) + " has been edited by the owner")
    #postobj.owner.neg_flags += neg
    #postobj.owner.save()
    #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                          #"text":'Post edited successfully. Click OK to view the post.', "link": '/post_page/?key=' + str(postobj.id)}))

##To reset the editted flag if the reservers are okay with the change.                                                                          
#@csrf_exempt
#def reset_edited(request):
    #retval = check(request)
    #if retval <> None:
        #return retval
    #resobj = Reserved.objects.filter(pk=request.REQUEST['resid'])
    #if len(resobj) == 0:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'Invalid Request. Click OK to the post details page', "link":'/'}))
    #resobj[0].edited = 0
    #resobj[0].save()
    #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                          #"text":'Done. Click OK to the post details page', "link":'/'}))

##Can be called from multiple places. It is used to send message from one user to another (Not to be confused with send email, which is to send from system to user's email ID 
#@csrf_exempt
#def send_message(request):
    ##check for user login
    #retval = check(request)
    #if retval <> None:
        #return retval
    
    #sender = request.user.author
    #try:
        #receiver = User.objects.get(username=request.REQUEST['to']).author
        #message = request.REQUEST['message']
        #message = message[:min(300,len(message))]
        #if sender==receiver:
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author, "text": 'Sending messages to self is a sign of narcissism. Click OK to go back to homepage.', "link":'/'}))

        #else:
            #entry = Message(sender = sender, receiver = receiver, message = message)
            #entry.save()
            
    #except Exception as e:
        #return HttpResponse(e)
    #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                          #"text":'Message Sent. Please go back or click OK to go to the homepage', "link":'/'}))

##Call function for inbox. Used to display all the messages sent to the user.                                                                          
#def view_messages(request):
    ##check for user login
    #retval = check(request)
    #if retval <> None:
        #return retval
    
    #author = request.user.author
    #results1 = Message.objects.filter(sender = author)
    #results2 = Message.objects.filter(receiver = author)
    
    #return HttpResponse((len(results1) + len(results2)))

##Used to display the message content in a side tab.
#@csrf_exempt
#def read_message(request):
  
    #retval = check(request)
    #if retval <> None:
        #return retval
    
    #key = request.REQUEST["mid"]
    
    #try:
        #result = Message.objects.filter(pk=mid)
        #result.rmailbox=2
        #result.save()
        #return HttpResponse("1")
    #except Exception as e:
        #return HttpResponse("0"+str(e))
        
##Called when a user deletes a message       
#@csrf_exempt
#def delete_message(request):
    ##check for user login
    #retval = check(request)
    #if retval <> None:
        #return retval
    
    #author = request.user.author
    #mids = request.REQUEST['mids']
    #mids = mids.split(',')
    #print mids
    #for mid in mids:
        #message = None
        
        #try:
            #message = Message.objects.get(pk=int(mid))
        #except:
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                            #"text":'No such message exists! Please go back or click OK to go to the homepage', "link":'/'}))
                                            
        #if message.receiver.pk == author.pk:
            #message.rmailbox = 0
            ##Kept for future use. Please Ignore.
            ## if message.rmailbox + message.smailbox == 0:
            ##This means the message has been deleted from both the sender and the receiver's side.
            ##The message will be deleted after one month
            ##if message.date_time.month - timezone.now().month >= 1:
            ##message.delete()
            
            ##For now, message will be deleted. In the future, we may implement restoring of messages, in which case
            ##We will keep the delete after one month feature.
            #dumptofile(message)
            #message.delete()
        #else:
            #message.save()
    #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                            #"text":'<p>Messege deleted successfully.</p>\
                                            #<p>Please go back or click OK to go to the homepage</p>', "link":'/'}))
        
##Reply to a message which has been sent by some user
#@csrf_exempt
#def reply(request):
    #retval = check(request)
    #if retval <> None:
        #return retval
    
    #mid = request.POST['mid']
    #message = request.POST['message']
    #receiver = None
    #try:
        #receiver = Message.objects.get(pk=int(mid)).sender
    #except:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'<p>Message not found.</p>\
                                                                                  #<p>Please go back or click OK to go to the homepage</p>', "link":'/'}))
    #entry = Message(sender = request.user.author, receiver = receiver, message = message)
    #entry.save()
    
    #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                          #"text":'<p>Message sent successfully.</p>\
                                                                              #<p>Please go back or click OK to go to the homepage</p>', "link":'/'}))

##Search for username
#@csrf_exempt
#def search(request):
    #if True:
        #if request.REQUEST['search'] == 'phone':
            #return HttpResponse("0")
        #elif request.REQUEST['search'] == 'username':
            #if len(User.objects.filter(username=request.REQUEST['username'])) <> 0:
                #return HttpResponse("1")
            #return HttpResponse("0")
        #elif request.REQUEST['search'] == 'email':
            #if len(User.objects.filter(email=request.REQUEST['email'])) <> 0:
                #return HttpResponse("1")
            #else:
                #return HttpResponse("0")

##Save facebook token. Will be used in facebook integration
#@csrf_exempt
#def facebook(request):
    #retval = check(request)
    #if retval <> None:
        #return retval
    #if request.method == "POST":
        #if "access_token" in request.REQUEST.keys():
            #fobj = []
            #try:
                #fbobj = GraphAPI(str(request.REQUEST['access_token']))
                ##return HttpResponse(fbobj.get_object("me")['id'])
                #fbid = fbobj.get_object("me")['id']
                #tempauthors = Author.objects.filter(facebook_id__contains = fbid)
                #if len(tempauthors) > 0:
                    #if tempauthors[0].id <> request.user.author.id:
                        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                                #"text":'Facebook account already synced with another user.' , "link": '/'}))
                #request.user.author.facebook_id = fbid + " " + request.REQUEST['access_token']
                #request.user.author.save()
                #x = urllib.urlopen('https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=1402875186650026&client_secret=0ebf2416ad64da0d0484eeaebdefc5b9&fb_exchange_token=' + request.REQUEST['access_token'])
                #x = x.read()
                #x = x[x.find('=')+1:x.rfind('&')]
                #request.user.author.facebook_id = fbid + " " + x
            #except:
                #pass
            ##Update friendlist
            #friendlist = []
            #try:
                #friendlist = GraphAPI(x).get_connections("me","friends")['data']
            #except:
                #pass
            #for z in friendlist:
                #for y in Author.objects.filter(facebook_id__contains=z['id']):
                    #request.user.author.fbfriends.add(y)
            
            
            #request.user.author.save()
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'Integrated with facebook friends successfully.' , "link": '/'}))
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'Could not connect to facebook. Please try again later' , "link": '/'}))
    #return HttpResponse(jinja_environ.get_template('facebook.html').render({"author":request.user.author, "text": request.get_full_path()}))


##Called when a user clicks delete account on settings page. It deletes the user's account and related items from database.
#def delete_account(request):
    #retval = check(request)
    #if 'confirm' not in request.REQUEST.keys():
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'<p>Please go back and enter confirmation text properly to delete account.</p>',"link":'/'}))
    #if request.REQUEST['confirm'] <> "I AM SURE I WANT TO DELETE THIS ACCOUNT":
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'<p>Please go back and enter confirmation text properly to delete account.</p>',"link":'/'}))
    #if retval <> None:
        #return retval
    ##checking
    #if request.REQUEST['username'] <> request.user.username or request.REQUEST['email'] <> request.user.email <> request.REQUEST['car_number'] <> request.user.author.car_number:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                              #"text":'<p>Message sent successfully.</p>\
                                                                                  #<p>Please go back or click OK to go to the homepage</p>',"link":'/'}))
    #for x in Message.objects.filter(sender=request.user.author):
        #dumptofile(x)
        #x.delete()
    #for x in Message.objects.filter(receiver=request.user.author):
        #dumptofile(x)
        #x.delete()
    #for x in Reserved.objects.filter(reserver=request.user.author):
        #dumptofile(x)
        #x.delete()
    #for x in Post.objects.filter(owner=request.user.author):
        #dumptofile(x)
        #x.delete()
    #dumptofile(request.user.author)
    #request.user.author.delete()
    #dumptofile(request.user)
    #request.user.delete()
    #logout(request)
    #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":None,
                                                                          #"text":'<p>Account Deleted Successfully.</p>\
                                                                              #<p>Please go back or click OK to go to the homepage</p>',"link":'/'}))

##Called when a user clicks submit button on invite friends page. The email-IDs are split by , and then stripped and then emails are sent.                                                                            
#@csrf_exempt
#def invite(request):

    #retval = check(request)
    #if retval <> None:
        #return retval
      
    #try:
        #email=request.REQUEST['email_id']
        #email=email.split(',')
        #email = list(set(email))
        #for i in range(0,len(email)):
            #email[i]=email[i].strip();
            
        #author=request.user.author
        #message=request.REQUEST['message']
        #message="Subject:RideBuddy.co Invitation\n" + author.user.first_name + " " + author.user.last_name + " has invited you to join RideBuddy!\n\n" + author.user.first_name + " says:\n" + message + "\n\nClick " + website + " to visit the website."
      
        #for i in range(0,len(email)):
            #x = send_email(message, email[i])
        #try:
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                                  #"text":'<p>Emails Sent Successfully.</p>\
                                                                                      #<p>Please go back or click OK to go to the homepage</p>',"link":'/'}))
        #except:
            #pass
    #except Exception as e:
        #try:
            #return HttpResponse(e)
        #except:
            #pass


##Called when a user clicks report user from dashboard when his/her reserved trip is cancelled. This add 1 to the number of user reports.
#def report_user(request):
    #retval = check(request)
    #if retval <> None:
        #return retval
        
    #if 'user' not in request.REQUEST.keys():
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                                  #"text":'<p>Invalid user.</p>\
                                                                                      #<p>Please go back or click OK to go to the homepage</p>', "link":'/'}))
    #user = User.objects.filter(username=request.REQUEST['user'])
    #if len(user)==0:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                                  #"text":'<p>Invalid user.</p>\
                                                                                      #<p>Please go back or click OK to go to the homepage</p>', "link":'/'}))    
    
    #user = user[0]
    #flag=Rating.objects.filter(rated=user.author, rater=request.user.author)
    
    #if len(flag) == 0 and len(flag) <5:
        #user.author.user_rating += 1
        #user.author.save()
        #rateobj=Rating(rated=user.author, rater=request.user.author)
        #rateobj.save()
    
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                          #"text":'<p>User reported successfully.</p>\
                                                                              #<p>Please go back or click OK to go to the homepage</p>', "link":'/'}))
    #else:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"author":request.user.author,
                                                                          #"text":'<p>You have already reported this user and can\'t report again. </p>\
                                                                          #<p>Please go back or click OK to go to the homepage</p>', "link":'/'}))

##Testing functions: These are used by us for testing. Not userful otherwise.
#def tempage(request):
    
    ## Do what you want with it - pass it to the template or print it!
    #return HttpResponse(fb_notif(request.user.author.facebook_id.split()[0], "hi"))
    
