# # serializers.py
#
# from rest_framework import serializers
#
# from media_collection_module.models import ImageCollectionCategory, ImageCollectionImage
#
#
# class ImageCollectionCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ImageCollectionCategory
#         fields = ['id', 'title', 'is_active']
#
#
# class CategoryPKField(serializers.PrimaryKeyRelatedField):
#     def get_choices(self, cutoff=None):
#         """
#         Return a dict of valid choices for the field where key is the primary key
#         and value is the string representation. This enumeration is used by Swagger
#         to display a dropdown.
#         """
#         queryset = self.get_queryset() or []
#         return {item.pk: str(item) for item in queryset}
#
#
# class ImageCollectionImageSerializer(serializers.ModelSerializer):
#     # Represent 'category' as a primary key. Alternatively, you can nest the CategorySerializer.
#     category = serializers.PrimaryKeyRelatedField(queryset=ImageCollectionCategory.objects.all())
#     # Add an image URL field to simplify accessing the image's URL.
#     file_url = serializers.SerializerMethodField()
#
#     class Meta:
#         model = ImageCollectionImage
#         fields = ['id', 'title', 'image', 'file_url', 'category', 'is_active']
#
#     def get_file_url(self, obj):
#         request = self.context.get('request')
#         if obj.image:
#             if request:
#                 return request.build_absolute_uri(obj.image.url)
#             return obj.image.url
#         return None
#
# # from rest_framework import serializers
# # from rest_framework.exceptions import ValidationError
# #
# # from accounts_module.models import User
# # from article_module.models import Article, ArticleCategory, ArticleTag, ArticleKeyWords
# # from user_module.models import UserProfile
# # from rest_framework import serializers
# # from persiantools.jdatetime import JalaliDate
# #
# #
# # # class ArticleSerializer(serializers.Serializer):
# # #     id = serializers.IntegerField()
# # #     title = serializers.CharField(max_length=300)
# # #
# # #
# #
# # class ArticleKeyWordsSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = ArticleKeyWords
# #         fields = ['title']
# #
# #
# # class ArticleTagSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = ArticleTag
# #         fields = ['id', 'title','url_title','is_active']
# #
# #
# # class ArticleCategorySerializer(serializers.ModelSerializer):
# #
# #     class Meta:
# #         model = ArticleCategory
# #         fields = ['id','parent', 'title','url_title','is_active']
# #
# #     def validate(self, attrs):
# #         # Example of how you might handle validation
# #         if not attrs.get('id'):
# #             raise serializers.ValidationError({
# #                 "success": False,
# #                 "error": "مقدار آی دی الزامیست."
# #             })
# #         return attrs
# #
# #
# # class AuthorSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = User  # Use the correct model for your author (User or Author)
# #         fields = ['id', 'first_name', 'last_name']  # Include any other fields you need
# #
# #
# #
# #
# # class ArticleSerializer(serializers.ModelSerializer):
# #     absolute_url = serializers.SerializerMethodField(method_name='get_abs_url')
# #     author = AuthorSerializer(read_only=True)  # Add the author field
# #     created_date = serializers.SerializerMethodField(method_name='get_created_date')
# #     created_month = serializers.SerializerMethodField(method_name='get_created_month')
# #     created_day = serializers.SerializerMethodField(method_name='get_created_day')
# #
# #     class Meta:
# #         model = Article
# #         fields = ['id', 'title', 'key_words', 'image', 'author', 'slug', 'short_description',
# #                   'text', 'absolute_url', 'is_active', 'selected_categories',
# #                   'tags', 'created_date', 'created_month','created_day']
# #
# #     def get_abs_url(self, obj):
# #         request = self.context.get('request')
# #         return request.build_absolute_uri(obj.id)
# #
# #     def get_created_date(self, obj):
# #         jalali_date = JalaliDate.to_jalali(obj.created_date)
# #         return jalali_date.strftime('%Y/%m/%d')
# #
# #     def get_created_month(self, obj):
# #         jalali_date = JalaliDate.to_jalali(obj.created_date)
# #         return jalali_date.strftime('%B', locale='fa')
# #
# #     def get_created_day(self, obj):
# #         jalali_date = JalaliDate.to_jalali(obj.created_date)
# #         return jalali_date.day  # Return only the day number
# #
# #     def to_representation(self, instance):
# #         request = self.context.get('request')
# #         rep = super().to_representation(instance)
# #         if request.parser_context.get('kwargs').get('pk'):
# #             rep.pop('absolute_url', None)
# #         else:
# #             rep.pop('text', None)
# #
# #         rep['key_words'] = [kw['title'] for kw in ArticleKeyWordsSerializer(instance.key_words.all(), many=True).data]
# #         rep['selected_categories'] = [kw['title'] for kw in ArticleCategorySerializer(instance.selected_categories.all(), many=True).data]
# #         rep['tags'] = [kw['title'] for kw in ArticleTagSerializer(instance.tags.all(), many=True).data]
# #         return rep
# #
# #     def create(self, validated_data):
# #         request = self.context.get('request')
# #         if not request:
# #             raise ValidationError({
# #                 "success": False,
# #                 "error": "Request context is missing."
# #             })
# #
# #         user = request.user
# #         if not user.is_authenticated:
# #             raise ValidationError({
# #                 "success": False,
# #                 "error": "کاربر مجاز نیست."
# #             })
# #
# #         validated_data['author'] = user  # Assign the User instance directly
# #         return super().create(validated_data)
# #
# #
# #
# # # class ArticleSerializer(serializers.ModelSerializer):
# # #     absolute_url = serializers.SerializerMethodField(method_name='get_abs_url')
# # #     author = AuthorSerializer(read_only=True)  # Add the author field
# # #
# # #     class Meta:
# # #         model = Article
# # #         fields = ['id','title','key_words','image','author','slug','short_description',
# # #                   'text','absolute_url','is_active','selected_categories',
# # #                   'tags','created_date']
# # #
# # #     def get_abs_url(self,obj):
# # #         request = self.context.get('request')
# # #         return request.build_absolute_uri(obj.id)
# # #
# # #     def to_representation(self, instance):
# # #         request = self.context.get('request')
# # #         rep = super().to_representation(instance)
# # #         if request.parser_context.get('kwargs').get('pk'):
# # #             rep.pop('absolute_url', None)
# # #         else:
# # #             rep.pop('text',None)
# # #
# # #         rep['key_words'] = [kw['title'] for kw in ArticleKeyWordsSerializer(instance.key_words.all(), many=True).data]
# # #         rep['selected_categories'] = [kw['title'] for kw in ArticleCategorySerializer(instance.selected_categories.all(), many=True).data]
# # #         rep['tags'] = [kw['title'] for kw in ArticleTagSerializer(instance.tags.all(), many=True).data]
# # #         # rep['key_words'] = ArticleKeyWordsSerializer(instance.key_words.all(), many=True).data
# # #         # rep['selected_categories'] = ArticleCategorySerializer(instance.selected_categories, many=True).data
# # #         # rep['tags'] = ArticleTagSerializer(instance.tags.all(), many=True).data
# # #
# # #         return rep
# # #
# # #     def create(self, validated_data):
# # #         request = self.context.get('request')
# # #         if not request:
# # #             raise ValidationError({
# # #                 "success": False,
# # #                 "error": "Request context is missing."
# # #             })
# # #
# # #         user = request.user
# # #         if not user.is_authenticated:
# # #             raise ValidationError({
# # #                 "success": False,
# # #                 "error": "کاربر مجاز نیست."
# # #             })
# # #
# # #         validated_data['author'] = user  # Assign the User instance directly
# # #         return super().create(validated_data)
# #
# #
# #
