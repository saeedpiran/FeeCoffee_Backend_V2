from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts_module.models import User, UserMediaFiles
from auth_sms_module.models import VerificationCode


# User = get_user_model()


# signup first step
class RegistrationCheckSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=12)

    def validate_mobile(self, value):
        # Check if the user exists
        if User.objects.filter(mobile__iexact=value).exists():
            raise serializers.ValidationError('کاربری با این شماره موبایل قبلاً ثبت نام کرده است.', code='user_exists')
        return value


# signup second step
class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(max_length=255, write_only=True)
    verification_code = serializers.CharField(max_length=5, write_only=True)
    user_type = serializers.CharField(max_length=10)
    introducer_id = serializers.UUIDField(required=False, write_only=True)  # Use UUIDField for user id

    class Meta:
        model = User
        fields = ['mobile', 'verification_code', 'password', 'confirm_password', 'user_type', 'introducer_id']

    def validate(self, attrs):

        # Check if the verification code matches and is not expired
        mobile = attrs.get('mobile')
        verification_code = attrs.get('verification_code')
        try:
            code_record = VerificationCode.objects.get(mobile=mobile)
            if code_record.is_expired():
                raise serializers.ValidationError({
                    'احراز هویت': 'کد تایید منقضی شده است.'
                }, code='expired_code')
            if code_record.code != verification_code:
                raise serializers.ValidationError({
                    'احراز هویت': 'کد تایید وارد شده صحیح نمی‌باشد'
                }, code='invalid_code')
        except VerificationCode.DoesNotExist:
            raise serializers.ValidationError({
                'احراز هویت': 'کد تایید معتبر نیست'
            }, code='code_not_found')

        # Check if the passwords match
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({
                'کلمه عبور': 'رمز وارد شده و تکرار رمز مطابقت ندارند.'
            }, code='password_mismatch')

        # check complexity of password
        try:
            validate_password(attrs.get('password'))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({
                'کلمه عبور': ' '.join(e.messages)
            }, code='password_invalid')

        # Store the introducer instance
        attrs['introducer'] = None
        introducer_id = attrs.get('introducer_id')
        # print(introducer_id)
        if introducer_id:
            try:
                user = User.objects.get(id=introducer_id)
                # print("Introducer object fetched:", user)  # Print the whole introducer object

                attrs['introducer'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'معرف': 'کاربر معرفی کننده یافت نشد.'
                }, code='code_not_found')

        return super().validate(attrs)

    def create(self, validated_data):
        # Retrieve the introducer directly from validated_data
        introducer = validated_data.pop('introducer', None)

        validated_data.pop('confirm_password', None)
        validated_data.pop('verification_code', None)

        # Create the user and set introducer
        user = User.objects.create_user(introducer=introducer, **validated_data)
        return user


# ---------------------------------------------------------------------------
# change password
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    Confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('Confirm_password'):
            raise serializers.ValidationError({
                "کمه عبور": "کلمه عبور با تکرار آن مطابقت ندارد."
            }, code="password_mismatch")
        try:
            validate_password(attrs.get('new_password'))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"کلمه عبور جدید": list(e.messages)})

        return super().validate(attrs)


# ---------------------------------------------------------------------------
# forget password first step
class ForgetPassCheckSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=12)

    def validate_mobile(self, value):
        # Check if the user exists
        if not User.objects.filter(mobile__iexact=value).exists():
            raise serializers.ValidationError('کاربری با این شماره موبایل قبلاً ثبت نام نکرده است.',
                                              code='user_not_exists')
        return value


# forget password second step
class ForgetPassSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(max_length=255, write_only=True)
    verification_code = serializers.CharField(max_length=5, write_only=True)

    class Meta:
        model = User
        fields = ['mobile', 'verification_code', 'password', 'confirm_password']
        extra_kwargs = {
            'mobile': {'validators': []},  # Disable unique validation on the mobile field for this serializer
        }

    def validate(self, attrs):

        # Check if the verification code matches and is not expired
        mobile = attrs.get('mobile')
        verification_code = attrs.get('verification_code')
        try:
            code_record = VerificationCode.objects.get(mobile=mobile)
            if code_record.is_expired():
                raise serializers.ValidationError({
                    'احراز هویت': 'کد تایید منقضی شده است.'
                }, code='expired_code')
            if code_record.code != verification_code:
                raise serializers.ValidationError({
                    'احراز هویت': 'کد تایید وارد شده صحیح نمی‌باشد'
                }, code='invalid_code')
        except VerificationCode.DoesNotExist:
            raise serializers.ValidationError({
                'احراز هویت': 'کد تایید معتبر نیست'
            }, code='code_not_found')

        # Check if the passwords match
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({
                'کلمه عبور': 'رمز وارد شده و تکرار رمز مطابقت ندارند.'
            }, code='password_mismatch')

        # check complexity of password
        try:
            validate_password(attrs.get('password'))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({
                'کلمه عبور': ' '.join(e.messages)
            }, code='password_invalid')

        return attrs

    def get_object(self, mobile):
        try:
            return User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'کاربر': 'کاربر با این مشخصات یافت نشد.'
            }, code='user_not_found')

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get('password'))
        instance.save()
        validated_data.pop('confirm_password', None)
        validated_data.pop('verification_code', None)
        return instance

    def save(self, **kwargs):
        mobile = self.validated_data.get('mobile')
        user = self.get_object(mobile)
        return self.update(user, self.validated_data)


# ---------------------------------------------------------------------------
# Token login serializer
class CustomAuthTokenSerializer(serializers.Serializer):
    mobile = serializers.CharField(
        label="mobile",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label="Token",
        read_only=True
    )

    def validate(self, attrs):
        mobile = attrs.get('mobile')
        password = attrs.get('password')
        request = self.context.get('request')

        # Validate input presence
        if not mobile or not password:
            raise serializers.ValidationError({
                'error': 'نام کاربری و رمز عبور الزامی است.'
            }, code='bad request')

        # Authenticate the user
        user = authenticate(request=request, username=mobile, password=password)
        if user is None or not user.is_active:
            raise serializers.ValidationError({
                'error': 'امکان ورود با اطلاعات داده شده وجود ندارد.'
            }, code='authorization')

        # Set the authenticated user for later retrieval
        self.user = user

        # Mimic the structure of CustomTokenObtainPairSerializer by preparing a validated_data dict.
        validated_data = {}
        # If you had a parent class implementing additional validation logic,
        # you could call: validated_data = super().validate(attrs)
        validated_data.update({
            'user': user,
            'mobile': user.mobile,
            'user_id': user.id,
            'user_type': getattr(user, 'user_type', None)  # include if applicable
        })

        return validated_data


# -----------------------------------------------------------------
# File manager
class UserMediaFilesSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file = serializers.FileField(write_only=True)  # Add this field for file upload input
    is_active = serializers.BooleanField(default=True)  # Add default=True here

    class Meta:
        model = UserMediaFiles
        fields = ['id', 'media_type', 'file', 'file_url', 'caption', 'is_active']
        read_only_fields = ['id', 'created_date']  # Mark is_active as read-only.

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

    # def get_file_url(self, obj):
    #     request = self.context.get("request", None)
    #     if obj.file:
    #         if request:
    #             # Build the absolute URL (e.g. https://your-domain.com/...)
    #             return request.build_absolute_uri(obj.file.url)
    #         return obj.file.url
    #     return None


# --------------------------------------------------------------------
# User full name and type
class UserFullNameAndTypeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['user_type', 'full_name']

    def get_full_name(self, instance):
        return instance.get_full_name()

# ============================================================================

# JWT Login serializer
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get('mobile')
        password = attrs.get('password')
        request = self.context.get('request')

        # Validate input presence
        if not username or not password:
            raise serializers.ValidationError({
                'error': 'مقادیر نام کاربری و رمز عبور الزامی است.'
            }, code='bad request')

        # Optimize user lookup with select_related
        # user = User.objects.select_related('profile').filter(mobile=username).first()

        # # Optimize user lookup
        # user = User.objects.only('mobile').filter(mobile=username).first()

        # Authenticate the user
        user = authenticate(request=request, username=username, password=password)

        if user is None or not user.is_active:
            raise serializers.ValidationError({
                'error': 'نام کاربری یا رمز عبور صحیح نمی‌باشد.'
            }, code='authorization')

        # Set the authenticated user for token generation by the super method.
        self.user = user

        # Get validated data from the super class
        validated_data = super().validate(attrs)

        # Add additional fields to the validated data
        validated_data.update({
            'mobile': user.mobile,
            'user_id': user.id,
            'user_type': user.user_type
        })

        return validated_data

# =========================================================================================================
