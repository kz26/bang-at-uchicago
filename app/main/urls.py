from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns

from app.main.views import *

urlpatterns = patterns('',
	url('^$', IndexView.as_view(), name="index"),
	url('^register/$', Register.as_view(), name="register"),
	url('^login/$', Login.as_view(), name="login"),
	url('^logout/$', Logout.as_view(), name="logout"),
	url('^activate/$', Activate.as_view(), name="activate"),
	url('^auth-info/$', AuthInfo.as_view(), name="auth_info"),
	url('^forgot-password/$', ForgotPassword.as_view(), name="forgot_password"),
	url('^reset-password/$', ResetPassword.as_view(), name="reset_password"),
	url('^change-password/$', ChangePassword.as_view(), name="change_password"),
	url('^profile/$', GetUpdateProfile.as_view(), name="GetUpdateProfile"),
	url('^my/bangs/$', BangList.as_view(), name="bang_list"),
	url('^my/bangs/matches/$', BangMatches.as_view(), name="bang_matches"),
	url('^my/bangability/$', BangScore.as_view(), name="bang_score"),
	url('^bangs/search/$', BangSearch.as_view(), name="bang_search"),
	url('^bangs/new/$', NewBang.as_view(), name="new_bang"),
	url('^bangs/delete/$', DeleteBang.as_view(), name="delete_bang"),
	url('^most/bangable/$', MostBangable.as_view(), name="most_bangable")
)

urlpatterns = format_suffix_patterns(urlpatterns)
