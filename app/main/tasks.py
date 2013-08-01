from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.models import Site

from celery import task

from app.main.models import *

@task
def setup_match(bangerID, bangeeID):
	"""
	Check if the banger and bangee want to bang each other.
	If so, create a pair of BangMatches, remove the pair of Bangs, and send an email to both.
	"""
	from app.main.emails import send_bang_match_email
	try:
		banger = User.objects.get(id=bangerID, profile__registered=True)
		bangee = User.objects.get(id=bangeeID, profile__registered=True)
	except User.DoesNotExist:
		return
	if banger.profile.optout or bangee.profile.optout:
		return
	if not Bang.objects.match_exists(banger, bangee):
		return

	with transaction.commit_on_success():	
		BangMatch.objects.create_matches(banger, bangee)
		Bang.objects.delete_bangs(banger, bangee)
	send_bang_match_email(banger, bangee)

@task
def mark_matches_read():
	"""
	Mark unread BangMatches as read
	Run this as a periodic task
	"""
	yesterday = timezone.now() - timedelta(days=1)
	BangMatch.objects.filter(read=False, date__lte=yesterday).update(read=True)

@task
def send_multipart_email(subject, from_addr, to_addrs, msg, is_html=False, subject_as_is=False, **kwargs):
	site_name = Site.objects.get_current().name

	if from_addr is None:
		from_addr = settings.DEFAULT_FROM_EMAIL
	if is_html:
		text_msg = strip_tags(msg)
	else:
		text_msg = msg
	if subject_as_is is False:
		subject = "[%s] %s" % (site_name, subject)

	e = EmailMultiAlternatives(subject, text_msg, from_addr, to_addrs, **kwargs)
	if is_html:
		e.attach_alternative(msg, "text/html")
	e.send()

