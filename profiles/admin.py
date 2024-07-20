from django.contrib import admin
from .models import Profile, ResetPassword


# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
  list_display = ("user", "firstName", "lastName", "email", "organisation")
admin.site.register(Profile, ProfileAdmin)


class ResetPasswordAdmin(admin.ModelAdmin):
  list_display = ("email", "token")
admin.site.register(ResetPassword, ResetPasswordAdmin)