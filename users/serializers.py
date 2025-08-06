from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import User, Profile
from knox.models import AuthToken


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'password', 'password2'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        
        # Send verification email
        request = self.context.get('request')
        if request:
            from users.utils.email import EmailVerification
            EmailVerification.send_verification_email(user, request)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
            
            if not user.is_active:
                msg = _('User account is disabled.')
                raise serializers.ValidationError(msg, code='authorization')
            
            if not user.is_verified:
                msg = _('User account is not verified.')
                raise serializers.ValidationError(msg, code='authorization')

        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    user_type = serializers.CharField(source='user.user_type', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'email', 'first_name', 'last_name', 'phone', 'user_type',
            'gender', 'date_of_birth', 'profile_picture', 'bio',
            'address', 'city', 'state', 'country', 'postal_code',
            'website', 'social_media', 'preferences',
            'email_notifications', 'push_notifications', 'age'
        ]
        read_only_fields = ['age']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone', 'user_type',
            'is_verified', 'last_login', 'created_at', 'updated_at', 'profile'
        ]
        read_only_fields = [
            'id', 'is_verified', 'last_login', 'created_at', 'updated_at'
        ]


class AuthUserSerializer(UserSerializer):
    token = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['token']

    def get_token(self, obj):
        return AuthToken.objects.create(obj)[1]