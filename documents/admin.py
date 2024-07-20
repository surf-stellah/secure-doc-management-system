from .models import Document
from django.contrib import admin


# Register your models here.
class DocumentAdmin(admin.ModelAdmin):
  list_display = ("owner", "title", "fileType", "fileSize", "created")
admin.site.register(Document, DocumentAdmin)