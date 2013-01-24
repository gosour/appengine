import os
import re

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

def valid_day(day):
    try:
        int(day)
    except ValueError:
        return None
    else:
        if int(day) <= 31 and int(day) >=1:
            return int(day)
        else:
            return None

def valid_year(year):
    if year.isdigit() and int(year) in range(1900, 2021):
        return int(year)
    else: return None

def valid_month(month):
    months = ['January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December']
    if month.lower() in [m.lower() for m in months]:
        return months[ [m.lower() for m in months].index(month.lower()) ]
    else:
        return None

def rot13fy(text):
	lowers = [i+13 for i in range(ord('a'), ord('z') +1) if (i+13)<=ord('z')]
	lowers = lowers + [(i+13)%ord('z')+ord('a') -1 for i in range(ord('a'), ord('z') +1) if (i+13)>ord('z')]
	uppers = [i+13 for i in range(ord('A'), ord('Z') +1) if (i+13)<=ord('Z')]
	uppers = uppers + [(i+13)%ord('Z')+ord('A') -1 for i in range(ord('A'), ord('Z') +1) if (i+13)>ord('z')]

	lowerdict = dict(map(lambda (x,y): (chr(x),chr(y)), zip([org for org in range(ord('a'),ord('z')+1)],lowers)))
	upperdict = dict(map(lambda (x,y): (chr(x),chr(y)), zip([org for org in range(ord('A'),ord('Z')+1)],uppers)))

	totaldict = dict(lowerdict.items()+upperdict.items())
	
	newtext = ''
	for char in text:
		if char in totaldict:
			newtext = newtext + totaldict[char]
		else:
			newtext = newtext + char
	
	return newtext


class BaseHandler(webapp2.RequestHandler):
    def render_str(self,template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self,template,**kw):
        self.response.write(self.render_str(template, **kw))
    def write(self,*a,**kw):
        self.response.write(*a, **kw)

class MainPage(BaseHandler):
	def get(self):
		self.render('home.html',username="")

class FormPage(BaseHandler):
    def write_form(self,error='',month='',day='',year=''):
        self.render('formcheck.html',error=error,day=day,year=year,month=month)

    def get(self):
        self.render('formcheck.html')
   
    def post(self): #when we post our form
        user_month = self.request.get('month')
        user_day = self.request.get('day')
        user_year = self.request.get('year')

        month = valid_month(user_month)
        year = valid_year(user_year)
        day = valid_day(user_day)
        if not(month and year and day):
            self.write_form(error="THIS IS NOT WHAT I WANT! GODDAMIT!",
                            day=user_day,
                            month=user_month,
                            year=user_year)
        else:
            self.redirect('/thanks')      

class ThanksHandler(BaseHandler):
    def get(self):
        self.write('<b>You are awesome!</b>')


class RotHandler(BaseHandler):
	def get(self):
		self.render('rot13.html')
	def post(self):
		txt = self.request.get('text')
		outputxt = rot13fy(txt)
		self.render('rot13.html',text=outputxt)

class Art(db.Model):
    #property_name = db.TypeProperty
    title = db.StringProperty(required = True)
    art = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)

class AsciiChan(BaseHandler):
    def ascii_front(self,title="",art = "", error = ""):
        arts = db.GqlQuery('SELECT * FROM Art ORDER BY created DESC')
        self.render("asciichan.html",title=title,art = art, error = error, arts = arts)

    def get(self):
        self.ascii_front()

    def post(self):
        title = self.request.get('title')
        art = self.request.get('art')
        if title and art:
            a = Art(title=title, art =art)
            a.put() #stores in the database
            self.redirect('/asciichan')
        else:
            self.render('asciichan.html',error="Both title and art needed!",
                                     title = title,
                                     art = art)

class Blog(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateProperty(auto_now_add = True)

class BlogMainHandler(BaseHandler):
    def get(self):
        blogs = db.GqlQuery('SELECT * FROM Blog ORDER BY created DESC')
        self.render("blog.html",blogs = blogs)

class BlogPostHandler(BaseHandler):
    def blogpostrender(self,error = "", subject = "", content = ""):
        self.render('newpost.html',error = error, subject = subject, content = content)
    def get(self):
        self.blogpostrender()
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        if subject and content:
            content = content.replace('\n','<br>')
            b = Blog(subject = subject, content = content)
            b_key = b.put() # key('Blog',id)
            self.redirect('/blog/%d' %b_key.id())
        else:
            error = "Subject and Content both required"
            self.blogpostrender(error=error,subject= subject, content = content)
        
class Permlink(BaseHandler):
    def get(self,blog_id): #if parentheses in url matcher 
        s = Blog.get_by_id(int(blog_id))
        self.render('blogpost.html',blog = s)

app = webapp2.WSGIApplication([ ('/',MainPage), 
								('/forms',FormPage),
								('/thanks',ThanksHandler),
								('/rot13',RotHandler),
                                ('/asciichan',AsciiChan),
                                ('/blog',BlogMainHandler),
                                ('/blog/newpost',BlogPostHandler),
                                ('/blog/(\d+)', Permlink)
                                ],
								debug=True)

