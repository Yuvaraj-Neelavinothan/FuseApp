from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import JsonData
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
import qrcode
import os
import uuid
import ipaddress
from PIL import Image
from django.templatetags.static import static

# store upload file and generate qr code and password.
@api_view(['POST'])
def store_json_data(request):
    if(request.method == 'POST'):
        apk_file = request.FILES.get('apk_file')
        if not apk_file:
            return Response({"error":"Please upload Apk file."}, status.HTTP_400_BAD_REQUEST)
        if not apk_file.name.endswith('.apk'):
            return Response({"error":"Please upload valid Apk file."}, status.HTTP_400_BAD_REQUEST)
        ip_address = request.META.get('REMOTE_ADDR')
        password = request.data.get('password','')
        hased_password = make_password(password) if password else ''
        fs = FileSystemStorage(location='media/apk_files')
        upld_file_name = fs.save(apk_file.name, apk_file)
        
        json_data = JsonData(apk_file_name = upld_file_name,
                             ip_address = ip_address,
                             password = hased_password)
        json_data.save()
        latest_row = JsonData.objects.latest('id')
        id = latest_row.id
        if hased_password:
            response_data = {"id":id}
        else:
            qr_path = generate_qr_code(request, id)
            response_data = {"qr_image_path":qr_path} 
        return Response(response_data, status.HTTP_201_CREATED)
    
# Generate QR code function. 
def generate_qr_code(request, id):
    rowRec = JsonData.objects.get(id=id)
    fileName = f'{id}-{uuid.uuid4()}.png'
    qr = qrcode.QRCode(
        version = 1,
        error_correction = qrcode.constants.ERROR_CORRECT_L,
        box_size = 10,
        border = 4,
    )
    dl_path = reverse('download_ApkFile', args=[id])
    abslt_path = request.build_absolute_uri(dl_path)
    qr.add_data(abslt_path)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color= "white")
    qr_image_path = f'ApiFuse/static/qr_images/{fileName}'
    qr_image.save(qr_image_path)
    img_name = f'qr_images/{fileName}'
    abslt_path = request.build_absolute_uri(settings.STATIC_URL + img_name)
    return abslt_path

# checking password api: if password matching it generate qr code else return error msg.
@api_view(['POST'])
def checking_password(request):
    if(request.method == 'POST'):
        id_ip = request.data.get('id')
        if not id_ip.isdigit():
            return JsonResponse({"error":"Invalid ID format"}, status=400)
        password = request.data.get('password')
        try:
            json_data = JsonData.objects.get(id=id_ip)
            stored_password = json_data.password
            if check_password(password, stored_password):
                qr_path = generate_qr_code(request, id_ip)
                response_data = {"qr_image_path":qr_path}
                return Response(response_data, status.HTTP_201_CREATED)
            else:
                response_data = {"error":"Password is Mismatch, please provide valid password"}
                return Response(response_data, status.HTTP_400_BAD_REQUEST)
    
        except JsonData.DoesNotExist:
            response_data = {"error":"Invalid ID, record not found"}
            return Response(response_data, status.HTTP_404_NOT_FOUND)
        
# show template page.
def show_qr(request):
    return render(request, 'showQRcode.html')

# collecting uploaded apk file names api.
@api_view(['POST'])
def collect_uploaded_apk_file(request):
    if (request.method == 'POST'):
        ip_address = request.data.get('ip_address')
        # validate ip address
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            return JsonResponse({"error":"invalid ip address"}, status=400)
        all_upld_files = JsonData.objects.filter(ip_address = ip_address)
        apk_files_dict = {}
        for data in all_upld_files:
            file_name = os.path.basename(data.apk_file_name.url)
            apk_files_dict[data.id] = file_name
        return JsonResponse(apk_files_dict, status=200)
    
# download apk file
def download_apk_file(request, id):
    try:
        json_data = JsonData.objects.get(id = id)
        file_name = os.path.basename(json_data.apk_file_name.url)
        file_path = os.path.join(settings.MEDIA_ROOT, 'apk_files', file_name)
        
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type = 'application/vnd.android.package-archive')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    except JsonData.DoesNotExist:
        return HttpResponse("Apk file not found", status=404)
    