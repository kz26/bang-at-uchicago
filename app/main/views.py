from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from rest_framework import exceptions
from rest_framework import generics
from rest_framework import permissions
from rest_framework import response
from rest_framework import status
from rest_framework import views

from app.main.models import *
from app.main.emails import *
from app.main.exceptions import *
from app.main.serializers import *
from app.main import tasks
from app.main.users import *

class IndexView(TemplateView):
	template_name = "index.html"
	
class Register(views.APIView):
	def post(self, request, *args, **kwargs):
		serializer = UserRegSerializer(data=request.DATA)
		if serializer.is_valid():
			user = serializer.user_object
			user.set_password(serializer.data['password'])
			user.save()
			user.profile.registered = True
			user.profile.save()
			send_activation_email(user)
			return response.Response(None)
		else:
			return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Activate(views.APIView):
	def get(self, request, *args, **kwargs):
		if 'key' in request.QUERY_PARAMS:
			result = Profile.objects.activate_user(request.QUERY_PARAMS['key'])
			if result:
				return HttpResponseRedirect("/#/you/can/start/banging")
		return response.Response({'key': ["Invalid activation key or account already activated. Email bang@bangatuchicago.com for assistance."]}, status=status.HTTP_400_BAD_REQUEST)

class Login(views.APIView):
	def post(self, request, *args, **kwargs):
		serializer = LoginSerializer(data=request.DATA)
		if serializer.is_valid():
			auth_login(request, serializer.user_object)	
			return response.Response(UserSerializer(serializer.user_object).data)
		return response.Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)

class Logout(views.APIView):
	def get(self, request, *args, **kwargs):
		auth_logout(request)
		return response.Response(status=status.HTTP_204_NO_CONTENT)

class AuthInfo(views.APIView):
	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated():
			data = UserSerializer(request.user).data
			return response.Response(data)
		return response.Response(None)

class ForgotPassword(views.APIView):
	def post(self, request, *args, **kwargs):
		if 'username' in request.DATA:
			try:
				user = User.objects.get(profile__cnetid=request.DATA['username'], profile__registered=True, profile__activation="ACTIVATED")
			except User.DoesNotExist:
				return response.Response({'username': ['Invalid CNetID']}, status=status.HTTP_404_NOT_FOUND)
			key = gen_forgot_password(user)
			reset_password_email(user, key)
			return response.Response(None, status=status.HTTP_204_NO_CONTENT)
		return response.Response(None, status=status.HTTP_400_BAD_REQUEST)

class ResetPassword(views.APIView):
	def post(self, request, *args, **kwargs):
		serializer = ResetPasswordSerializer(data=request.DATA)
		if serializer.is_valid():
			user = serializer.user_object
			user.set_password(serializer.data['password'])
			user.save()
			return response.Response(status=status.HTTP_204_NO_CONTENT)
		return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePassword(views.APIView):
	permission_classes = (permissions.IsAuthenticated,)
	def post(self, request, *args, **kwargs):
		serializer = ChangePasswordSerializer(data=request.DATA)
		if serializer.is_valid():
			user = authenticate(username=request.user.username, password=serializer.data['old_password'])
			if user:
				user.set_password(serializer.data['password'])
				user.save()
				return response.Response(status=status.HTTP_204_NO_CONTENT)
			else:
				return response.Response({'old_password': ["Original password is incorrect"]}, status=status.HTTP_403_FORBIDDEN)
		return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetUpdateProfile(generics.RetrieveUpdateAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	serializer_class = ProfileSerializer

	def get_object(self):
		return self.request.user.profile

	def put(self, request, *args, **kwargs):
		result = super(GetUpdateProfile, self).put(request, *args, **kwargs)
		user = self.request.user
		if not user.profile.optout:
			for bang in user.bangs_is_bangee.all(): # get all Bangs where user is bangee
				tasks.setup_match.delay(user.id, bang.banger.id)
		return result

class BangList(generics.ListAPIView):
	permission_classes = (permissions.IsAuthenticated,) 
	serializer_class = BangSerializer
	
	def get_queryset(self):
		results = Bang.objects.select_related().filter(banger=self.request.user)
		#for bang in results:
		#	tasks.setup_match.delay(self.request.user.id, bang.bangee.id)
		return results

class BangSearch(views.APIView):
	permission_classes = (permissions.IsAuthenticated,)
	
	def get(self, request, *args, **kwargs):
		query_serializer = BangSearchSerializer(data=request.QUERY_PARAMS)
		if query_serializer.is_valid():
			results = lookup_user(query_serializer.data)
			eligible = []
			for bangee in results:
				if not Bang.objects.filter(banger=request.user, bangee=bangee).exists() and not BangMatch.objects.filter(banger=request.user, bangee=bangee).exists() and bangee != request.user:
					eligible.append(bangee)
			out_serializer = UserSerializer(eligible, many=True)
			return response.Response(out_serializer.data)
		return response.Response(query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BangScore(views.APIView):
	permission_classes = (permissions.IsAuthenticated,)
	def get(self, request, *args, **kwargs):
		return response.Response(request.user.profile.get_bang_score_and_rank())

class NewBang(views.APIView):
	permission_classes = (permissions.IsAuthenticated,) 

	def post(self, request, *args, **kwargs):
		serializer = IDSerializer(data=request.DATA)
		if serializer.is_valid():
			bangee = None
			try:
				bangee = User.objects.get(id=serializer.data['id'])
			except User.DoesNotExist:
				return response.Response({'id': ['Invalid user ID']}, status=status.HTTP_404_NOT_FOUND)
			if Bang.objects.filter(banger=request.user, bangee=bangee).exists():
				raise AlreadyBangListedException()
			elif BangMatch.objects.already_matched(request.user, bangee):
				raise AlreadyBangedException()
			bang = Bang.objects.create(banger=request.user, bangee=bangee)
			bangee.profile.bang_score += 1
			bangee.profile.save()
			tasks.setup_match.delay(request.user.id, bangee.id)
			return response.Response(BangSerializer(bang).data, status=status.HTTP_201_CREATED)
		else:
			return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			
class BangMatches(generics.ListAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	serializer_class = BangMatchSerializer

	def get_queryset(self):
		return BangMatch.objects.filter(banger=self.request.user)

class DeleteBang(views.APIView):
	permission_classes = (permissions.IsAuthenticated,) 

	def post(self, request, *args, **kwargs):
		serializer = IDSerializer(data=request.DATA)
		if serializer.is_valid():
			bang = None
			try:
				bang = Bang.objects.get(id=serializer.data['id'], banger=request.user)
			except Bang.DoesNotExist:
				return response.Response({'id': ['Invalid bang ID']}, status=status.HTTP_404_NOT_FOUND)
			bang.delete()
			bangee = bang.bangee
			bangee.profile.bang_score -= 1
			bangee.profile.save()
			return response.Response(None, status=status.HTTP_204_NO_CONTENT)
		return response.response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MostBangable(generics.ListAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	serializer_class = UserWithBangScoreSerializer 

	def get_queryset(self):
		return Bang.objects.most_bangable_users()

	def get(self, request, *args, **kwargs):
		if request.user.is_staff or request.user.groups.filter(name='Inner Circle').exists():
			return super(MostBangable, self).get(request, *args, **kwargs)
		return response.Response(None, status=status.HTTP_403_FORBIDDEN)
