from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .mixins import LogoutRequiredMixin
from .forms import (
    LoginForm,
    UserRegistrationForm,
    ChangePasswordForm,
    SendEmailForm,
    ResetPasswordConfirmForm,

)


@method_decorator(never_cache, name='dispatch')
class Home(LoginRequiredMixin, generic.TemplateView):
    login_url = 'login'
    template_name = "acc/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


@method_decorator(never_cache, name='dispatch')
class Login(LogoutRequiredMixin, generic.View):
    def get(self, *args, **kwargs):
        form = LoginForm()
        context = {"form": form}
        return render(self.request, 'acc/login.html', context)

    def post(self, *args, **kwargs):
        form = LoginForm(self.request.POST)

        if form.is_valid():
            user = authenticate(
                self.request,
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password')
            )
            if user:
                login(self.request, user)

                return redirect('home')
            else:
                messages.warning(self.request, "Wrong credentials")
                return redirect('login')

        return render(self.request, 'acc/login.html', {"form": form})


class Logout(generic.View):
    def get(self, *args, **kwargs):
        logout(self.request)
        return redirect('login')


@method_decorator(never_cache, name='dispatch')
class Registration(LogoutRequiredMixin, generic.CreateView):
    template_name = 'acc/registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Registration Successful!")
        return super().form_valid(form)


@method_decorator(never_cache, name='dispatch')
class ChangePassword(LoginRequiredMixin, generic.FormView):
    template_name = 'acc/change_password.html'
    form_class = ChangePasswordForm
    login_url = reverse_lazy('login')
    success_url = reverse_lazy('login')

    def get_form_kwargs(self):
        context = super().get_form_kwargs()
        context['user'] = self.request.user
        return context

    def form_valid(self, form):
        user = self.request.user
        user.set_password(form.cleaned_data.get('new_password1'))
        user.save()
        messages.success(self.request, "Password changed Successfully!")
        return super().form_valid(form)


class SendEmailToResetPassword(PasswordResetView):
    template_name = 'acc/password_reset.html'
    form_class = SendEmailForm


class ResetPasswordConfirm(PasswordResetConfirmView):
    template_name = 'acc/password_reset_confirm.html'
    form_class = ResetPasswordConfirmForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Password reset successfully!")
        return super().form_valid(form)
