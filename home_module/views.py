from audioop import reverse

from django.http import HttpResponse
from django.shortcuts import render, redirect

from article_module.models import Article
from shop_module.models import Shop
from site_module.models import SiteSetting


# Create your views here.

def home_index(request):
    last_articles = Article.objects.all().order_by('-created_date')
    last_articles = last_articles[:3]
    setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
    context = {
        'site_setting': setting,
        'last_articles': last_articles
    }
    return render(request, 'home_module/index.html', context)


def site_header_component(request):
    setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()

    context = {
        'site_setting': setting,
    }
    if request.user.is_authenticated:
        context['user'] = request.user

    return render(request, 'shared/site_header_components.html', context)


def site_footer_component(request):
    setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
    # footer_link_boxes = FooterLinkBox.objects.all()
    # for item in footer_link_boxes:
    #     item.footerlink_set
    context = {
        'site_setting': setting,
        # 'footer_link_boxes': footer_link_boxes
    }
    return render(request, 'shared/site_footer_components.html', context)

def transfer_page_shop(request):
    user = request.user
    if user.is_authenticated:
        user_type = getattr(user, 'user_type', None)
        if user_type == 'customer':
            return render(request, 'cafe_market_module/cafe_market_index.html')
        elif user_type == 'seller':
            user_id = user.id
            shops = Shop.objects.filter(owner_id=user_id)
            if shops.exists():
                shop = shops.first()  # Handling multiple shops scenario
                return redirect('shop_dashboard_page', shop_id=shop.id)
            return HttpResponse("No shops found for this seller.")
        else:
            return HttpResponse("Invalid user type.")
    else:
        return redirect('send_verification_code', type='seller')  # Redirect to login

# Ensure your `urls.py` is correctly set up to capture necessary arguments like `shop_id`.
