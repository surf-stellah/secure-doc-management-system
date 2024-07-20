from .utils import get_uuid
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


# Create your models here.
class Profile(models.Model):
    user           = models.OneToOneField(User, on_delete=models.CASCADE)
    slug           = models.SlugField(unique=True, blank=True)
    profilePicture = models.ImageField(default='ProfilePictures/profileIcon.png', upload_to='ProfilePictures')
    firstName      = models.CharField(max_length=35, blank=True)
    lastName       = models.CharField(max_length=35, blank=True)
    email          = models.EmailField(max_length=90, blank=True)
    organisation   = models.CharField(max_length=35, blank=True)
    updated        = models.TimeField(auto_now=True)
    created        = models.TimeField(auto_now_add=True)


    def __str__(self): return f"{self.user}" 
    

    def save(self, *args, **kwargs):
        instance = False
        if self.user.email:
            sluged   = slugify(str(self.user.username))
            instance = Profile.objects.filter(slug=sluged).exists()

            while instance:
                sluged   = slugify(sluged + " " + str(get_uuid()))
                instance = Profile.objects.filter(slug=sluged).exists()

                self.slug  = sluged
                self.email = self.user.email  
        else:
            sluged = str(self.user)
        self.slug = sluged
        super().save(*args, **kwargs)


class ResetPassword(models.Model):
    email = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.email} {self.token}"