from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from datetime import timedelta

from app.main.random_str import *

class ProfileManager(models.Manager):
	def activate_user(self, key):
		if key == "ACTIVATED":
			return False
		try:
			profile = self.get(activation=key, registered=True)
		except:
			return False
		profile.activation = "ACTIVATED"
		profile.save()
		return True

class Profile(models.Model):
	class Meta:
		ordering = ['user__last_name', 'user__first_name']
	user = models.OneToOneField(User)
	activation = models.CharField(max_length=255, blank=True)
	cnetid = models.CharField(max_length=30)
	registered = models.BooleanField(default=False)
	optout = models.BooleanField(default=False)
	bang_score = models.IntegerField(default=0)

	objects = ProfileManager()

	def __unicode__(self):
		return self.user.get_full_name()

	def get_bang_score_and_rank(self):
		return {
			'score': self.bang_score,
			'rank': Profile.objects.filter(bang_score__gt=self.bang_score).count() + 1
		}

	def save(self, *args, **kwargs):
		if not self.activation and not self.registered:
			self.activation = GenRandomHash(self.user.username)
		super(Profile, self).save(*args, **kwargs)

@receiver(models.signals.post_save, sender=User)
def create_profile_hook(sender, **kwargs):
	user = kwargs['instance']
	Profile.objects.get_or_create(user=user)

class BangManager(models.Manager):
	def match_exists(self, bang1, bang2):
		return self.filter(banger=bang1, bangee=bang2).exists() and self.filter(banger=bang2, bangee=bang1).exists()

	def delete_bangs(self, bang1, bang2):
		Bang.objects.filter(banger=bang1, bangee=bang2).delete()
		Bang.objects.filter(banger=bang2, bangee=bang1).delete()

	def most_bangable_users(self):
		return User.objects.all().exclude(profile__bang_score=0).order_by('-profile__bang_score', 'last_name')

class Bang(models.Model):
	class Meta:
		unique_together = ("banger", "bangee")
		ordering = ['-date', 'bangee__last_name']

	banger = models.ForeignKey(User, related_name='bangs_is_banger') # initiating user
	bangee = models.ForeignKey(User, related_name='bangs_is_bangee') # target user
	date = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return "<%s, %s>" % (self.banger.get_full_name(), self.bangee.get_full_name())

	@property
	def can_unbang(self):
		if settings.DEBUG:
			return True
		return self.date + timedelta(days=1) < timezone.now()

	objects = BangManager()

class BangMatchManager(models.Manager):
	def create_matches(self, bang1, bang2):
		assert not self.already_matched(bang1, bang2)
		self.create(banger=bang1, bangee=bang2)
		self.create(banger=bang2, bangee=bang1)
		Bang.objects.delete_bangs(bang1, bang2)

	def already_matched(self, bang1, bang2):
		return self.filter(banger=bang1, bangee=bang2).exists() or self.filter(banger=bang2, bangee=bang1).exists()

class BangMatch(models.Model):
	"""
	Create two BangMatches for each match ; banger/bangee and vice versa
	"""
	class Meta:
		unique_together = ("banger", "bangee")
		ordering = ['-date', 'bangee__last_name']
		verbose_name_plural = "bang matches"

	banger = models.ForeignKey(User, related_name='bang_matches')
	bangee = models.ForeignKey(User, related_name='+')
	date = models.DateTimeField(auto_now_add=True)
	read = models.BooleanField(default=False)

	def __unicode__(self):
		return "<%s, %s>" % (self.banger.get_full_name(), self.bangee.get_full_name())

	objects = BangMatchManager()
