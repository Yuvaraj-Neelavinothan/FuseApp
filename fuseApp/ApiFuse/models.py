from django.db import models
    
class JsonData(models.Model):
    apk_file_name = models.FileField(upload_to='apk_files/', null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.apk_file_name