from django.urls import path
from . import views

urlpatterns = [
    path('store-json-data/', views.store_json_data, name='store_json_data'),
    path('check-password/', views.checking_password, name="checking_password"),
    path('view-qr-code/', views.show_qr, name="show_qr"),
    path('uploaded-apk-file/', views.collect_uploaded_apk_file, name="collecting_apkfiles"),
    path('download-apk-file/<int:id>/', views.download_apk_file, name="download_ApkFile"),
]