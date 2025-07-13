from rest_framework import serializers
from core.models import Usuario


class UsusarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["public_id", "username", "email", "first_name", "last_name"]
