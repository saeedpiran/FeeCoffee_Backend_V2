from persiantools.jdatetime import JalaliDate
from rest_framework import serializers

from accounts_module.models import User
from article_module.models import Article, ArticleCategory, ArticleTag, ArticleKeyWords, ArticleMediaFiles


# from .models import (
#     Article,
#     ArticleMediaFiles,
#     ArticleTag,
#     ArticleKeyWords,
#     ArticleCategory,
# )
# ----------------------------------------------------------------

class ArticleKeyWordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleKeyWords
        fields = ['title']


class ArticleTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleTag
        fields = ['id', 'title', 'url_title', 'is_active']


class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = ['id', 'parent', 'title', 'url_title', 'is_active']

    def validate(self, attrs):
        if not attrs.get('id'):
            raise serializers.ValidationError({
                "success": False,
                "error": "مقدار آی دی الزامیست."
            })
        return attrs


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # or use your custom user model if necessary
        fields = ['id', 'first_name', 'last_name']


class ArticleMediaFilesSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField(read_only=True)
    file = serializers.FileField(write_only=True)


    class Meta:
        model = ArticleMediaFiles
        fields = [
            'id',
            'user',          # Read-only; set automatically in the view.
            'media_type',
            'file',
            'caption',
            'is_active',
            'file_url',
        ]
        extra_kwargs = {
            'user': {'read_only': True},
        }

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

class WritableNestedField(serializers.PrimaryKeyRelatedField):
    """
    A field that writes using primary keys but on read returns a nested
    representation via a provided serializer_class.
    """

    def __init__(self, **kwargs):
        self.serializer_class = kwargs.pop("serializer_class")
        super().__init__(**kwargs)

    def to_representation(self, value):
        # If the returned object is a partial (PK-only) object,
        # reload the complete model instance from the queryset.
        if not hasattr(value, "media_type"):
            value = self.get_queryset().get(pk=value.pk)
        return self.serializer_class(value, context=self.context).data


class ArticleSerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField(method_name='get_abs_url')
    author = AuthorSerializer(read_only=True)
    created_date = serializers.SerializerMethodField(method_name='get_created_date')
    created_month = serializers.SerializerMethodField(method_name='get_created_month')
    created_day = serializers.SerializerMethodField(method_name='get_created_day')
    # Use the custom field so that on write you only pass an ID,
    # but on read a fully nested representation is returned.
    image = WritableNestedField(
        serializer_class=ArticleMediaFilesSerializer,
        queryset=ArticleMediaFiles.objects.filter(media_type=ArticleMediaFiles.ARTICLE),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'key_words',
            'image',  # Now writable via a file ID on POST/PATCH
            'author',
            'slug',
            'short_description',
            'text',
            'absolute_url',
            'is_active',
            'selected_categories',
            'tags',
            'created_date',
            'created_month',
            'created_day'
        ]

    def get_abs_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.id)

    def get_created_date(self, obj):
        jalali_date = JalaliDate.to_jalali(obj.created_date)
        return jalali_date.strftime('%Y/%m/%d')

    def get_created_month(self, obj):
        jalali_date = JalaliDate.to_jalali(obj.created_date)
        return jalali_date.strftime('%B', locale='fa')

    def get_created_day(self, obj):
        jalali_date = JalaliDate.to_jalali(obj.created_date)
        return jalali_date.day

    def to_representation(self, instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        # For detail view, remove absolute URL; for list view, remove text.
        if request.parser_context.get('kwargs', {}).get('pk'):
            rep.pop('absolute_url', None)
        else:
            rep.pop('text', None)
        # Return only titles for many-to-many related fields.
        rep['key_words'] = [kw['title'] for kw in ArticleKeyWordsSerializer(instance.key_words.all(), many=True).data]
        rep['selected_categories'] = [cat['title'] for cat in
                                      ArticleCategorySerializer(instance.selected_categories.all(), many=True).data]
        rep['tags'] = [tag['title'] for tag in ArticleTagSerializer(instance.tags.all(), many=True).data]
        return rep

    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError({
                "success": False,
                "error": "Request context is missing."
            })

        user = request.user
        if not user.is_authenticated:
            raise serializers.ValidationError({
                "success": False,
                "error": "کاربر مجاز نیست."
            })

        # Assign the user as the author.
        validated_data['author'] = user

        # Pop "image" (if provided) so that it's not processed as a nested object.
        image = validated_data.pop('image', None)
        article = super().create(validated_data)
        if image is not None:
            article.image = image
            article.save()
        return article

    def update(self, instance, validated_data):
        # For update, process the image field similarly.
        image = validated_data.pop('image', None)
        instance = super().update(instance, validated_data)
        if image is not None:
            instance.image = image
            instance.save()
        return instance

# -----------------------------------------------------------------
# Media file manager
# class ArticleMediaFilesSerializer(serializers.ModelSerializer):
#     file_url = serializers.SerializerMethodField()
#
#     class Meta:
#         model = ArticleMediaFiles
#         fields = ['id', 'file_url', 'media_type', 'caption', 'created_date']
#
#     def get_file_url(self, obj):
#         request = self.context.get("request", None)
#         if obj.file:
#             if request:
#                 # Build an absolute URL (e.g. https://your-domain.com/medias/...)
#                 return request.build_absolute_uri(obj.file.url)
#             return obj.file.url
#         return None


# # class ArticleSerializer(serializers.Serializer):
# #     id = serializers.IntegerField()
# #     title = serializers.CharField(max_length=300)
# #
# #
#
# class ArticleKeyWordsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ArticleKeyWords
#         fields = ['title']
#
#
# class ArticleTagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ArticleTag
#         fields = ['id', 'title','url_title','is_active']
#
#
# class ArticleCategorySerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = ArticleCategory
#         fields = ['id','parent', 'title','url_title','is_active']
#
#     def validate(self, attrs):
#         # Example of how you might handle validation
#         if not attrs.get('id'):
#             raise serializers.ValidationError({
#                 "success": False,
#                 "error": "مقدار آی دی الزامیست."
#             })
#         return attrs
#
#
# class AuthorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User  # Use the correct model for your author (User or Author)
#         fields = ['id', 'first_name', 'last_name']  # Include any other fields you need
#
#
#
#
# class ArticleSerializer(serializers.ModelSerializer):
#     absolute_url = serializers.SerializerMethodField(method_name='get_abs_url')
#     author = AuthorSerializer(read_only=True)  # Add the author field
#     created_date = serializers.SerializerMethodField(method_name='get_created_date')
#     created_month = serializers.SerializerMethodField(method_name='get_created_month')
#     created_day = serializers.SerializerMethodField(method_name='get_created_day')
#
#     class Meta:
#         model = Article
#         fields = ['id', 'title', 'key_words', 'image', 'author', 'slug', 'short_description',
#                   'text', 'absolute_url', 'is_active', 'selected_categories',
#                   'tags', 'created_date', 'created_month','created_day']
#
#     def get_abs_url(self, obj):
#         request = self.context.get('request')
#         return request.build_absolute_uri(obj.id)
#
#     def get_created_date(self, obj):
#         jalali_date = JalaliDate.to_jalali(obj.created_date)
#         return jalali_date.strftime('%Y/%m/%d')
#
#     def get_created_month(self, obj):
#         jalali_date = JalaliDate.to_jalali(obj.created_date)
#         return jalali_date.strftime('%B', locale='fa')
#
#     def get_created_day(self, obj):
#         jalali_date = JalaliDate.to_jalali(obj.created_date)
#         return jalali_date.day  # Return only the day number
#
#     def to_representation(self, instance):
#         request = self.context.get('request')
#         rep = super().to_representation(instance)
#         if request.parser_context.get('kwargs').get('pk'):
#             rep.pop('absolute_url', None)
#         else:
#             rep.pop('text', None)
#
#         rep['key_words'] = [kw['title'] for kw in ArticleKeyWordsSerializer(instance.key_words.all(), many=True).data]
#         rep['selected_categories'] = [kw['title'] for kw in ArticleCategorySerializer(instance.selected_categories.all(), many=True).data]
#         rep['tags'] = [kw['title'] for kw in ArticleTagSerializer(instance.tags.all(), many=True).data]
#         return rep
#
#     def create(self, validated_data):
#         request = self.context.get('request')
#         if not request:
#             raise ValidationError({
#                 "success": False,
#                 "error": "Request context is missing."
#             })
#
#         user = request.user
#         if not user.is_authenticated:
#             raise ValidationError({
#                 "success": False,
#                 "error": "کاربر مجاز نیست."
#             })
#
#         validated_data['author'] = user  # Assign the User instance directly
#         return super().create(validated_data)


# class ArticleSerializer(serializers.ModelSerializer):
#     absolute_url = serializers.SerializerMethodField(method_name='get_abs_url')
#     author = AuthorSerializer(read_only=True)  # Add the author field
#
#     class Meta:
#         model = Article
#         fields = ['id','title','key_words','image','author','slug','short_description',
#                   'text','absolute_url','is_active','selected_categories',
#                   'tags','created_date']
#
#     def get_abs_url(self,obj):
#         request = self.context.get('request')
#         return request.build_absolute_uri(obj.id)
#
#     def to_representation(self, instance):
#         request = self.context.get('request')
#         rep = super().to_representation(instance)
#         if request.parser_context.get('kwargs').get('pk'):
#             rep.pop('absolute_url', None)
#         else:
#             rep.pop('text',None)
#
#         rep['key_words'] = [kw['title'] for kw in ArticleKeyWordsSerializer(instance.key_words.all(), many=True).data]
#         rep['selected_categories'] = [kw['title'] for kw in ArticleCategorySerializer(instance.selected_categories.all(), many=True).data]
#         rep['tags'] = [kw['title'] for kw in ArticleTagSerializer(instance.tags.all(), many=True).data]
#         # rep['key_words'] = ArticleKeyWordsSerializer(instance.key_words.all(), many=True).data
#         # rep['selected_categories'] = ArticleCategorySerializer(instance.selected_categories, many=True).data
#         # rep['tags'] = ArticleTagSerializer(instance.tags.all(), many=True).data
#
#         return rep
#
#     def create(self, validated_data):
#         request = self.context.get('request')
#         if not request:
#             raise ValidationError({
#                 "success": False,
#                 "error": "Request context is missing."
#             })
#
#         user = request.user
#         if not user.is_authenticated:
#             raise ValidationError({
#                 "success": False,
#                 "error": "کاربر مجاز نیست."
#             })
#
#         validated_data['author'] = user  # Assign the User instance directly
#         return super().create(validated_data)
