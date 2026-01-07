from collections.abc import Iterable

from rest_framework import serializers

from accounts_module.models import User, UserMediaFiles
from shop_module.models import CafeTableQrCodes, ShopMediaFiles
from shop_module.models import Shop, ShopProfile
from shop_module.models import ShopOpenDays, ShopOpenHours


# serializers.py

# ---------------------------------------------------------------
# Shop Profile
# -----------------------------------------------
#           Serializers for Related Images
class ShopCertificateImageSerializerForProfile(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ShopMediaFiles
        fields = ['id', 'media_type', 'file_url', 'is_active', 'caption']
        read_only_fields = ['id', 'created_date']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class ShopIdCardImageSerializerForProfile(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ShopMediaFiles
        fields = ['id', 'media_type', 'file_url', 'is_active', 'caption']
        read_only_fields = ['id', 'created_date']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

# -----------------------------------------------------
#             Avatar Serializers for User
# For GET requests: the avatar returns full information.
class ShopOwnerAvatarSerializerForProfile(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = UserMediaFiles  # The avatar is stored as a UserMediaFiles instance.
        fields = ['id', 'media_type', 'file_url', 'is_active', 'caption']
        read_only_fields = ['id']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

# -----------------------------------------------------
#         User Read and Write Serializers
# For GET responses, return full avatar details.
class UserReadSerializerForProfile(serializers.ModelSerializer):
    avatar = ShopOwnerAvatarSerializerForProfile(
        read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'mobile', 'id_number', 'avatar']
        read_only_fields = ['id', 'mobile']

# For edit/create (write) actions, accept the avatar as an ID only.
class UserWriteSerializerForProfile(serializers.ModelSerializer):
    # Use an IntegerField to expect only a primary key for the avatar.
    avatar = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'id_number', 'avatar']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        # Pop the avatar field if present to handle it separately.
        avatar_pk = validated_data.pop('avatar', None)

        # Update other fields from the validated data.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # If an avatar id is provided, update the avatar field.
        if avatar_pk is not None:
            try:
                avatar_instance = UserMediaFiles.objects.get(pk=avatar_pk)
                instance.avatar = avatar_instance
            except UserMediaFiles.DoesNotExist:
                raise serializers.ValidationError({"avatar": "Invalid avatar id."})

        instance.save()
        return instance

# -----------------------------------------------------
#         ShopProfile Serializers
# Read Serializer returns full details for certificates, id_card, and owner.
class ShopProfileReadSerializer(serializers.ModelSerializer):
    owner = UserReadSerializerForProfile(required=False)
    certificate_images = ShopCertificateImageSerializerForProfile(
        source='shop.certificate', many=True, read_only=True
    )
    id_card_image = ShopIdCardImageSerializerForProfile(
        source='shop.id_card', read_only=True
    )

    class Meta:
        model = ShopProfile
        fields = [
            'id',
            'owner',
            'latitude',
            'longitude',
            'postal_code',
            'number',
            'address',
            'city',
            'state',
            'country',
            'certificate_images',
            'id_card_image',
            'is_complete',
        ]
        read_only_fields = ['id']


# Write Serializer expects image IDs for certificates and id_card.
# The nested owner uses the write serializer so that avatar is accepted as an id.
class ShopProfileWriteSerializer(serializers.ModelSerializer):
    owner = UserWriteSerializerForProfile(required=False)
    certificate = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    id_card = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = ShopProfile
        fields = [
            'id',
            'owner',
            'latitude',
            'longitude',
            'postal_code',
            'number',
            'address',
            'city',
            'state',
            'country',
            'certificate',  # list of certificate image IDs
            'id_card',      # single id card image ID
            'is_complete',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        # Enforce that user-related fields such as 'avatar', 'first_name',
        # 'last_name', and 'id_number' are only provided inside the "owner" object.
        disallowed_keys = ['avatar', 'first_name', 'last_name', 'id_number']
        # `self.initial_data` holds the raw input payload.
        # If any disallowed key is at the root level, raise a validation error.
        for key in disallowed_keys:
            if key in self.initial_data:
                raise serializers.ValidationError({key: "This field should be nested inside 'owner'."})
        return super().validate(attrs)

    def update(self, instance, validated_data):
        # Update owner data if provided.
        owner_data = validated_data.pop('owner', None)
        if owner_data:
            owner_serializer = UserWriteSerializerForProfile(
                instance=instance.owner,
                data=owner_data,
                partial=True,
                context=self.context
            )
            owner_serializer.is_valid(raise_exception=True)
            owner_serializer.save()

        # Extract image IDs.
        certificate_ids = validated_data.pop('certificate', None)
        id_card_id = validated_data.pop('id_card', None)

        # Update ShopProfile fields.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Access the related Shop instance (assuming a one-to-one relationship).
        shop = instance.shop

        if certificate_ids is not None:
            certificates = ShopMediaFiles.objects.filter(
                id__in=certificate_ids,
                media_type=ShopMediaFiles.CERTIFICATE
            )
            shop.certificate.set(certificates)

        if id_card_id is not None:
            try:
                id_card_instance = ShopMediaFiles.objects.get(
                    id=id_card_id,
                    media_type=ShopMediaFiles.IDCARD
                )
                shop.id_card = id_card_instance
                shop.save()
            except ShopMediaFiles.DoesNotExist:
                raise serializers.ValidationError({
                    "id_card": "Invalid id card image id."
                })

        return instance

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Shop is complete Profile Status
# -----------------------------------------------
class ShopProfileIsCompleteStatusSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()

    class Meta:
        model = ShopProfile
        fields = [
            'is_complete',
            'user_type'
        ]

    def get_user_type(self, obj):
        request = self.context.get('request')
        return request.user.user_type if request and hasattr(request, 'user') else None

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Shop panel
# -----------------------------------------------
#         Media Files Serializer for Shop Panel
# Media Files Serializer (for panel read operations)
class ShopMediaFilesForPanelSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ShopMediaFiles
        fields = [
            'id',
            'media_type',
            'is_active',
            'file_url',
            'caption',
        ]
        # These are read-only properties.
        read_only_fields = ['id', 'file_url', 'created_date', 'is_global', 'is_active']
        ref_name = 'ShopMediaFileDetailsForPanel'

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None


# -----------------------------------------------------
# Owner Serializers
# Read serializer returns nested avatar details.
class ShopOwnerReadForPanelSerializer(serializers.ModelSerializer):
    avatar = serializers.PrimaryKeyRelatedField(
        queryset=UserMediaFiles.objects.filter(media_type=UserMediaFiles.AVATAR),
        required=False,
        allow_null=True
    )

    class Meta:
        model = User
        fields = ['id', 'mobile', 'first_name', 'last_name', 'avatar']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        avatar_obj = instance.avatar
        rep['avatar'] = (
            ShopMediaFilesForPanelSerializer(avatar_obj, context=self.context).data
            if avatar_obj else None
        )
        return rep


# For edit/create actions, accept the avatar as an ID only.
class ShopOwnerWriteForPanelSerializer(serializers.ModelSerializer):
    # Expect just an integer ID for avatar.
    avatar = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'id_number', 'avatar']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        # Pop the avatar field if present.
        avatar_pk = validated_data.pop('avatar', None)
        # Update other fields.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        # Update avatar if provided.
        if avatar_pk is not None:
            try:
                avatar_instance = UserMediaFiles.objects.get(pk=avatar_pk)
                instance.avatar = avatar_instance
            except UserMediaFiles.DoesNotExist:
                raise serializers.ValidationError({"avatar": "Invalid avatar id."})
        instance.save()
        return instance


# -----------------------------------------------------
#           Serializers for Related Images
class ShopCertificateImageSerializerForPanel(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ShopMediaFiles
        fields = ['id', 'media_type', 'file_url', 'is_active', 'caption']
        read_only_fields = ['id', 'created_date']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class ShopIdCardImageSerializerForPanel(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ShopMediaFiles
        fields = ['id', 'media_type', 'file_url', 'is_active', 'caption']
        read_only_fields = ['id', 'created_date']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

# -----------------------------------------------------
# Shop Profile Serializers for Panel
# Read serializer returns full shop profile details.
class ShopProfileReadSerializerForPanel(serializers.ModelSerializer):
    owner = ShopOwnerReadForPanelSerializer(read_only=True)
    certificate_images = ShopCertificateImageSerializerForProfile(
        source='shop.certificate', many=True, read_only=True
    )
    id_card_image = ShopIdCardImageSerializerForProfile(
        source='shop.id_card', read_only=True
    )

    class Meta:
        model = ShopProfile
        fields = [
            'id',
            'owner',
            'postal_code',
            'number',
            'address',
            'city',
            'state',
            'country',
            'certificate_images',
            'id_card_image',
            'is_complete',
            'is_verified',
        ]
        read_only_fields = fields


# Write serializer accepts nested profile data.
# Note that we add an explicit 'owner' field that is write-only.
class ShopProfileWriteSerializerForPanel(serializers.ModelSerializer):
    owner = ShopOwnerWriteForPanelSerializer(write_only=True)
    certificate = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    id_card = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = ShopProfile
        fields = [
            'owner',
            'postal_code',
            'number',
            'address',
            'city',
            'state',
            'country',
            'certificate',
            'id_card',
        ]

    def create(self, validated_data):
        """
        Expect a 'shop' instance to be provided in the serializer context.
        The nested owner data is used to update the existing shop owner.
        """
        owner_data = validated_data.pop('owner', None)
        # Get the shop from context (provided by the parent serializer).
        shop = self.context.get("shop", None)
        if not shop:
            raise serializers.ValidationError("Shop instance must be provided for profile creation.")
        profile = ShopProfile.objects.create(shop=shop, **validated_data)
        # Update the profile's owner if data was provided.
        if owner_data:
            # Assume the ShopProfile already has a related 'owner'
            owner_instance = profile.owner
            owner_serializer = ShopOwnerWriteForPanelSerializer(instance=owner_instance, data=owner_data, partial=True)
            owner_serializer.is_valid(raise_exception=True)
            owner_serializer.save()
        return profile

    def update(self, instance, validated_data):
        """
        Update instance fields and update the nested owner using its write serializer.
        """
        owner_data = validated_data.pop('owner', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if owner_data:
            owner_serializer = ShopOwnerWriteForPanelSerializer(instance=instance.owner, data=owner_data, partial=True)
            owner_serializer.is_valid(raise_exception=True)
            owner_serializer.save()
        return instance


# -----------------------------------------------------
# Shop Panel Serializers
# Read serializer returns complete nested details.
class ShopPanelReadSerializer(serializers.ModelSerializer):
    profile = ShopProfileReadSerializerForPanel(read_only=True)
    logo = ShopMediaFilesForPanelSerializer(read_only=True)
    banner = ShopMediaFilesForPanelSerializer(many=True, read_only=True)
    shop_qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = [
            'id',
            'name',
            'profile',  # Nested profile details
            'manager_name',
            'manager_mobile',
            'description',
            'logo',  # Full media details
            'banner',
            'shop_url',
            'shop_qr_code_url',
            'number_of_tables',
            'shop_type',
            'monetary_unit',
            'free_delivery',
            'pickup',
            'phone_number',
        ]
        read_only_fields = fields

    def get_shop_qr_code_url(self, obj):
        request = self.context.get('request')
        if obj.shop_qr_code and hasattr(obj.shop_qr_code, 'url'):
            return request.build_absolute_uri(obj.shop_qr_code.url) if request else obj.shop_qr_code.url
        return None


# Write serializer accepts editable shop and nested profile data.
# Note: Media file fields (logo, banner) are accepted as IDs.
class ShopPanelWriteSerializer(serializers.ModelSerializer):
    logo = serializers.PrimaryKeyRelatedField(
        queryset=ShopMediaFiles.objects.filter(media_type=ShopMediaFiles.LOGO),
        required=False,
        allow_null=True,
        write_only=True,
        help_text="ID of the logo ShopMediaFile."
    )
    banner = serializers.PrimaryKeyRelatedField(
        queryset=ShopMediaFiles.objects.filter(
            media_type__in=[ShopMediaFiles.BANNERIMAGE, ShopMediaFiles.BANNERVIDEO]
        ),
        many=True,
        required=False,
        write_only=True,
        help_text="List of IDs for banner ShopMediaFiles."
    )
    profile = ShopProfileWriteSerializerForPanel(required=False)

    class Meta:
        model = Shop
        fields = [
            'id',  # Read-only
            'name',  # نام فروشگاه
            'manager_name',  # نام مدیر داخلی
            'manager_mobile',  # موبایل مدیر داخلی
            'description',  # توضیحات
            'profile',  # Nested, editable shop profile (and owner) data.
            'logo',  # Provided as an ID.
            'banner',  # List of IDs.
            'shop_url',  # Url کافه/فروشگاه
            'number_of_tables',  # تعداد میزهای کافه
            'shop_type',  # نوع کافه/فروشگاه
            'monetary_unit',  # واحد قیمت ها
            'free_delivery',  # ارسال رایگان
            'pickup',  # ارسال با فی کافی
            'phone_number',  # تلفن کافه/فروشگاه
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        errors = {}
        logo_obj = attrs.get('logo')
        if logo_obj is not None and logo_obj.media_type != ShopMediaFiles.LOGO:
            errors['logo'] = (f"Provided logo must be of type '{ShopMediaFiles.LOGO}', "
                              f"found '{logo_obj.media_type}'.")
        banner_objs = attrs.get('banner', [])
        if banner_objs:
            allowed_types = [ShopMediaFiles.BANNERIMAGE, ShopMediaFiles.BANNERVIDEO]
            invalid = [obj for obj in banner_objs if obj.media_type not in allowed_types]
            if invalid:
                errors['banner'] = (f"One or more banner files have invalid types. "
                                    f"Allowed types: {allowed_types}. "
                                    f"Invalid IDs: {[obj.id for obj in invalid]}")
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        logo = validated_data.pop('logo', None)
        banner = validated_data.pop('banner', [])
        shop = Shop.objects.create(**validated_data)
        if logo:
            shop.logo = logo
        if banner:
            shop.banner.set(banner)
        shop.save()

        if profile_data:
            # Pass the shop instance to the nested profile serializer via context.
            profile_serializer = ShopProfileWriteSerializerForPanel(
                data=profile_data, context={**self.context, "shop": shop}
            )
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save(shop=shop)
        return shop

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        if 'logo' in validated_data:
            instance.logo = validated_data.pop('logo')
        elif self.initial_data.get('logo') is None:
            instance.logo = None

        if 'banner' in validated_data:
            instance.banner.set(validated_data.pop('banner'))
        elif self.initial_data.get('banner') == []:
            instance.banner.clear()

        instance = super().update(instance, validated_data)

        if profile_data:
            if hasattr(instance, 'profile') and instance.profile is not None:
                profile_serializer = ShopProfileWriteSerializerForPanel(
                    instance=instance.profile,
                    data=profile_data,
                    partial=True,
                    context={**self.context, "shop": instance}
                )
            else:
                profile_serializer = ShopProfileWriteSerializerForPanel(
                    data=profile_data,
                    context={**self.context, "shop": instance}
                )
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save(shop=instance)
        return instance

    def to_representation(self, instance):
        # Delegate the output to the read serializer.
        return ShopPanelReadSerializer(instance, context=self.context).data


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# Open days and hours
# -----------------------------------------------
class NormalizedTimeField(serializers.TimeField):
    def to_internal_value(self, value):
        # If the input is an integer or a digit-only string, convert it.
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
            try:
                number_value = int(value)
                if not 0 <= number_value < 24:
                    raise serializers.ValidationError("ساعت باید بین 0 تا 23 باشد.")
                # Format the value as HH:MM (e.g., 8 becomes "08:00")
                value = f"{number_value:02d}:00"
            except Exception:
                raise serializers.ValidationError(
                    "فرمت ساعت وارد شده نامعتبر است. مقدار معتبر بصورت HH:MM میباشد. مانند: 08:00"
                )
        return super().to_internal_value(value)


class ShopOpenHoursSerializer(serializers.ModelSerializer):
    open_time = NormalizedTimeField()
    close_time = NormalizedTimeField()

    class Meta:
        model = ShopOpenHours
        fields = ['id', 'open_time', 'close_time']
        read_only_fields = ['id']


class ShopOpenDaysSerializer(serializers.ModelSerializer):
    open_hours = ShopOpenHoursSerializer(many=True)

    # Do not allow users to send an id when creating a day – make it read-only.
    class Meta:
        model = ShopOpenDays
        fields = ['id', 'open_day', 'open_hours']
        read_only_fields = ['id']

    def create(self, validated_data):
        open_hours_data = validated_data.pop('open_hours', [])
        shop = self.context.get('shop')
        open_day = validated_data.get('open_day')

        # Check if the day already exists for the shop
        existing_day = ShopOpenDays.objects.filter(shop=shop, open_day=open_day).first()

        if existing_day:
            # If the day exists, update its open hours
            current_hours = {str(hour.id): hour for hour in existing_day.open_hours.all()}
            payload_ids = []
            for hour_data in open_hours_data:
                hour_id = hour_data.get('id', None)
                if hour_id and str(hour_id) in current_hours:
                    hour_instance = current_hours[str(hour_id)]
                    hour_instance.open_time = hour_data.get('open_time', hour_instance.open_time)
                    hour_instance.close_time = hour_data.get('close_time', hour_instance.close_time)
                    hour_instance.save()
                    payload_ids.append(str(hour_id))
                else:
                    new_hour = ShopOpenHours.objects.create(day=existing_day, **hour_data)
                    payload_ids.append(str(new_hour.id))

            # Optionally delete open hours that are not included in the payload
            for existing_id in current_hours.keys():
                if existing_id not in payload_ids:
                    current_hours[existing_id].delete()

            return existing_day

        # If the day does not exist, create a new day
        day_instance = ShopOpenDays.objects.create(shop=shop, **validated_data)
        for hour_data in open_hours_data:
            ShopOpenHours.objects.create(day=day_instance, **hour_data)
        return day_instance

    def update(self, instance, validated_data):
        # Optionally, you could update the open_day field if that's desired,
        # but if you want it to remain untouched, just call:
        instance.save()

        open_hours_data = validated_data.pop('open_hours', None)
        if open_hours_data is not None:
            current_hours = {str(hour.id): hour for hour in instance.open_hours.all()}
            payload_ids = []
            for hour_data in open_hours_data:
                hour_id = hour_data.get('id', None)
                if hour_id and str(hour_id) in current_hours:
                    hour_instance = current_hours[str(hour_id)]
                    hour_instance.open_time = hour_data.get('open_time', hour_instance.open_time)
                    hour_instance.close_time = hour_data.get('close_time', hour_instance.close_time)
                    hour_instance.save()
                    payload_ids.append(str(hour_id))
                else:
                    new_hour = ShopOpenHours.objects.create(day=instance, **hour_data)
                    payload_ids.append(str(new_hour.id))
            # Optionally delete any open hours not included in the payload.
            for existing_id in current_hours.keys():
                if existing_id not in payload_ids:
                    current_hours[existing_id].delete()
        return instance


class ShopWeeklyPlanSerializer(serializers.Serializer):
    open_days = ShopOpenDaysSerializer(many=True)

    def to_representation(self, instance):
        if isinstance(instance, dict):
            days = instance.get("open_days", [])
        elif not isinstance(instance, Iterable):
            days = [instance]
        else:
            days = instance
        return {"open_days": ShopOpenDaysSerializer(days, many=True).data}

    def create(self, validated_data):
        shop = self.context.get('shop')
        open_days_data = validated_data.get('open_days', [])
        updated_days = []

        for day_data in open_days_data:
            # Delegate creation or update of each day to the nested serializer
            day_serializer = ShopOpenDaysSerializer(data=day_data, context={'shop': shop})
            day_serializer.is_valid(raise_exception=True)
            day_instance = day_serializer.save()
            updated_days.append(day_instance)

        return {"open_days": updated_days}

    def update(self, instance, validated_data):
        shop = self.context.get('shop')
        current_days = {str(day.id): day for day in shop.open_days.all()}
        updated_days = []
        open_days_data = validated_data.get("open_days", [])
        for day_data in open_days_data:
            day_id = day_data.get("id", None)
            if day_id and str(day_id) in current_days:
                day_instance = current_days[str(day_id)]
                day_serializer = ShopOpenDaysSerializer(
                    day_instance,
                    data=day_data,
                    partial=True,
                    context={'shop': shop}
                )
                day_serializer.is_valid(raise_exception=True)
                updated_day = day_serializer.save()
                updated_days.append(updated_day)
            # In update mode, we skip creating new days.
        return {"open_days": updated_days}

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# delete rejected shop profile data by admin
# -----------------------------------------------
class ClearProfileAttributeSerializer(serializers.Serializer):
    attribute = serializers.CharField(required=True)

    def validate_attribute(self, value):
        # Define the fields that are allowed to be cleared.
        allowed_attributes = [
            "city", "state", "address", "postal_code", "number",
            "latitude", "longitude", "owner_first_name", "owner_last_name", "owner_id_number"
        ]
        if value not in allowed_attributes:
            raise serializers.ValidationError(f"ویژگی '{value}' قابل حذف نیست.")
        return value

    def map_attribute_to_model(self, attribute):
        """
        Maps the provided attribute to the proper model and field name.
        Owner-related attribute names are mapped to their corresponding User model fields;
        all other names default to the ShopProfile model.
        """
        owner_field_mapping = {
            "owner_first_name": "first_name",
            "owner_last_name": "last_name",
            "owner_id_number": "id_number"
        }
        if attribute in owner_field_mapping:
            return "owner", owner_field_mapping[attribute]
        return "profile", attribute

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# File manager
# -----------------------------------------------
class ShopMediaFilesSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file = serializers.FileField(write_only=True)  # Add this field for file upload input
    is_active = serializers.BooleanField(default=True)  # Add default=True here

    class Meta:
        model = ShopMediaFiles
        fields = ['id', 'media_type','file', 'file_url', 'caption', 'is_active']
        read_only_fields = ['id', 'created_date']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ---------------------------------------------------------------------
# shop dashboard serializers
# # ------------------------------------------------------------------------------
# # Avatar & User Dashboard Serializers
# class AvatarSerializer(serializers.ModelSerializer):
#     file_url = serializers.SerializerMethodField()
#
#     class Meta:
#         model = UserMediaFiles  # Replace with the model representing the avatar file if needed
#         fields = ['id', 'media_type', 'is_active', 'file_url', 'caption']
#         ref_name = 'ShopAvatarSerializer'  # Unique reference name for shop module
#
#     def get_file_url(self, obj):
#         request = self.context.get('request')
#         if obj.file and request:
#             return request.build_absolute_uri(obj.file.url)
#         return None
#
# class UserDashboardSerializer(serializers.ModelSerializer):
#     full_name = serializers.SerializerMethodField()
#     avatar = AvatarSerializer(read_only=True)
#
#     class Meta:
#         model = User
#         fields = ('id', 'mobile', 'first_name', 'last_name', 'avatar', 'full_name')
#
#     def get_full_name(self, obj):
#         return f"{obj.first_name} {obj.last_name}"
#
# # ------------------------------------------------------------------------------
# # Shop Profile Serializer
# class ShopProfileSerializer(serializers.ModelSerializer):
#     owner = UserDashboardSerializer(read_only=True)
#
#     class Meta:
#         model = ShopProfile
#         fields = [
#             'id',
#             'owner',
#             'latitude',
#             'longitude',
#             'postal_code',
#             'number',
#             'address',
#             'city',
#             'state',
#             'country',
#             'is_complete',
#             'is_verified',
#             'created_date',
#             'updated_date'
#         ]
#
# # ------------------------------------------------------------------------------
# # Shop Media Files Dashboard Serializer
# class ShopMediaFilesDashboardSerializer(serializers.ModelSerializer):
#     file_url = serializers.SerializerMethodField()
#     """
#     Serializer for media files such as logo, banners, id cards, and certificates.
#     """
#
#     class Meta:
#         model = ShopMediaFiles
#         fields = ['id', 'media_type', 'file_url', 'is_active', 'caption']
#         read_only_fields = ['id', 'created_date']
#
#     def get_file_url(self, obj):
#         request = self.context.get('request')
#         if obj.file and request:
#             return request.build_absolute_uri(obj.file.url)
#         return None
#
# # ------------------------------------------------------------------------------
# # Shop Open Hours & Days Dashboard Serializers
# class ShopOpenHoursDashboardSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ShopOpenHours
#         fields = ['open_time', 'close_time']
#
#
# class ShopOpenDaysDashboardSerializer(serializers.ModelSerializer):
#     open_hours = ShopOpenHoursDashboardSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = ShopOpenDays
#         fields = ['open_day', 'open_hours']
#
# # ------------------------------------------------------------------------------
# # Shop Dashboard Serializer (Main Read-Only Serializer)
# class ShopDashboardSerializer(serializers.ModelSerializer):
#     profile = ShopProfileSerializer(read_only=True)
#     # Since logo and id_card are now one-to-one, do not use many=True.
#     logo = ShopMediaFilesDashboardSerializer(read_only=True)
#     banner = ShopMediaFilesDashboardSerializer(many=True, read_only=True)
#     id_card = ShopMediaFilesDashboardSerializer(read_only=True)
#     certificate = ShopMediaFilesDashboardSerializer(many=True, read_only=True)
#
#     total_product_count = serializers.SerializerMethodField()
#     verified_product_count = serializers.SerializerMethodField()
#     open_days = ShopOpenDaysDashboardSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = Shop
#         fields = [
#             'id',
#             'profile',
#             'name',
#             'description',
#             'logo',
#             'shop_url',
#             'shop_qr_code',
#             'number_of_tables',
#             'banner',
#             'shop_type',
#             'monetary_unit',
#             'id_card_upload',
#             'certificate_upload',
#             'is_verified',
#             'free_delivery',
#             'pickup',
#             'phone_number',
#             'created_date',
#             'updated_date',
#             'total_product_count',
#             'verified_product_count',
#             'open_days',
#             'certificate',
#             'id_card'
#         ]
#
#     def get_total_product_count(self, obj):
#         """
#         Counts all active (non-deleted) products related to this shop.
#         Assumes the related name 'products' is used on the Product model.
#         """
#         return obj.products.count() if hasattr(obj, 'products') else 0
#
#     def get_verified_product_count(self, obj):
#         """Counts only the products that are verified."""
#         return obj.products.filter(is_verified=True).count() if hasattr(obj, 'products') else 0
#
#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         # Replace the raw monetary_unit (e.g. "h_toman") with its human-readable form.
#         representation['monetary_unit'] = instance.get_monetary_unit_display()
#         return representation

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++





# ----------------------------------------------------------------------
# class ProductImageSerializer(serializers.ModelSerializer):
#     image = serializers.SerializerMethodField()
#
#     class Meta:
#         model = ProductImage
#         fields = ['image']
#
#     def get_image(self, obj):
#         request = self.context.get('request')
#         if obj.image and request:
#             return request.build_absolute_uri(obj.image.url)
#         return None
#
#
# class ProductSerializer(serializers.ModelSerializer):
#     images = ProductImageSerializer(many=True)
#     # product_features = ProductFeatureSerializer(many=True)
#     category_name = serializers.CharField(source='category.title', default="Unknown Category", read_only=True)
#
#     class Meta:
#         model = Product
#         fields = ['id', 'name', 'category_name', 'images', 'is_wholesale', 'is_special']
#         ref_name = 'ShopModuleProductSerializer'
#
#
# class ProductBundleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductBundle
#         fields = ['id', 'name', 'shop', 'is_active']


# --------------------------------------------------------------------------
# class FeatureValueSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FeatureValues
#         fields = ['title']

# class FeatureSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Feature
#         fields = ['title']

# class ProductFeatureSerializer(serializers.ModelSerializer):
#     feature = FeatureSerializer()
#     feature_value = FeatureValueSerializer()
#
#     class Meta:
#         model = ProductFeature
#         fields = ['feature', 'feature_value']

# class ProductCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductCategory
#         fields = ['id', 'title', 'category_type']
