from urllib import urlencode

from django.conf import settings
from django.core.urlresolvers import *
from django.core.cache import cache
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.utils import timezone
from django.utils.safestring import *

from app.main import tasks

def send_activation_email(user, is_https=False):
	if user.profile.activation == "ACTIVATED":
		return
	subject = "You're almost ready to Bang!"
	protocol = is_https and 'https' or 'http'
	link = reverse('activate') + "?" + urlencode((('key', user.profile.activation),))
	d = {
		'site': Site.objects.get_current(),
		'protocol': protocol,
		'link': mark_safe(link),
		'user': user,
	}
	msg = render_to_string('email/activation.html', d)
	tasks.send_multipart_email.delay(subject, None, [user.email], msg, True)

def send_bang_match_email(user1, user2):
	subject = "Someone wants to bang you too!"
	for banger, bangee in ((user1, user2), (user2, user1)):
		d = {
			'banger': banger,
			'bangee': bangee
		}
		msg = render_to_string('email/bangMatch.html', d)
		tasks.send_multipart_email.delay(subject, None, [banger.email], msg, True)

def reset_password_email(user, key, is_https=False):
	# Check for existing reset key - if so, don't send the email again
	if cache.get("forgot_password_%s" % (user.username)):
		return
	else:
		cache.set("forgot_password_%s" % (user.username), True, settings.PASSWORD_RESET_EXPIRY)
	subject = "Reset your password"
	protocol = is_https and 'https' or 'http'
	link = "/#/remember/how/to/bang?" + urlencode([('key', key)])
	d = {
		'site': Site.objects.get_current(),
		'protocol': protocol,
		'link': mark_safe(link),
		'user': user
	}

	msg = render_to_string('email/reset-password.html', d)
	tasks.send_multipart_email.delay(subject, None, [user.email], msg, True)
