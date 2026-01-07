from django.contrib.auth import logout, login
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from shop_module.models import Shop
from .forms import LoginForm
from .models import User


# Create your views here.


class LoginView(View):
    """
    with this class all users can login an go to their relevant page.
    for customer user they will see the cafe marketplace page.
    for sellers they will see their shop dashboard page.
    """

    def get(self, request):
        login_form = LoginForm()
        # Get recipient mobile number from the session
        mobile = request.session.get('recipient', '')
        context = {
            'login_form': login_form,
            'mobile': mobile
        }
        return render(request, 'accounts_module/login_page.html', context)

    def post(self, request: HttpRequest):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_mobile = login_form.cleaned_data.get('mobile')
            user_password = login_form.cleaned_data.get('password')
            user: User = User.objects.filter(mobile__iexact=user_mobile).first()

            if user is not None:
                if not user.is_active:
                    login_form.add_error('mobile', 'حساب کاربری شما فعال نشده است')
                else:
                    is_password_correct = user.check_password(user_password)
                    if is_password_correct:
                        login(request, user)
                        user_type = user.user_type
                        user_id = user.id
                        if user_type == 'seller':
                            shop: Shop = Shop.objects.filter(profile__owner_id=user_id).first()
                            if shop is not None:
                                return redirect(reverse('home_page'))
                            else:
                                return redirect(reverse('home_page'))  # change View to destination
                        elif user_type == 'customer':
                            return redirect(reverse('home_page'))
                        elif user_type == 'admin':
                            return redirect(reverse('home_page'))  # change View to destination
                    else:
                        login_form.add_error('mobile', 'نام کاربری و یا کلمه عبور اشتباه است')
            else:
                login_form.add_error('mobile', 'کاربری با این مشخضات یافت نشد')
                # return redirect(reverse('login_page'))  # change View to destination

        context = {
            'login_form': login_form
        }
        return render(request, 'accounts_module/login_page.html', context)


class LogoutView(View):
    """
    logout all user from the site
    """

    def get(self, request):
        logout(request)
        return redirect(reverse('home_page'))
