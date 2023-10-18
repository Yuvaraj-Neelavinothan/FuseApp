from rest_framework import serializers
from .models import JsonData
from django.contrib.auth.hashers import make_password

class JsonDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = JsonData
        fields = ('file_name', 'ip_address', 'password')
        
    def create(self, validated_data):
        ip_address = self.context['request'].META.get('REMOTE_ADDR')
        hased_password = validated_data['password']
        if hased_password != '':
            hased_password = make_password(hased_password)
        else:
            hased_password = ''
        json_data = JsonData(file_name = validated_data['file_name'],
                             ip_address = ip_address,
                             password = hased_password)
        json_data.save()
        return json_data