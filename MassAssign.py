from rest_framework import serializers

from .models import User, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'is_superuser', 'is_staff', 'is_active',
            'last_login', 'date_joined'
        ]


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'date_joined',
            'last_login'
        ]


class UserContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(many=False, read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'picture', 'user', 'birthdate', 'about', 'country', 'education_level',
            'graduation_date', 'dismissed_date'
        ]


class UserProfileContactSerializer(serializers.ModelSerializer):
    user = UserContactSerializer(many=False, read_only=True)

    class Meta:
        model = UserProfile
        fields = ['picture', 'user']


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
