from .models import Profile
from django.template import loader
from django.contrib import messages
from django.http import HttpResponse
from documents.models import Document
from django.core.mail import send_mail
from .models import Profile, ResetPassword
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from .forms import EditForm, ResetPasswordForm
from django.utils.crypto import get_random_string
from django.core.validators import validate_email
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.decorators import login_required


@login_required
def profileView(request):
    profile   = Profile.objects.get(user=request.user)
    totalDocs = Document.objects.filter(owner=profile)
    template  = loader.get_template('profiles/profile.html')
    context   = { 'profile' : profile, 'totalDocs' : totalDocs, }
    return HttpResponse(template.render(context, request))


@login_required
def editProfile(request):
    profile  = Profile.objects.get(user=request.user)
    form     = EditForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('profiles:profile')
    template = loader.get_template('profiles/editProfile.html')
    context = {
        'profile':profile,
        'form'   :form,
    }
    return HttpResponse(template.render(context, request))


def resetPassword(request):
    template = loader.get_template('profiles/resetPassword.html')
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                validate_email(email)
                token = get_random_string(length=32)
                ResetPassword.objects.create(email=email, token=token)

                resetUrl = f"http://127.0.0.1:8000/profiles/reset/{token}/"

                send_mail(
                    subject        = "Reset your password!",
                    message        = f"Click the following link to reset your password: {resetUrl}",
                    from_email     = "", #Your Email
                    recipient_list = [email]
                )
                messages.success(request, 'A password reset link has been sent to your email.')
                return redirect('profiles:resetDone')

            except Profile.DoesNotExist:
                messages.error(request, 'No profile found with that email address.')
                print('No profile found with that email address:', email)
            except Exception as e:
                messages.error(request, 'An error occurred. Please try again.')
                print('An error occurred:', e)
    else:
        form = ResetPasswordForm()

    context  = { 'form': form }
    return HttpResponse(template.render(context, request))


def resetPasswordConfirm(request, token):
    template = loader.get_template('profiles/resetPasswordConfirm.html')
    try:
        resetToken = ResetPassword.objects.get(token=token)
    except ResetPassword.DoesNotExist:
        messages.error(request, 'Invalid reset link.')
        return redirect('home')
    
    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid(): 
            try:
                user = User.objects.get(email=resetToken.email)   
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                resetToken.delete()

                print('email: ', user.email)
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
                return redirect('documents:home') 
    else:
        form = SetPasswordForm(request.user)
    
    context  = { 'form': form }
    return HttpResponse(template.render(context, request))


def resetPasswordDone(request):
    return render(request, 'profiles/resetPasswordDone.html')