#Imports
from django.shortcuts import render, redirect
from django.http import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from notify.models import ContactList

import re
import json
import hashlib

# All views relating to users

def login_view(request):
	status = "started"
	username = password = ""
	next = "/notify/"
	if request.GET:
		next = request.GET['next']

	if request.POST:
		first = False
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				status = "success"
				remember = request.POST.getlist('remember[]')
				if "remember" in remember:
					request.session.set_expiry(1209600)
				if next == "":
					return HttpResponseRedirect("/")
				else:
					return HttpResponseRedirect(next)
			else:
				status = "inactive"
		else:
			status = "failed"
	else:
		first = True
	context = {
		"status" : status,
		"first" : first,
		"username_init" : username,
		"password_init" : password,
		"next" : next,
	}
	return render(request, 'usermanage/login.html', context)

def logout_view(request):
	logout(request)
	return HttpResponseRedirect("/")

def register_view(request):
	issues = []
	username = firstname = lastname = password = email = ""
	if request.method == "POST":
		first = False
		username = request.POST['username']
		password = request.POST['password']
		firstname = request.POST['displayname']
		email = request.POST['email']
		if len(username) < 4 or len(username) > 50:
			#Username must be 4-50 characters long
			issues.append("username_length")
		if re.match('^\w+$', username) is None and len(username) != 0:
			#Username can only contain characters and numbers and underscores
			issues.append("username_char")
		if len(password) < 6 or len(password) > 50:
			#Password must be 6-50 characters long
			issues.append("password_length")
		if re.match("^[A-Za-z ]*$", firstname) is None:
			#Names can only contain letters and spaces
			issues.append("firstname_char")
		if len(firstname) < 3 or len(username) > 70:
			#Display name must be 3-70 characters long
			issues.append("firstname_length")
		if re.match("^[A-Za-z0-9@._]*$", email) is None or len(email) < 3:
			#Email invalid
			issues.append("email_char")
		if check_user_exists(username):
			#User already exists
			issues.append("username_taken")
		if check_email_exists(email):
			#Email is already being used
			issues.append("email_taken")

		#Sign the user up
		if len(issues) == 0:
			user = User.objects.create_user(username, email, password)
			if len(firstname) != 0:
				user.first_name = firstname
			userp = user.profile
			userp.contact_list_ids = "[]"
			userp.save()
			print(user.profile.contact_list_ids)
			#Authenticate and login user
			userb = authenticate(username=username, password=password)
			if userb is not None and userb.is_active:
				login(request, userb)
			else:
				print("fatal error")

			#Redirect the user to the verification process
			#TO-DO

			#Create the first contact list
			c = ContactList(listname = firstname + " List", firstnames="[]", lastnames="[]", phonenumbers="[]",
				emailaddresses="[]", recentnotifications="[]", rnottimes="[]")
			c.save()
			addContactList(userb, c)
			print(user.profile.contact_list_ids)
			return HttpResponseRedirect("/notify/")
	else:
		first = True
	print(firstname)
	context = {
		"issues" : issues,
		"first" : first,
		"username_init" : username,
		"password_init" : password,
		"displayname_init" : firstname,
		"email_init" : email,
	}
	return render(request, 'usermanage/register.html', context)

def changepassword_view(request):
	if request.user.is_authenticated():
		issues = []
		oldpassword = newpassword = newpassword_confirm = ""
		if request.method == "POST":
			first = False
			oldpassword = request.POST['oldpassword']
			newpassword = request.POST['newpassword']
			newpassword_confirm = request.POST['newpassword_confirm']
			user = authenticate(username=request.user.get_username(), password=oldpassword)
			if user is None:
				#Wrong old password
				issues.append("wrong_password")
			elif not user.is_active:
				#User is not active
				issues.append("user_inactive")
			if len(newpassword) < 6 or len(newpassword) > 50:
				#Password must be 6-50 characters long
				issues.append("password_length")
			if newpassword != newpassword_confirm:
				#New passwords do not match
				issues.append("password_match")

			#Change the user's password
			if len(issues) == 0:
				user.set_password(newpassword)
				user.save()
				#TODO: Send email that your password has been changed
				#If the password change was not you, reset the account (lock)
				return HttpResponseRedirect("/account/")
		else:
			first = True

		context = {
			"issues" : issues,
			"first" : first,
			"oldpassword_init" : oldpassword,
			"newpassword_init" : newpassword,
			"newpassword_confirm_init" : newpassword_confirm,
		}
		return render(request, 'usermanage/change_password.html', context)
	else:
		return HttpResponseRedirect('/login/?next=/changepassword/')

def reset_view(request):
	pass

def check_user_exists(username):
	if User.objects.filter(username=username).exists():
		return True
	else:
		return False

def check_email_exists(email):
	if User.objects.filter(email=email).exists():
		return True
	else:
		return False

def normalize(number):
	if number > 1000000000:
		return str(round(float(number)/1000000000, 1)) + "b"
	elif number > 1000000:
		return str(round(float(number)/1000000, 1)) + "m"
	elif number > 1000:
		return str(round(float(number)/1000, 1)) + "k"
	else:
		return str(number)

def getContactLists(userprofile):
	try:
		return json.decoder.JSONDecoder().decode(userprofile.contact_list_ids)
	except ValueError:
		return []

def addContactList(user, contactlist):
	userp = user.profile
	clist = getContactLists(userp)
	clist.insert(0, contactlist.id)
	userp.contact_list_ids = json.dumps(clist)
	userp.save()

def deleteContactList(user, contactlist):
	userp = user.profile
	clist = getContactLists(userp)
	if contactlist in clist:
		clist.remove(contactlist.id)
	userp.contact_list_ids = json.dumps(clist)
	userp.save()