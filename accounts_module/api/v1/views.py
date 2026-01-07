import re
from datetime import timedelta

from django.contrib.auth import logout
from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status, serializers
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.exceptions import ValidationError

from accounts_module.api.v1.paginations import DefaultPagination
from auth_sms_module.models import VerificationCode
from .permissions import IsOwnerOrAdminForUserMediaFiles
from .serializers import RegistrationSerializer, RegistrationCheckSerializer, \
    CustomTokenObtainPairSerializer, ChangePasswordSerializer, ForgetPassCheckSerializer, ForgetPassSerializer, \
    CustomAuthTokenSerializer, UserMediaFilesSerializer, UserFullNameAndTypeSerializer
from ...models import User, UserMediaFiles


# signup first step
class RegistrationCheckApiView(generics.GenericAPIView):
    """
    this class will check the imported mobile is existed in the database or not.
    if not then send a verification code to the mobile number and get bak the verification number
    and mobile number to the frontend.
    """
    serializer_class = RegistrationCheckSerializer

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = RegistrationCheckSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']

            # Validate mobile number format
            if not re.match(r'^09\d{9}$', mobile):
                return Response({
                    "success": False,
                    "error": "شماره موبایل باید با 09 شروع شده و 11 رقم باشد."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Generate and send verification code if the user does not exist
            verification_code = str(123)
            # verification_code = str(random.randint(10000, 99999))
            expires_at = timezone.now() + timedelta(minutes=3)  # Example: 10 minutes expiration

            # # Sending SMS using Faraz SMS
            # response = send_sms(mobile, verification_code)

            # Save the code to the database
            VerificationCode.objects.update_or_create(
                mobile=mobile,
                defaults={'code': verification_code, 'expires_at': expires_at}
            )

            # # # store verification code in cache
            # # cache.set(mobile, verification_code, timeout=100)

            # if response.get('code') == 200:
            #     return Response({
            #         "success": True,
            #         "data": {
            #             "mobile": mobile,
            #             # "verification_code": verification_code
            #         },
            #         "message": "کد اعتبارسنجی ارسال شد."
            #     }, status=status.HTTP_200_OK)
            # else:
            #     return Response({
            #         "success": False,
            #         "error": "کد اعتبارسنجی ارسال نشد."
            #     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                "success": True,
                "data": {
                    "mobile": mobile,
                    # "verification_code": verification_code
                },
                "message": "کد اعتبارسنجی ارسال شد."
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "user_exists": True,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# signup second step
class RegistrationApiView(generics.GenericAPIView):
    """
    in this view we get the signup form data and check whether everything is valid then save the user.
    then return the token to the frontend in order to login user.
    """
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Set the user as active
            user.is_active = True
            user.save()

            # Create a token for the user
            token, created = Token.objects.get_or_create(user=user)

            # Generate JWT token for the user
            # refresh = RefreshToken.for_user(user)
            # access = str(refresh.access_token)

            data = {
                'token': token.key,
                # 'refresh': str(refresh),
                # 'access': access,
                'mobile': serializer.validated_data['mobile'],
                'user_id': user.id,
                'user_type': serializer.validated_data['user_type'],
            }
            return Response({
                "success": True,
                "data": data,
                "message": 'کاربر با موفقیت ثبت شد.'  # Adjust this message to be more specific if needed
            }, status=status.HTTP_201_CREATED)

        # # Debugging: Print detailed errors
        # print("Serializer errors:", serializer.errors)

        return Response({
            "success": False,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------------------------------------------------------
# change password
class ChangePasswordApiView(generics.GenericAPIView):
    model = User
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # change old password
            if not self.object.check_password(serializer.data.get('old_password')):
                return Response({
                    "success": False,
                    "error": "کلمه عبور قبلی اشتباه است."
                }, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get('new_password'))
            self.object.save()

            # Retrieve the mobile number
            mobile = self.object.mobile
            user_id = self.object.id
            user = self.object
            user_type = self.object.user_type

            # Get or create the auth token for the user
            token, created = Token.objects.get_or_create(user=user)

            # # Generate JWT token for the user
            # refresh = RefreshToken.for_user(user)
            # access = str(refresh.access_token)

            data = {
                'token': token.key,
                # 'refresh': str(refresh),
                # 'access': access,
                'mobile': mobile,
                'user_id': user_id,
                'user_type': user_type,
            }

            return Response({
                "success": True,
                "data": data,
                "message": "کلمه عبور با موفقیت تغییر یافت."
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------------------------------------
# forget password first step
class ForgetPassCheckApiView(generics.GenericAPIView):
    """
    this class will check the imported mobile is existed in the database or not.
    if yes then send a verification code to the mobile number and get bak mobile number to the frontend.
    """
    serializer_class = ForgetPassCheckSerializer

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = ForgetPassCheckSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']

            # Validate mobile number format
            if not re.match(r'^09\d{9}$', mobile):
                return Response({
                    "success": False,
                    "error": "شماره موبایل باید با 09 شروع شده و 11 رقم باشد."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Generate and send verification code if the user does not exist
            verification_code = str(123)
            # verification_code = str(random.randint(10000, 99999))
            expires_at = timezone.now() + timedelta(minutes=3)  # Example: 10 minutes expiration

            # # Sending SMS using Faraz SMS
            # response = send_sms(mobile, verification_code)

            # Save the code to the database
            VerificationCode.objects.update_or_create(
                mobile=mobile,
                defaults={'code': verification_code, 'expires_at': expires_at}
            )

            # # store verification code in cache
            # cache.set(mobile, verification_code, timeout=100)

            # if response.get('code') == 200:
            #     return Response({
            #         "success": True,
            #         "data": {
            #             "mobile": mobile,
            #             # "verification_code": verification_code
            #         },
            #         "message": "کد اعتبارسنجی ارسال شد."
            #     }, status=status.HTTP_200_OK)
            # else:
            #     return Response({
            #         "success": False,
            #         "error": "کد اعتبارسنجی ارسال نشد."
            #     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                "success": True,
                "data": {
                    "mobile": mobile,
                    # "verification_code": verification_code
                },
                "message": "کد اعتبارسنجی ارسال شد."
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "user_exists": False,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# forget password second step
class ForgetPassApiView(generics.GenericAPIView):
    """
    in this view we get the forget pass form data and check whether everything is valid then save the user.
    then return the token to the frontend in order to login user.
    """
    serializer_class = ForgetPassSerializer

    def post(self, request, *args, **kwargs):
        serializer = ForgetPassSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Create a token for the user
            token, created = Token.objects.get_or_create(user=user)

            # # Generate JWT token for the user
            # refresh = RefreshToken.for_user(user)
            # access = str(refresh.access_token)

            data = {
                'token': token.key,
                # 'refresh': str(refresh),
                # 'access': access,
                'mobile': serializer.validated_data['mobile'],
                'user_id': user.id,
                'user_type': user.user_type
            }
            return Response({
                "success": True,
                "data": data,
                "message": 'کلمه عبور با موفقیت تغییر یافت.'  # Adjust this message to be more specific if needed
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------------------------------------
# login
# send token and id and mobile data to front when login
class CustomObtainAuthToken(ObtainAuthToken):
    """
    This view handles token-based authentication. It leverages the updated
    CustomAuthTokenSerializer to validate credentials, authenticate the user,
    and then generate (or retrieve) the auth token. The response includes additional
    user data for frontend consistency.
    """
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']

            # Get or create the auth token for the user
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'user_id': user.id,
                'mobile': user.mobile,
                'user_type': getattr(user, 'user_type', None)  # include if applicable
            }

            return Response({
                "success": True,
                "data": data,
                "message": "عملیات ورود با موفقیت انجام شد."
            }, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -------------------------------------------------------------------------
# logout
# delete the token for logout
class CustomDiscardAuthToken(APIView):
    """
    This view logs out the user by deleting their token.
    It handles potential errors to ensure a graceful response.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Attempt to retrieve the token associated with the user.
            token = request.user.auth_token
        except AttributeError:
            logout(request)
            # This exception could occur if the user object does not have an auth_token attribute.
            return Response({
                "success": False,
                "error": "توکنی برای کاربر وجود ندارد."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            # Attempt to delete the token.
            token.delete()
        except Exception as e:
            logout(request)
            # Catch any unexpected errors during deletion.
            return Response({
                "success": False,
                "error": f"خطا در حذف توکن: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logout(request)
        return Response({
            "success": True,
            "message": "توکن مورد نظر با موفقیت حذف شد."
        }, status=status.HTTP_200_OK)

    # def get(self, request):
    #     # Optionally handle GET requests similarly (although POST is preferred)
    #     return self.post(request)


# -----------------------------------------------------------------
# File manager
class UserAvatarUploadViewSet(viewsets.ModelViewSet):
    """
    Endpoint for uploading an avatar.

    On POST:
      - Expects a file upload (multipart form data).
      - Forces media_type to "avatar".
      - Associates the file with the current user.
      - Updates the user's 'avatar' field to reference the new media file.
    """
    serializer_class = UserMediaFilesSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = DefaultPagination

    def get_queryset(self):
        # Prevent errors during Swagger schema generation or if the user is not authenticated.
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return UserMediaFiles.objects.none()

        # Superusers (or staff) see everything.
        if self.request.user.is_staff or self.request.user.is_superuser:
            return UserMediaFiles.objects.all()

        # For normal users: filter by the user's files (assuming the user field expects a UUID or specific identifier)
        return UserMediaFiles.objects.filter(
            Q(user=self.request.user.id, media_type=UserMediaFiles.AVATAR) | Q(is_global=True)
        )

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [IsOwnerOrAdminForUserMediaFiles]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Override POST so that the new avatar is saved with media_type forced to "avatar"
        and associated with the current user. Also update the user's avatar field.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        response.message = "آواتار کاربر با موفقیت ایجاد شد."
        return response

        # return Response({
        #     "success": True,
        #     "data": serializer.data,
        #     "message": "آواتار کاربر با موفقیت ایجاد شد."
        # }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single avatar record in the envelope.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        response.message = "آواتار کاربر با موفقیت فراخوانی شد."
        return response

        # return Response({
        #     "success": True,
        #     "data": serializer.data,
        #     "message": "آواتار کاربر با موفقیت فراخوانی شد."
        # }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Update an avatar record and return it in the envelope.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        response.message = "آواتار کاربر با موفقیت به روز رسانی شد."
        return response

        # return Response({
        #     "success": True,
        #     "data": serializer.data,
        #     "message": "آواتار کاربر با موفقیت به روز رسانی شد."
        # }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Delete an avatar record and return the envelope.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        response = Response({}, status=status.HTTP_204_NO_CONTENT)
        response.message = "آواتار کاربر با موفقیت حذف شد."
        return response

        # return Response({
        #     "success": True,
        #     "data": {},
        #     "message": "آواتار کاربر با موفقیت حذف شد."
        # }, status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        """
        Override list() to return avatar records grouped by media_type in the envelope.
        In this example we’re splitting the query into global files and user-specific ones.
        """
        queryset = self.get_queryset()

        global_files_qs = queryset.filter(is_global=True)
        local_files_qs = queryset.exclude(is_global=True)

        global_serialized = self.get_serializer(global_files_qs, many=True).data
        user_serialized = self.get_serializer(local_files_qs, many=True).data

        grouped_global_files = self._group_by_media_type(global_serialized)
        grouped_local_files = self._group_by_media_type(user_serialized)

        response_data = {
            "global_files": grouped_global_files,
            "local_files": grouped_local_files,
        }
        response = Response(response_data, status=status.HTTP_200_OK)
        response.message = "آواتار‌ها با موفقیت فراخوانی شدند."
        return response

        # return Response({
        #     "success": True,
        #     "data": response_data,
        #     "message": "آواتار‌ها با موفقیت فراخوانی شدند."
        # }, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """
        Force media_type to "avatar" and associate the file with the current user.
        Also, update the user's avatar field.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            serializer.save(user=None, is_global=True)
        else:
            try:
                instance = serializer.save(
                    user=self.request.user,
                    media_type=UserMediaFiles.AVATAR,
                    is_global=False
                )
                # Update the user's avatar field.
                user.avatar = instance
                user.save()
            except User.DoesNotExist:
                raise ValidationError({
                    "user": "کاربری برای درخواست احراز هویت شده یافت نشد."
                })

    def _group_by_media_type(self, serialized_files):
        """
        Group the serialized file objects by their media_type.
        Returns a dictionary with media_type as keys and lists of file data as values.
        """
        grouped = {}
        for file in serialized_files:
            media_type = file.get("media_type")
            if media_type not in grouped:
                grouped[media_type] = []
            grouped[media_type].append(file)
        return grouped

# -----------------------------------------------------------------
# User full name and type
class UserFullNameAndTypeAPIView(APIView):
    """
    This APIView returns the authenticated user's type and full name.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Serialize the authenticated user's data.
        serializer = UserFullNameAndTypeSerializer(request.user)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        # Attach a custom message to the response.
        response.message = "اطلاعات کاربر با موفقیت فرواخوانی شد."
        return response
        # data = {
        #     "data": serializer.data,
        #     "message": "اطلاعات کاربر با موفقیت فراخوانی شد."
        # }
        # return Response(data, status=status.HTTP_200_OK)

# class UserFullNameAndType(viewsets.ReadOnlyModelViewSet):
#     """
#     This viewset provides a GET endpoint returning the authenticated
#     user's type and full name.
#     """
#     permission_classes = [IsAuthenticated]
#     serializer_class = UserFullNameAndTypeSerializer
#
#     def get_queryset(self):
#         # Filtering so that only the currently authenticated user is returned.
#         return User.objects.filter(id=self.request.user.id)
#
#     def list(self, request, *args, **kwargs):
#         # Using list() so that even if your router returns a list you only get one user.
#         user = request.user
#         serializer = self.get_serializer(user)
#         response = Response(serializer.data, status=status.HTTP_200_OK)
#         # Attach a custom message to the response.
#         response.message = "اطلاعات کاربر با موفقیت فرواخوانی شد."
#         return response

# ===============================================================
# JWT Login View
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    this view will create JWT token for user and get back
    to the frontend with user id and mobile data.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            return Response({
                'success': True,
                'data': serializer.validated_data,
                'message': 'عملیات ورود با موفقیت انجام شد.'
            }, status=status.HTTP_200_OK)
        except (TokenError, InvalidToken, serializers.ValidationError) as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# JWT Logout View
class LogoutView(APIView):
    """
    Logout view that blacklists the refresh token and logs the user out.
    Only authenticated users can access this endpoint.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            # Logout the user from Django
            logout(request)
            return Response({
                'success': True,
                'message': 'کاربر از قبل خارج شده است.'
            }, status=status.HTTP_200_OK)

        try:
            token = RefreshToken(refresh_token)

            # Blacklist the token
            token.blacklist()

            # Logout the user from Django
            logout(request)

            return Response({
                'success': True,
                'message': 'شما با موفقیت از حساب کاربری خود خارج شدید.'
            }, status=status.HTTP_200_OK)
        except TokenError as e:
            # Logout the user from Django
            logout(request)
            return Response({
                'success': True,
                'message': 'کاربر از قبل خارج شده است.'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            # Logout the user from Django
            logout(request)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
# ==================================================================
