from base64 import b64encode

from django.shortcuts import render, get_object_or_404, redirect
from .grade import detect_image
import cv2
import math
import numpy as np
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from datetime import datetime


def init_view(request):
    if request.method == 'POST':
        ts = int(datetime.now().timestamp() * 1000000)
        file_name = str(ts) + '.jpg'

        image = request.FILES.get('image')
        path = default_storage.save(file_name, ContentFile(image.read()))

        result = detect_image(path)
        print("result: ", result)
        context = {
            'result': result
        }
        return render(request, 'index.html', context)
    else:
        return render(request, 'index.html')
