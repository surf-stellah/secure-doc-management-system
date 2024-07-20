from . import views
from django.urls import path


app_name = 'documents'


urlpatterns = [
    path('', views.homeView, name='home'),
    path('logout/', views.logoutView, name='logout'),
    path('upload/', views.uploadDocument, name='uploadDoc'),
    path('<int:documentId>/pdf/', views.openPdf, name='openPdf'),
    path('<int:documentId>/docx/', views.openDocx, name='openDocx'),
    path('<int:documentId>/text/', views.openText, name='openText'),
    path('<int:documentId>/excel/', views.openExcel, name='openExcel'),
    path('<int:documentId>/image/', views.openImage, name='openImage'),
    path('<int:documentId>/download/', views.downloadFile, name='downloadFile'),
    path('<int:documentId>/delete/', views.deleteDocument, name='deleteDocument')
]