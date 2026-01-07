# # views.py
# from drf_yasg.utils import swagger_auto_schema
# from rest_framework import generics
# from rest_framework import viewsets
# from rest_framework.parsers import MultiPartParser, FormParser
#
# from media_collection_module.models import ImageCollectionCategory, ImageCollectionImage
# from .permissions import IsAdminOrSuperuserOrReadOnly
# from .serializers import ImageCollectionCategorySerializer
# from .serializers import ImageCollectionImageSerializer
#
#
# # -------------------------------------------------------------------
# # Collection images and categories
# class ImageCollectionCategoryViewSet(viewsets.ModelViewSet):
#     """
#     A viewset that provides the standard actions for ImageCollectionCategory.
#     """
#     queryset = ImageCollectionCategory.objects.all()
#     serializer_class = ImageCollectionCategorySerializer
#     permission_classes = [IsAdminOrSuperuserOrReadOnly]
#     # Optional: add filtering or search capabilities if needed
#     filter_fields = ['is_active']
#     search_fields = ['title']
#
#
# class ImageCollectionImageViewSet(viewsets.ModelViewSet):
#     """
#     A viewset that provides the standard actions for ImageCollectionImage.
#     """
#     queryset = ImageCollectionImage.objects.all()
#     serializer_class = ImageCollectionImageSerializer
#     permission_classes = [IsAdminOrSuperuserOrReadOnly]
#     parser_classes = [MultiPartParser, FormParser]  # Enables file upload
#     # Optional filters: for quick filtering of active images or by category.
#     filter_fields = ['is_active', 'category']
#     search_fields = ['title']
#
#     @swagger_auto_schema(request_body=ImageCollectionImageSerializer)
#     def create(self, request, *args, **kwargs):
#         return super().create(request, *args, **kwargs)
#
#
# # --------------------------------------------------------------------------------
# # list of images by category
# # views.py
# class ImagesByCategoryListView(generics.ListAPIView):
#     serializer_class = ImageCollectionImageSerializer
#
#     def get_queryset(self):
#         # Get the category_id from the URL route parameter.
#         category_id = self.kwargs.get('category_id')
#         queryset = ImageCollectionImage.objects.filter(is_active=True)
#         if category_id:
#             queryset = queryset.filter(category__id=category_id)
#         return queryset
