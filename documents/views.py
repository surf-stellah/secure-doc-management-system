import os
import mammoth
import pandas as pd
from io import BytesIO
from .models import Document
from .forms import DocumentForm
from django.template import loader
from profiles.models import Profile
from django.contrib.auth import logout
from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect


# Create your views here.
@login_required
def homeView(request):
    profile   = Profile.objects.get(user=request.user)
    documents = Document.objects.filter(owner=profile)

    if 'search' in request.GET:
        query     = request.GET['search']
        documents = Document.objects.filter(title__istartswith=query)

    template = loader.get_template('documents/home.html')
    context = {
        "profile"  : profile,
        "documents": documents,
    }
    if not request.user.is_authenticated:
        return redirect('login')
    return HttpResponse(template.render(context, request))


def uploadDocument(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.owner = profile

            # Calculate file size
            if 'fileItem' in request.FILES:
                fileSize = request.FILES['fileItem'].size
                document.fileSize = fileSize

            print(f"Uploading document: {document.title}, owner: {document.owner}, fileSize: {document.fileSize}")

            document.save()
            return redirect('documents:home')
    else:
        form = DocumentForm()
    template = loader.get_template('documents/upload.html')
    context = {
        'profile': profile,
        'form': form,
    }
    return HttpResponse(template.render(context, request))


def openDocx(request, documentId):
    profile = Profile.objects.get(user=request.user)
    document = get_object_or_404(Document, id=documentId)

    if profile.user != document.owner.user:
        return HttpResponse(status=403)

    filePath = document.fileItem.path
    if not os.path.exists(filePath):
        return HttpResponse(status=404, content='File not found.')

    try:
        # Convert DOCX to HTML using Mammoth
        with open(filePath, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value  # The generated HTML

        # Debug: Log length of HTML content
        print(f"Length of HTML content: {len(html)}")
    except Exception as e:
        # Debug: Log the error message
        print(f"Error converting document: {str(e)}")
        return HttpResponse(f"Error converting document: {str(e)}", status=500)

    return render(request, 'documents/viewDocx.html', {'document': document, 'html': html})


def openExcel(request, documentId):
    profile  = Profile.objects.get(user=request.user)
    document = get_object_or_404(Document, id=documentId)

    if profile.user != document.owner.user:
        return HttpResponse(status=403)

    filePath = document.fileItem.path
    if not os.path.exists(filePath):
        return HttpResponse(status=404, content='File not found.')

    try:
        # Load Excel file using pandas
        excel_data = pd.read_excel(filePath, sheet_name=None)  # Load all sheets

        # Convert each sheet to HTML
        html_tables = {}
        for sheet_name, df in excel_data.items():
            html_tables[sheet_name] = df.to_html(index=False)
            
    except Exception as e:
        # Debug: Log the error message
        print(f"Error converting Excel document: {str(e)}")
        return HttpResponse(f"Error converting Excel document: {str(e)}", status=500)

    return render(request, 'documents/viewExcel.html', {'document': document, 'html_tables': html_tables})


def openText(request, documentId):
    profile = Profile.objects.get(user=request.user)
    document = get_object_or_404(Document, id=documentId)

    if profile.user != document.owner.user:
        return HttpResponse(status=403)

    filePath = document.fileItem.path
    if not os.path.exists(filePath):
        return HttpResponse(status=404, content='File not found.')

    with open(filePath, 'r') as file:
        file_data = file.read()

    response = HttpResponse(file_data, content_type='text/plain')
    response['Content-Disposition'] = f'inline; filename="{document.title}.txt"'
    return response


def openPdf(request, documentId):
    profile  = Profile.objects.get(user=request.user)
    document = get_object_or_404(Document, id=documentId)

    if profile.user != document.owner.user:
        return HttpResponse(status=403)

    filePath = document.fileItem.path
    if not os.path.exists(filePath):
        return HttpResponse(status=404, content='File not found.')

    with open(filePath, 'rb') as file:
        file_data = file.read()

    buffer = BytesIO()
    buffer.write(file_data)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{document.title}.pdf"'
    return response


def openImage(request, documentId):
    profile = Profile.objects.get(user=request.user)
    document = get_object_or_404(Document, id=documentId)

    if profile.user != document.owner.user:
        return HttpResponse(status=403)

    filePath = document.fileItem.path
    if not os.path.exists(filePath):
        return HttpResponse(status=404, content='File not found.')

    with open(filePath, 'rb') as file:
        file_data = file.read()

    buffer = BytesIO()
    buffer.write(file_data)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type=f'image/{document.fileType}')
    response['Content-Disposition'] = f'inline; filename="{document.title}"'
    return response


def downloadFile(request, documentId):
    profile  = Profile.objects.get(user=request.user)
    document = get_object_or_404(Document, id=documentId)

    if profile.user != document.owner.user:
        return HttpResponse(status=403)

    filePath = document.fileItem.path
    if not os.path.exists(filePath):
        return HttpResponse(status=404, content='File not found.')

    with open(filePath, 'rb') as file:
        file_data = file.read()

    response = HttpResponse(file_data, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filePath)}"'
    return response


def deleteDocument(request, documentId):
    profile  = Profile.objects.get(user=request.user)
    document = get_object_or_404(Document, id=documentId)

    if profile.user != document.owner.user:
        return HttpResponse(status=403)
    
    if request.method == "POST":
        if document.fileItem:
            document.fileItem.delete(save=False)  
        document.delete()
        return redirect('documents:home')
    
    return render(request, 'documents/delete.html', {'document': document, 'profile' : profile})


def logoutView(request):
    logout(request)
    return redirect('login')
