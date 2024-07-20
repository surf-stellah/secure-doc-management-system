import os
from django.db import models
from profiles.models import Profile
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage


# Create your models here.
def validateFileExtension(value):
    ext      = os.path.splitext(value.name)[1]
    validExt = ['.pdf', '.xlsx', '.docx', '.txt', '.png', '.jpg', '.jpeg', '.gif']
    if not ext.lower() in validExt:
        raise ValidationError('Unsupported file extension.')
    

class Document(models.Model):
    FILETYPECHOICE = (
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
        ('docx', 'Word'),
        ('txt', 'Text'),
        ('jpg', 'JPEG'),
        ('jpeg', 'JPEG'),
        ('png', 'PNG')
    )

    owner    = models.ForeignKey(Profile, related_name='owner', on_delete=models.CASCADE)
    title    = models.CharField(max_length=100)
    fileItem = models.FileField(upload_to='DocumentFiles/', validators=[validateFileExtension])
    fileType = models.CharField(max_length=10, choices=FILETYPECHOICE, blank=True)
    fileSize = models.PositiveIntegerField(blank=True, null=True)
    updated  = models.TimeField(auto_now=True)
    created  = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.owner:
            raise ValueError("Owner must be set.")

        super().save(*args, **kwargs)

        if self.fileItem and self.fileItem.name:
            filePath = default_storage.path(self.fileItem.name)
            if default_storage.exists(filePath):
                self.fileSize = default_storage.size(filePath)

            _, ext = os.path.splitext(self.fileItem.name)
            ext = ext.lower()
            for choice in self.FILETYPECHOICE:
                if ext == f".{choice[0]}":
                    self.fileType = choice[0]
                    break
        else:
            self.fileType = ''
            self.fileSize = 0

        print(f"Saving document: {self.title}, fileType: {self.fileType}, fileSize: {self.fileSize}, filePath: {filePath}")

        super().save(*args, **kwargs)