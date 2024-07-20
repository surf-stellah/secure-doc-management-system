from django import forms
from .models import Profile


class EditForm(forms.ModelForm):
    username     = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder' : 'Username'}))
    firstName    = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder' : 'First Name'}))
    lastName     = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder' : 'Last Name'}))
    email        = forms.EmailField(required=False, widget=forms.TextInput(attrs={'placeholder' : 'Email',}))
    organisation = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder' : 'organisation ~ (NCBA)',}))

    class Meta:
        model   = Profile
        fields  = ('profilePicture','username', 'firstName', 'lastName', 'email', 'organisation')
        widgets = {'profilePicture' : forms.FileInput(attrs={})}


    def save(self, commit=True):
        profile  = super().save(commit=False)
        username = self.cleaned_data.get('username')
        if username:
            profile.user.username = username
            profile.user.save()
        if commit:
            profile.save()
        return profile
    

class ResetPasswordForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)