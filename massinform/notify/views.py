from django.shortcuts import render, redirect
from django.http import *
from .models import ContactList
from django.contrib.auth.models import User

import json
import smtplib
import sys
import os
import re
from email.MIMEText import MIMEText

# Create your views here.

def index_view2(request):
	if request.user.is_authenticated():
		user = request.user
	else:
		return HttpResponseRedirect("/login?next=/notify/")

	#Collect user information
	c_ids = getUserContactLists(user.profile)
	print(c_ids)
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

			nots = {}
			nots['text'] = c.recentnotifications
			nots['times'] = c.rnottimes
			nots['clist_name'] = c.listname
	context = {
		"contactlists" : contactlists,
		"notifications" : notifications,
	}
	print(contactlists)
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
				clist_id = request.GET['contactlist']
				removeFromContactList(clist_id, request.user.profile)
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
	print(email)
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
	contactlist = Contacts.objects.get(id=clist_id)
	firstname = getFirstNames(contactlist)
	lastname = getLastNames(contactlist)
	phonenumber = getPhoneNumbers(contactlist)
	email = getEmails(contactlist)

def deleteContactList(clist_id, userprofile):
	contactlist = ContactList.objects.get(id=clist_id)
	#Remove it from the user bank
	deleteUserContactList(userprofile, contactlist)
	contactlist.delete()

def createContactlist(name):
	c = ContactList(name=name)
	c.save()

def notify(contactlist, message):
	carrierlist = [
		"vtext.com",
		"txt.att.net",
		"messaging.sprintpcs.com",
		"tmomail.net",
		"email.uscc.net",
		"vmobl.com",
	]
	gmail_user = ""
	gmail_pwd = ""
	FROM = contactlist.name + " <" + gmail_user + ">"
	SUBJECCT = "Notification"
	TO = []
	for number in getPhoneNumbers(contactlist):
		for carrier in carrierlist:
			TO.append(number + "@" + carrier)

	for email in getEmails(contactlist):
		TO.append(email)

	# Prepare actual message
	message = """\From: %s\nSubject: %s\n\n%s""" % (FROM, SUBJECT, TEXT)
	try:
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.ehlo()
		server.starttls()
		server.login(gmail_user, gmail_pwd)
		server.sendmail(FROM, TO, message)
		server.close()
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