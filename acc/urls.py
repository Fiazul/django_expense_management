from django.urls import path
from django.contrib.auth.views import PasswordResetDoneView
from .views import (
    Home,
    Login,
    Logout,
    Registration,
    ChangePassword,
    SendEmailToResetPassword,
    ResetPasswordConfirm,
    RegisterUserAPIView,
    LoginAPIView,
    VerifyEmailAPIView,
    PasswordResetRequestAPIView,
    PasswordResetConfirmAPIView,
    SendEmailAPIView,
)

urlpatterns = [
    path('api/send-verification-email/', SendEmailAPIView.as_view(),
         name='send-verification-email'),
    path('', Home.as_view(), name='home'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('registration/', Registration.as_view(), name='registration'),
    path('change_password/', ChangePassword.as_view(), name='change_password'),
    path('password_reset/', SendEmailToResetPassword.as_view(),
         name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name='acc/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', ResetPasswordConfirm.as_view(),
         name='password_reset_confirm'),
    path('api/register/', RegisterUserAPIView.as_view(), name='api_register'),
    path('api/login/', LoginAPIView.as_view(), name='api_login'),
    path('api/verify-email/', VerifyEmailAPIView.as_view(), name='api_verify_email'),
    path('api/password-reset/', PasswordResetRequestAPIView.as_view(),
         name='api_password_reset'),
    path('api/reset-password-confirm/', PasswordResetConfirmAPIView.as_view(),
         name='api_password_reset_confirm'),
]
