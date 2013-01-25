""" All the database junks for the webapp go here"""
from google.appengine.ext import db

class Art(db.Model):
    #property_name = db.TypeProperty
    title = db.StringProperty(required = True)
    art = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)


class Blog(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateProperty(auto_now_add = True)

class User(db.Model):
	username = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	