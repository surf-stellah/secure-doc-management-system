from . import views
from django.urls import path

app_name = 'profiles'

urlpatterns = [
    path('', views.profileView, name='profile'),
    path('edit/', views.editProfile, name='editProfile'),
    path('reset/', views.resetPassword, name='resetPassword'),
    path('reset/<str:token>/', views.resetPasswordConfirm, name='resetConfirm'),
    path("resetDone/", views.resetPasswordDone, name="resetDone")
]