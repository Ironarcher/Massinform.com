from django.db import models

# Create your models here.

class ContactList(models.Model):
	listname = models.CharField(max_length=100)

	#List of every contact
	firstnames = models.TextField(default="[]")
	lastnames = models.TextField(default="[]")
	phonenumbers = models.TextField(default="[]")
	emailaddresses = models.TextField(default="[]")

	recentnotifications = models.TextField(default="[]")
	#Times corresponding to every notification about when it was sent
	rnottimes = models.TextField(default="[]")

	def __unicode__(self):
		return self.listname