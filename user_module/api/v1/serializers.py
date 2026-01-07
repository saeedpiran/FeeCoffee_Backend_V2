from rest_framework import serializers

from accounts_module.models import UserMediaFiles
from user_module.models import UserProfile, StoredLocation


class StoredLocationSerializer(serializers.ModelSerializer):
    # owner_id = serializers.CharField(source='user_profile.owner.id')

    class Meta:
        model = StoredLocation
        fields = ['id', 'title', 'lat', 'long', 'state', 'city', 'address']


# ------------------------------------------------------------------------
# class UserProfileSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(source='owner.first_name')
#     last_name = serializers.CharField(source='owner.last_name')
#     mobile = serializers.CharField(source='owner.mobile', read_only=True)
#     id_number = serializers.CharField(source='owner.id_number')
#     avatar = serializers.ImageField(source='owner.avatar')
#     introduction_url = serializers.CharField(source='owner.introduction_url', read_only=True)  # Add this line
#     created_date = serializers.ImageField(source='owner.created_date', read_only=True)
#
#     stored_locations = StoredLocationSerializer(many=True)
#
#     class Meta:
#         model = UserProfile
#         fields = ['id', 'owner', 'first_name', 'last_name', 'mobile',
#                   'id_number', 'avatar', 'created_date', 'introduction_url', 'stored_locations']
#         read_only_fields = ['owner']
#
#     # def validate_stored_locations(self, value):
#     #     """Custom validation for stored_locations"""
#     #     if not isinstance(value, list):
#     #         raise serializers.ValidationError("Stored locations must be a list.")
#     #     for location in value:
#     #         if not all(key in location for key in ('name', 'lat', 'long')):
#     #             raise serializers.ValidationError("Each location must contain 'name', 'lat', and 'long' keys.")
#     #     return value
#
#     def update(self, instance, validated_data):
#         owner_data = validated_data.pop('owner', {})
#         # new_locations = validated_data.pop('stored_locations', [])
#         stored_locations_data = validated_data.pop('stored_locations', [])
#
#         # Update User fields
#         user = instance.owner
#         for attr, value in owner_data.items():
#             setattr(user, attr, value)
#         user.save()
#
#         # # Get existing locations and add new locations
#         # for location in new_locations:
#         #     instance.add_location(location['name'], location['lat'], location['long'])
#
#         # Update stored locations
#         for location_data in stored_locations_data:
#             StoredLocation.objects.create(user_profile=instance, **location_data)
#
#         # Update UserProfile fields
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#
#         return instance
#
#     # def validate(self, attrs):
#     #     # Example of how you might handle validation
#     #     if not attrs.get('first_name'):
#     #         raise serializers.ValidationError({
#     #             "success": False,
#     #             "data": {},
#     #             "message": "نام الزامی است."
#     #         })
#     #     if not attrs.get('last_name'):
#     #         raise serializers.ValidationError({
#     #             "success": False,
#     #             "data": {},
#     #             "message": "نام خانوادگی الزامی است."
#     #         })
#     #     return attrs


# -----------------------------------------------------------------------

class AvatarSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = UserMediaFiles
        fields = ['id', 'media_type', 'is_active', 'file_url', 'caption']
        # Unique reference name for this serializer
        ref_name = 'UserProfileAvatarSerializer'

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class WritableNestedField(serializers.PrimaryKeyRelatedField):
    """
    Acts as a PK-related field for write operations but returns a fully nested
    representation on read. This avoids having to use a separate “avatar_id”
    field.
    """
    def __init__(self, **kwargs):
        self.serializer_class = kwargs.pop("serializer_class")
        super().__init__(**kwargs)

    def to_representation(self, value):
        # If the instance is not fully populated (e.g., just a PK), retrieve the full instance.
        if not hasattr(value, "media_type"):
            value = self.get_queryset().get(pk=value.pk)
        return self.serializer_class(value, context=self.context).data


class UserProfileSerializer(serializers.ModelSerializer):
    # Use WritableNestedField to handle avatar: on GET, full nested data is returned;
    # on update, simply providing the avatar's ID is enough.
    avatar = WritableNestedField(
         serializer_class=AvatarSerializer,
         queryset=UserMediaFiles.objects.filter(media_type=UserMediaFiles.AVATAR),
         required=False,
         allow_null=True,
         source='owner.avatar'
    )
    first_name = serializers.CharField(source="owner.first_name")
    last_name = serializers.CharField(source="owner.last_name")
    mobile = serializers.CharField(source="owner.mobile", read_only=True)
    id_number = serializers.CharField(source="owner.id_number", required=False, allow_blank=True)
    introduction_url = serializers.CharField(source="owner.introduction_url", read_only=True)
    created_date = serializers.DateTimeField(source="owner.created_date", read_only=True)

    class Meta:
         model = UserProfile
         fields = [
             "id", "owner", "first_name", "last_name", "mobile",
             "id_number", "avatar", "created_date", "introduction_url"
         ]
         read_only_fields = ["owner"]

    def update(self, instance, validated_data):
         # Extract owner data (which includes the avatar, thanks to source='owner.avatar')
         owner_data = validated_data.pop("owner", {})
         user = instance.owner

         # Update the avatar field if provided; note that the field value has already been converted
         # by our WritableNestedField into a full model instance.
         if "avatar" in owner_data:
              user.avatar = owner_data["avatar"]

         # Update any additional owner field, if needed.
         for attr, value in owner_data.items():
              setattr(user, attr, value)
         user.save()

         # Update the remaining UserProfile fields.
         for attr, value in validated_data.items():
              setattr(instance, attr, value)
         instance.save()
         return instance
# ---------------------------------------------------------------------------
# # user avatar manager
# class UserAvatarManageSerializer(serializers.ModelSerializer):
#     file_url = serializers.SerializerMethodField(read_only=True)
#
#     class Meta:
#         model = UserMediaFiles
#         fields = ['id', 'media_type', 'file_url', 'is_active', 'caption']
#         read_only_fields = ['id', 'media_type', 'file_url']
#
#     def get_file_url(self, obj):
#         request = self.context.get('request')
#         if obj.file and request:
#             return request.build_absolute_uri(obj.file.url)
#         return None
#
#     def create(self, validated_data):
#         # Force the media_type to be avatar.
#         validated_data['media_type'] = UserMediaFiles.AVATAR
#         # Automatically assign the current user to this avatar.
#         user = self.context.get('request').user
#         validated_data['user'] = user
#         return super().create(validated_data)
