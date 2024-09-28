from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail

from django.conf import settings

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email_or_username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, data):
        email_or_username = data.get('email_or_username')
        password = data.get('password')

        user = User.objects.filter(email=email_or_username).first(
        ) or User.objects.filter(username=email_or_username).first()
        if user and user.check_password(password):
            if not user.is_active:
                raise serializers.ValidationError('Please verify your email.')

            user = authenticate(username=user.username, password=password)
            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.')

            return {'user': user}
        else:
            raise serializers.ValidationError('Invalid credentials.')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email is already in use.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False
        )

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_link = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"

        send_mail(
            'Verify Your Email',
            f'Click the link to verify your email: {verification_link}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )

        return user


class VerifyEmailSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data):
        try:
            uid = urlsafe_base64_decode(data.get('uid')).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError(
                'Invalid token or user does not exist.')

        if not default_token_generator.check_token(user, data.get('token')):
            raise serializers.ValidationError(
                'Invalid token or token expired.')

        return data

    def save(self):
        uid = urlsafe_base64_decode(self.validated_data['uid']).decode()
        user = User.objects.get(pk=uid)
        user.is_active = True
        user.save()
        return user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with this email does not exist.")
        return value

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        send_mail(
            'Password Reset Request',
            f'Click the link to reset your password: {reset_link}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data):
        uid = urlsafe_base64_decode(data.get('uid')).decode()
        user = User.objects.get(pk=uid)

        if not default_token_generator.check_token(user, data.get('token')):
            raise serializers.ValidationError(
                'Invalid token or token expired.')

        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError("Passwords do not match.")

        return data

    def save(self):
        uid = urlsafe_base64_decode(self.validated_data['uid']).decode()
        user = User.objects.get(pk=uid)
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return user


class SendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("The email is not registered.")
        return value

    def send_verification_email(self, user):
        subject = 'Email Verification'
        message = f'Please verify your email by clicking the link: {self.verification_link(user)}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]

        send_mail(subject, message, from_email, to_email)

    def verification_link(self, user):
        uid = ...
        token = ...
        return f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"

    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        self.send_verification_email(user)
        return user
