from django.contrib import admin
from django.contrib.auth.models import *
from django.contrib.auth.admin import UserAdmin
from app.main.models import *

admin.site.register(Bang)
admin.site.register(BangMatch)

class ProfileInline(admin.StackedInline):
	model = Profile
	can_delete = False
	verbose_name_plural = 'profile'

class UserAdmin(UserAdmin):
	inlines = [ProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
