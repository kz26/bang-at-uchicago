from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.cache import cache

from rest_framework import serializers

from app.main.models import *
from app.main.users import *

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id', 'cnetid', 'first_name', 'last_name', 'groups')
	cnetid = serializers.SerializerMethodField('get_cnetid')
	groups = serializers.SerializerMethodField('get_groups')

	def get_cnetid(self, obj):
		return obj.profile.cnetid
	def get_groups(self, obj):
		return list(obj.groups.all().values_list('name', flat=True))

class UserWithBangScoreSerializer(UserSerializer):
	class Meta:
		model = User
		fields = ('id', 'cnetid', 'first_name', 'last_name', 'bang_score')
	bang_score = serializers.SerializerMethodField('get_bang_score')

	def get_bang_score(self, obj):
		return obj.profile.bang_score

class UserRegSerializer(serializers.Serializer):
	username = serializers.CharField()
	password = serializers.CharField(min_length=6)

	def validate_username(self, attrs, source):
		username = attrs[source]
		try:
			user = lookup_user({'cnetid': username})[0] # a CNetID
		except:
			raise serializers.ValidationError("This is not a valid CNetID, or there was a problem obtaining your directory information")
		if user.profile.registered:
			raise serializers.ValidationError("This username has already been registered")
		self.user_object = user
		return attrs

class LoginSerializer(serializers.Serializer):
	username = serializers.CharField()
	password = serializers.CharField()

	def validate(self, attrs):
		user = None
		try:
			user = User.objects.get(profile__cnetid=attrs['username'], profile__registered=True, profile__activation="ACTIVATED")
		except User.DoesNotExist:
			raise serializers.ValidationError("Invalid username and/or password")
		user = authenticate(username=user.username, password=attrs['password'])
		if not user:
			raise serializers.ValidationError("Invalid username and/or password")
		self.user_object = user
		return attrs

class ResetPasswordSerializer(serializers.Serializer):
	key = serializers.CharField()
	password = serializers.CharField(min_length=6)

	def validate_key(self, attrs, source):
		key = attrs[source]
		user_id = cache.get(key)
		if not user_id:
			raise serializers.ValidationError("Invalid password reset key")
		try:
			self.user_object = User.objects.get(id=user_id)
		except User.DoesNotExist:
			raise serializers.ValidationError("Invalid password reset key")
		cache.delete(key)
		return attrs

class ChangePasswordSerializer(serializers.Serializer):
	old_password = serializers.CharField()
	password = serializers.CharField(min_length=6)

class BooleanToIntField(serializers.WritableField):
	def from_native(self, value):
		return True if value == 1 else False
	def to_native(self, value):
		return 1 if value else 0

class ProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = Profile
		fields = ('optout',)
	optout = BooleanToIntField()

class BangSerializer(serializers.ModelSerializer):
	class Meta:
		model = Bang
		fields = ('id', 'first_name', 'last_name', 'cnetid', 'date', 'can_unbang')
	first_name = serializers.SerializerMethodField('get_first_name')
	last_name = serializers.SerializerMethodField('get_last_name')
	cnetid = serializers.SerializerMethodField('get_cnetid')
	can_unbang = serializers.SerializerMethodField('get_can_unbang')

	def get_first_name(self, obj):
		return obj.bangee.first_name

	def get_last_name(self, obj):
		return obj.bangee.last_name
	
	def get_cnetid(self, obj):
		return obj.bangee.profile.cnetid

	def get_can_unbang(self, obj):
		return obj.can_unbang


class BangMatchSerializer(BangSerializer):
	class Meta:
		model = BangMatch
		fields = ('id', 'first_name', 'last_name', 'cnetid', 'date', 'read')

class BangSearchSerializer(serializers.Serializer):
	cnetid = serializers.CharField(required=False, default=None)
	first_name = serializers.CharField(required=False, default=None)
	last_name = serializers.CharField(required=False, default=None)

	def validate(self, attrs):
		if attrs.get('cnetid') or (attrs.get('first_name') and attrs.get('last_name')):
			return attrs
		raise serializers.ValidationError("CNetID or both first_name and last_name must be specified")

class IDSerializer(serializers.Serializer):
	id = serializers.IntegerField()
