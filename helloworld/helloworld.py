import os

import webapp2
import jinja2


from webappfunc import *
from webappdatabase import *

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)


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
            self.write_form(error="You cannot even enter dates properly. Shame one you..",
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
        if not s:
            self.error(404)
            return

        self.render('blogpost.html',blog = s)

class Signup(BaseHandler):
    def get(self):
        self.render('signupform.html')
    def post(self):
        have_error = False
        error = ""
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(  username = username,
                        email = email,
                        error= error)

        if not valid_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        user = db.GqlQuery('SELECT * FROM User WHERE username = \'%s\'' %(username))
        result = user.get()
        if result:
            params['error'] = "Username exists!"
            have_error = True

        if have_error:
            self.render('signupform.html',**params)
        else:
            u = User(username=username,password=password)
            u_key = u.put()
            #setcookie
            cookieval = 'username=%s' %(set_cookie(username))
            self.response.headers.add_header('Set-cookie',cookieval.encode('ascii'))
            self.redirect('/signup/welcome')

class Welcome(BaseHandler):
    def get(self):
        cookiestr = self.request.cookies.get('username')
        username = valid_cookie(cookiestr)
        if valid_username(username):
            self.render('welcome.html', username = username)
        else:
            self.redirect('/signup')

class Login(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')

        user = db.GqlQuery('SELECT * FROM User WHERE username = \'%s\' AND password = \'%s\'' %(username,password))
        result = user.get()
        if not result:
            self.render('login.html',error = 'Invalid login', username = username)
        else:
            cookieval = 'username=%s' %(set_cookie(username))
            self.response.headers.add_header('Set-cookie',cookieval.encode('ascii'))
            self.redirect('/signup/welcome')    

class Logout(BaseHandler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'username=; Path=/')
        self.redirect('/signup')  



app = webapp2.WSGIApplication([ ('/',MainPage), 
								('/forms',FormPage),
								('/thanks',ThanksHandler),
								('/rot13',RotHandler),
                                ('/asciichan',AsciiChan),
                                ('/blog',BlogMainHandler),
                                ('/blog/newpost',BlogPostHandler),
                                ('/blog/(\d+)', Permlink),
                                ('/signup',Signup),
                                ('/signup/welcome',Welcome),
                                ('/login',Login),
                                ('/logout',Logout),
                               ],
								debug=True)

