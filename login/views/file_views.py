from django.contrib import messages
from django.shortcuts import render

from ..forms import FileUploadForm
from ..utils.file_utils import handle_uploaded_file


def file_upload(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            data = handle_uploaded_file(request.FILES['file'])
            return render(request, 'login/view_file.html', {'data': data})
        else:
            messages.error(request, 'Invalid form submission. Try again.')
    else:
        form = FileUploadForm()
    return render(request, 'login/file_upload.html', {'form': form})
