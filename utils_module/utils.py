from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated

from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


# -----------------------------------------------------------------------------------
# restframework exception handler
def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns errors in the standard envelope format.
    Also, for LogoutView, if the error is AuthenticationFailed, a 200 response is returned.
    """
    # Let DRF generate its default response.
    response = exception_handler(exc, context)
    view = context.get('view')

    # Special handling for LogoutView's AuthenticationFailed exception.
    if isinstance(exc, AuthenticationFailed) and view and view.__class__.__name__ == 'LogoutView':
        return Response({
            "success": True,
            "data": {},
            "message": "کاربر از قبل خارج شده یا دسترسی توکن منقضی شده است."
        }, status=status.HTTP_200_OK)

    # For authentication errors elsewhere, enforce a 401 status code.
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)) and response is not None:
        response.status_code = status.HTTP_401_UNAUTHORIZED

    if response is not None:
        # Check if the response data has a 'detail' key.
        if isinstance(response.data, dict) and 'detail' in response.data:
            detail_msg = response.data.get('detail')
            # For 404 errors, we force a specific Persian message.
            if response.status_code == 404:
                persian_detail = "رکورد مورد نظر یافت نشد."
            else:
                # Otherwise, translate whatever detail we have.
                persian_detail = detail_msg
            response.data = {
                "success": False,
                "data": {},
                "error": {"detail": persian_detail}
            }
        else:
            response.data = {
                "success": False,
                "data": {},
                "error": response.data
            }
    return response


# --------------------------------------------------------------------------------
# Clean database from blacklisted and expired JWT
def cleanup_old_outstanding_tokens(days=45):
    """
    Deletes outstanding tokens that expired more than `days` days ago.

    Args:
        days (int): Number of days beyond expiration to keep the token.

    Returns:
        int: Count of outstanding tokens deleted.
    """
    # Compute the threshold; tokens expired before this date will be deleted.
    threshold_date = timezone.now() - timedelta(days=days)
    tokens_to_delete = OutstandingToken.objects.filter(expires_at__lt=threshold_date)
    count = tokens_to_delete.count()
    tokens_to_delete.delete()
    return count


def cleanup_old_blacklisted_tokens(days=10):
    """
    Deletes blacklisted tokens that were blacklisted more than `days` days ago.

    Args:
        days (int): Number of days after which a blacklisted token should be deleted.

    Returns:
        int: Count of blacklisted tokens deleted.
    """
    # Compute the threshold; tokens blacklisted before this date will be deleted.
    threshold_date = timezone.now() - timedelta(days=days)
    tokens_to_delete = BlacklistedToken.objects.filter(blacklisted_at__lt=threshold_date)
    count = tokens_to_delete.count()
    tokens_to_delete.delete()
    return count


# --------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------


# =====================================================================================
# import io
# import os
# import urllib.parse
#
# import arabic_reshaper
# from bidi.algorithm import get_display
# from django.conf import settings
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# from reportlab.pdfgen import canvas


# # Generate PDF
# def generate_pdf(shop):
#     # Create a buffer to hold the PDF data
#     buffer = io.BytesIO()
#
#     # Create a canvas object
#     pdf = canvas.Canvas(buffer, pagesize=letter)
#     width, height = letter
#
#     # Register and set the Almarai font
#     pdfmetrics.registerFont(TTFont('Almarai', 'static/fonts/Almarai-Light.ttf'))
#     pdf.setFont('Almarai', 18)
#
#     # Set title
#     title = f"منوی کافه {shop.name}"
#     reshaped_title = arabic_reshaper.reshape(title)  # Reshape the title
#     bidi_title = get_display(reshaped_title)  # Correct the display order
#     text_width = pdf.stringWidth(bidi_title, 'Almarai', 18)
#     pdf.drawString((width - text_width) / 2, height - 50, bidi_title)
#
#     # Fetch product categories
#     product_categories = CafeProductCategory.objects.filter(product_categories__shop=shop).distinct()
#
#     # Set starting point for the product list
#     pdf.setFont('Almarai', 12)
#     y = height - 100
#
#     for category in product_categories:
#         # Draw category title on the right side
#         category_title = category.title
#         reshaped_category_title = arabic_reshaper.reshape(category_title)
#         bidi_category_title = get_display(reshaped_category_title)
#         pdf.setFont('Almarai', 14)
#         pdf.drawRightString(width - 50, y, bidi_category_title)
#         pdf.setFont('Almarai', 12)
#         y -= 30
#
#         # Fetch products for the current category in the desired order
#         cafe_products = Product.objects.filter(shop=shop, category=category, product_type='cafe')
#         other_products = Product.objects.filter(shop=shop, category=category).exclude(product_type='cafe').exclude(
#             product_type='sop')
#         sop_products = Product.objects.filter(shop=shop, category=category, product_type='sop')
#         products = list(cafe_products) + list(other_products) + list(sop_products)
#
#         for product in products:
#             name = f"{product.name}"
#             price = f"{product.last_price:,}  تومان "  # Add thousands separator
#             reshaped_name = arabic_reshaper.reshape(name)  # Reshape the product name
#             bidi_name = get_display(reshaped_name)  # Correct the display order
#             reshaped_price = arabic_reshaper.reshape(price)  # Reshape the product price
#             bidi_price = get_display(reshaped_price)  # Correct the display order
#
#             # Draw the product image above the product name
#             first_image_url = product.get_first_image_url()
#             if first_image_url:
#                 # Convert the relative image path to an absolute path
#                 absolute_image_path = os.path.join(settings.MEDIA_ROOT, first_image_url.replace(settings.MEDIA_URL, ''))
#                 # Decode the URL-encoded characters
#                 absolute_image_path = urllib.parse.unquote(absolute_image_path)
#                 pdf.drawImage(absolute_image_path, width - 100, y - 50, width=50, height=37.5, preserveAspectRatio=True)
#                 y -= 40  # Adjust the y position to accommodate the image
#
#             # Draw the product name and price aligned with the image
#             pdf.drawRightString(width - 150, y, bidi_name)
#             pdf.drawString(50, y, bidi_price)  # Position the price on the left side
#             y -= 20  # Further reduce the y position for the next product and separator line
#
#             # Draw a thin line separator
#             pdf.line(50, y + 10, width - 50, y + 10)
#             y -= 10  # Reduce vertical space between products
#
#             if y < 150:
#                 pdf.showPage()  # Create a new page
#                 y = height - 50
#
#         y -= 20  # Add some space after each category
#
#     # Save the PDF file
#     pdf.save()
#
#     # Move the buffer position to the beginning
#     buffer.seek(0)
#
#     return buffer
