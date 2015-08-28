from django.shortcuts import render, redirect
from django.http import *
from .models import ContactList
from django.contrib.auth.models import User

import json
import smtplib
import sys
import os
import re
import time
from email.MIMEText import MIMEText

# Create your views here.

def index_view2(request):
	if request.user.is_authenticated():
		user = request.user
	else:
		return HttpResponseRedirect("/login?next=/notify/")

	if request.POST:
		notText = request.POST['content']
		clist_id = request.POST['clist_id']
		clist = ContactList.objects.get(id=clist_id)
		notify(clist, notText)
		return HttpResponseRedirect("/notify/")
	else:
		#Collect user information
		c_ids = getUserContactLists(user.profile)
		contactlists = []
		notifications = []
		for cid in c_ids:	
			c = ContactList.objects.get(id=cid)
			if c is not None:
				#Translate data into string object to send to client
				clist = {}
				clist['name'] = c.listname
				firstnames = getFirstNames(c)
				lastnames = getLastNames(c)
				phonenumbers = getPhoneNumbers(c)
				emailaddr = getEmails(c)
				contacts = []
				for i in range(len(firstnames)):
					tempdict = {}
					tempdict['firstname'] = firstnames[i]
					tempdict['lastname'] = lastnames[i]
					tempdict['phonenumber'] = phonenumbers[i]
					tempdict['email'] = emailaddr[i]
					contacts.append(tempdict)
				clist['contacts'] = contacts
				clist['id'] = c.id
				contactlists.append(clist)

				#Get recent notifications and other information
				nots = {}
				nots['text'] = getRecentNots(c)
				nots['times'] = getRecentNotTimes(c)
				nots['clist_name'] = c.listname
				print(nots)
				notifications.append(nots)

		#Get recent notifications
		context = {
			"contactlists" : contactlists,
			"notifications" : notifications,
		}
		return render(request, 'notify/notify.html', context)

#Ajax method
def createContact(request):
	if request.user.is_authenticated():
		#Get data
		if request.GET:
			if 'contactlist' in request.GET:
				clist_id = request.GET['contactlist']
				if 'new_firstname' in request.GET:
					new_firstname = request.GET['new_firstname']
				else:
					new_firstname = ""

				if 'new_lastname' in request.GET:
					new_lastname = request.GET['new_lastname']
				else:
					new_lastname = ""

				if 'new_phonenumber' in request.GET:
					new_phonenumber = request.GET['new_phonenumber']
				else:
					new_phonenumber = ""

				if 'new_email' in request.GET:
					new_email = request.GET['new_email']
				else:
					new_email = ""
				print()
				#Check to make sure the parameters are valid
				if len(new_firstname) != 0 and len(new_firstname) < 4 or len(new_firstname) > 50:
					return;
				elif re.match('[A-Za-z]*$', new_lastname) is None and len(new_lastname) != 0:
					return;
				elif len(new_lastname) and len(new_lastname) < 4 or len(new_lastname) > 50:
					return;
				elif re.match('[A-Za-z]*$', new_lastname) is None and len(new_lastname) != 0:
					print('3')
					return;
				elif len(new_phonenumber) != 10 and len(new_phonenumber) != 0:
					return;
				elif re.match('[0-9]*$', new_phonenumber) is None:
					return;
				elif re.match("^[A-Za-z0-9@._]*$", new_email) is None:
					return;
				elif len(new_email) != 0 and len(new_email) < 3 or len(new_email) > 70:
					return;
				else:
					contactlist = ContactList.objects.get(id=clist_id)
					addToContactList(contactlist, new_firstname, new_lastname, new_phonenumber, new_email)
					return HttpResponse("success")
			else:
				return HttpResponseRedirect('/')
		else:
			return HttpResponseRedirect('/')
	else:
		return HttpResponseRedirect('/')

#Ajax method
def deleteContact(request):
	if request.user.is_authenticated():
		#Get data
		if request.GET:
			if 'contactlist' in request.GET:
				if 'email' in request.GET:
					email = request.GET['email']
				else:
					email = ""

				if 'phonenumber' in request.GET:
					phonenumber = request.GET['phonenumber']
				else:
					phonenumber = ""
				clist_id = request.GET['contactlist']
				removeFromContactList(clist_id, email, phonenumber)
				return HttpResponse("success")
			else:
				return HttpResponseRedirect('/')
		else:
			return HttpResponseRedirect('/')
	else:
		return HttpResponseRedirect('/')

def getContactList(name):
	return ContactList.objects.get(name=name)

def getFirstNames(contactlist):
	try:
		return json.decoder.JSONDecoder().decode(contactlist.firstnames)
	except ValueError:
		return []

def getLastNames(contactlist):
	try:
		return json.decoder.JSONDecoder().decode(contactlist.lastnames)
	except ValueError:
		return [] 

def getPhoneNumbers(contactlist):
	try:
		return json.decoder.JSONDecoder().decode(contactlist.phonenumbers)
	except ValueError:
		return []

def getEmails(contactlist):
	try:
		return json.decoder.JSONDecoder().decode(contactlist.emailaddresses)
	except ValueError:
		return []

#Must have an email address
def addToContactList(contactlist, firstname, lastname, phonenumber, emailaddress):
	email = getEmails(contactlist)
	if emailaddress not in email:
		email.insert(0, emailaddress)
		firstlist = getFirstNames(contactlist)
		firstlist.insert(0, firstname)
		lastlist = getLastNames(contactlist)
		lastlist.insert(0, lastname)
		phonelist = getPhoneNumbers(contactlist)
		phonelist.insert(0, phonenumber)
		#Save all of these lists
		contactlist.firstnames = json.dumps(firstlist)
		contactlist.lastnames = json.dumps(lastlist)
		contactlist.phonenumbers = json.dumps(phonelist)
		contactlist.emailaddresses = json.dumps(email)
		contactlist.save()
	else:
		print("Contact ERROR: Email address already exists")

#Cannot have someone with no email address or the same email address
def removeFromContactList(clist_id, email, phonenumber):
	contactlist = ContactList.objects.get(id=clist_id)
	firstnames = getFirstNames(contactlist)
	lastnames = getLastNames(contactlist)
	phonenumbers = getPhoneNumbers(contactlist)
	emails = getEmails(contactlist)
	if email in emails and email != "":
		position = [i for i, x in enumerate(emails) if x == email][0]
		emails.remove(email)
		firstnames.remove(firstnames[position])
		lastnames.remove(lastnames[position])
		phonenumbers.remove(phonenumbers[position])
		contactlist.emailaddresses = json.dumps(emails)
		contactlist.firstnames = json.dumps(firstnames)
		contactlist.lastnames = json.dumps(lastnames)
		contactlist.phonenumbers = json.dumps(phonenumbers)
		contactlist.save()
	elif phonenumber in phonenumbers:
		position = [i for i, x in enumerate(phonenumbers) if x == phonenumber][0]
		phonenumbers.remove(phonenumber)
		firstnames.remove(firstnames[position])
		lastnames.remove(lastnames[position])
		phonenumbers.remove(phonenumbers[position])
		contactlist.emailaddresses = json.dumps(emails)
		contactlist.firstnames = json.dumps(firstnames)
		contactlist.lastnames = json.dumps(lastnames)
		contactlist.phonenumbers = json.dumps(phonenumbers)
		contactlist.save()

def deleteContactList(clist_id, userprofile):
	contactlist = ContactList.objects.get(id=clist_id)
	#Remove it from the user bank
	deleteUserContactList(userprofile, contactlist)
	contactlist.delete()

def createContactlist(name):
	c = ContactList(name=name)
	c.save()

def notify(contactlist, msg):
	carrierlist = [
		"vtext.com",
		"txt.att.net",
		"messaging.sprintpcs.com",
		"tmomail.net",
		"email.uscc.net",
		"vmobl.com",
	]
	gmail_user = os.environ.get("GMAIL_USER")
	gmail_pwd = os.environ.get("GMAIL_PASSWORD")
	FROM = contactlist.listname + " <" + gmail_user + ">"
	TO = []
	SUBJECT = ""
	for number in getPhoneNumbers(contactlist):
		for carrier in carrierlist:
			TO.append(number + "@" + carrier)

	for email in getEmails(contactlist):
		TO.append(email)

	# Prepare actual message
	message = """\From: %s\n\n%s""" % (FROM, msg)
	try:
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.ehlo()
		server.starttls()
		server.login(gmail_user, gmail_pwd)
		server.sendmail(FROM, TO, message)
		server.close()

		rememberNotifications(contactlist, msg)
	except:
		print "failed to send email"

def getUserContactLists(userprofile):
	try:
		return json.decoder.JSONDecoder().decode(userprofile.contact_list_ids)
	except ValueError:
		return []

def addUserContactList(userprofile, contactlist):
	clist = getContactLists(userprofile)
	clist.insert(contactlist.id)
	userprofile.contact_list_ids = json.dumps(clist)
	userprofile.save()

def deleteUserContactList(userprofile, contactlist):
	print("imhere")
	clist = getContactLists(userprofile)
	print(clist)
	if contactlist in clist:
		clist.remove(contactlist.id)
		print("FOFWOFMOM")
	userprofile.contact_list_ids = json.dumps(clist)
	print("FJJJjj")
	userprofile.save()

def verifyUser(user, contactlist):
	usercontactlists = getUserContactLists(user.profile)
	if contactlist.id in usercontactlists:
		return True
	else:
		return False

#Section for saving and getting recent notifications
def getRecentNots(contactlist):
	try:
		return json.decoder.JSONDecoder().decode(contactlist.recentnotifications)
	except ValueError:
		return []

def getRecentNotTimes(contactlist):
	try:
		return json.decoder.JSONDecoder().decode(contactlist.rnottimes)
	except ValueError:
		return []

def rememberNotifications(contactlist, notification):
	print("!!!!!")
	recentnots = getRecentNots(contactlist)
	recentnottimes = getRecentNotTimes(contactlist)

	recentnots.insert(0, notification)
	tm = int(time.time())
	recentnottimes.insert(0, tm)

	contactlist.recentnotifications = json.dumps(recentnots)
	contactlist.recentnottimes = json.dumps(recentnottimes)
	contactlist.save()