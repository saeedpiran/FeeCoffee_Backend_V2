
from django.http import JsonResponse
from .utils import send_sms

# Create your views here.


def send_sms_view(request):
    recipient = request.GET.get('recipient')
    verification_code = request.GET.get('code')

    if recipient and verification_code:
        response = send_sms(recipient, verification_code)
        return JsonResponse(response)
    else:
        return JsonResponse({'error': 'Missing recipient or code'}, status=400)

