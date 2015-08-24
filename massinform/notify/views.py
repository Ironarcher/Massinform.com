from django.shortcuts import render
from .models import ContactList
from django.contrib.auth.models import User

import json
import smtplib
import sys
import os
import re
from email.MIMEText import MIMEText

# Create your views here.

def index(request):
	context = {
		
	}
	return render(request, 'notify/notify.html', context)

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
		email.insert(emailaddress)
		firstlist = getFirstNames(contactlist)
		firstlist.insert(firstname)
		lastlist = getLastNames(contactlist)
		lastlist.insert(lastname)
		phonelist = getPhoneNumbers(contactlist)
		phonelist.insert(phonenumber)

		#Save all of these lists
		contactlist.firstnames = json.dumps(firstlist)
		contactlist.lastnames = json.dumps(lastlist)
		contactlist.phonenumbers = json.dumps(phonelist)
		contactlist.emailaddresses = json.dumps(email)
		contactlist.save()
	else:
		print("Contact ERROR: Email address already exists")

#Cannot have someone with no email address or the same email address
def removeFromContactList(contactlist, emailaddress):
	pass

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
	clist.insert(contactlist)
	userprofile.save()

def deleteUserContactList(userprofile, contactlist):
	clist = getContactLists(userprofile)
	if contactlist in clist:
		clist.remove(contactlist)
	userprofile.save()