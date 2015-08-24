from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import json
import hashlib

# Create your models here.

class UserProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
	contact_list_ids = models.TextField(default="[]")

	def __unicode__ (self):
		return self.user.username

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])