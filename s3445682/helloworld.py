from google.appengine.ext import ndb
from google.appengine.api import users
import os
import urllib
import logging
import jinja2
import webapp2
from datetime import datetime
import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'])

class MainPage (webapp2.RequestHandler):
 def get(self):
   cats_query = Cat.query().order(-Cat.date_of_birth)
   cats = cats_query.fetch(10)
   logging.info("Num cats: %s", str(len(cats)))
   template_values = {
     'cats': cats,
   }
   template = JINJA_ENVIRONMENT.get_template('index.html')
   self.response.write(template.render(template_values))
 def post(self):
   owner_name = self.request.get("owner")
   #first look for an existing owner
   owner = Owner.query(Owner.name == owner_name).get()
   if not owner:
     owner = Owner()
     owner.name = owner_name
     owner.put()
     logging.info("Added owner: %s", owner.key)
   cat = Cat()
   cat.owner = owner.key
   cat.name = self.request.get('name')
   cat.description = self.request.get('description')
   day = self.request.get('day')
   month = self.request.get('month')
   year = self.request.get('year')
   cat.date_of_birth = datetime.date(year=int(year), month=int(month), day=int(day))
   # store the data
   cat.put()
   logging.info("Added cat: %s", cat.key)
   self.redirect('/')

			
class CatPage(webapp2.RequestHandler):
 def get(self):
   name = self.request.get("name")   
   logging.info("Name is: %s", name)
   if name is None:
     logging.info("No name supplied, redirecting...")
     self.redirect('/')
   cat = Cat.query(Cat.name == name).get()
   if cat is None:
     logging.info("Cannot find cat with name %s, redirecting...", name)
     self.redirect('/')
   # so we have a cat
   template_values = {
     'cat': cat,
   }
   template = JINJA_ENVIRONMENT.get_template('cat.html')
   self.response.write(template.render(template_values))
 def post(self, name):
   if name is None:
     logging.info("No name supplied, redirecting...")
     self.redirect('/')
   cat = Cat.query(Cat.name == name).get()
   if cat is None:
     logging.info("Cannot find cat with name %s, redirecting...", name)
     self.redirect('/')
   # find the 'owner'
   owner_name = self.request.get("owner")
   #first look for an existing owner
   owner = Owner.query(Owner.name == owner_name).get()
   # need to add the owner
   if not owner:
     owner = Owner()
     owner.name = owner_name
     owner.put()
     logging.info("Added owner: %s", owner.key)
   # update the cat
   cat.owner = owner.key
   cat.name = self.request.get('name')
   cat.description = self.request.get('description')
   day = self.request.get('day')
   month = self.request.get('month')
   year = self.request.get('year')
   cat.date_of_birth = datetime.date(year=int(year), month=int(month), day=int(day))
   cat.put()
   # redirect to home page
   self.redirect('/') 
 def delete(self, cat_name):
   logging.info("in delete")
   if cat_name is None:
     self.response.out.write("NOT OK")
   logging.info("Name is: %s", cat_name)
   cat = Cat.query(Cat.name == cat_name).get()
   if cat is None:
     self.response.out.write("NOT OK")
   cat.key.delete()
   self.response.out.write("OK")
		
		
class MyCatsPage(webapp2.RequestHandler):
 def get(self):
   owner_name = self.request.get("name")
   if owner_name:
     # restrict query to the cats of this owner
     owner = Owner.query(Owner.name == owner_name).get()
     if owner:
       logging.info("owner: %s", owner.name)
       cats_query = Cat.query(Cat.owner == owner.key)
     else:
       logging.info("no owner found with name: %s", owner_name)
       cats_query = Cat.query()
   else:
     # get all the cats
     cats_query = Cat.query()
   # actually fetch the cats (restrict to last 10)
   cats = cats_query.fetch(10)
   template_values = {
     'cats': cats,
   }
   template = JINJA_ENVIRONMENT.get_template('my_cats.html')
   self.response.write(template.render(template_values))		
	

	

class OwnersPage(webapp2.RequestHandler):
 def get(self):
   cat_owners = Owner.query()
   template_values = {
   'cat_owners': cat_owners
   }
   template = JINJA_ENVIRONMENT.get_template('owners.html')
   self.response.write(template.render(template_values))
			

	

	
			
class Owner(ndb.Model):
 """Models a cat owner record"""
 name = ndb.StringProperty()	
	
class Cat(ndb.Model):
 """Models a single Cat to record"""
 owner = ndb.KeyProperty(kind=Owner)
 name = ndb.StringProperty()
 description = ndb.StringProperty(indexed=False)
 date_of_birth = ndb.DateProperty()	
	
	
	
application = webapp2.WSGIApplication([
   ('/', MainPage),
   ('/cats', MyCatsPage),
   ('/owners', OwnersPage),
   (r'/cat/(\w+)', CatPage),
], debug=True)
		
	
	
	

