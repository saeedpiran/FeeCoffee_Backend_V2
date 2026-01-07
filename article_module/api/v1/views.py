from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from article_module.models import Article, ArticleCategory, ArticleMediaFiles
from .paginations import DefaultPagination
from .permissions import IsArticleOwnerOrAdmin
from .serializers import ArticleMediaFilesSerializer
from .serializers import ArticleSerializer, ArticleCategorySerializer


# ==========================================================================
# @api_view(["GET","POST"])
# @permission_classes([IsAuthenticatedOrReadOnly])
# def article_list_view(request):
#     if request.method == "GET":
#         articles = Article.objects.filter(is_active=True)
#         serializer = ArticleSerializer(articles, many=True)
#         return Response(serializer.data)
#     elif request.method == "POST":
#         serializer = ArticleSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)


# class ArticleList(APIView):
#     """
#     getting a list of articles and creating an article
#     """
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     serializer_class = ArticleSerializer
#
#     def get(self,request):
#         """retrieving a list of articles"""
#         articles = Article.objects.filter(is_active=True)
#         serializer = ArticleSerializer(articles, many=True)
#         return Response(serializer.data)
#
#     def post(self,request):
#         """creating an article with provided data"""
#         serializer = ArticleSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)


# class ArticleList(ListCreateAPIView):
#     """getting a list of articles and creating an article"""
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     serializer_class = ArticleSerializer
#     queryset = Article.objects.filter(is_active=True)

# ============================================================================
# @api_view(["GET","PUT","DELETE"])
# @permission_classes([IsAuthenticatedOrReadOnly])
# def article_detail_view(request, id):
#     article = get_object_or_404(Article, id=id, is_active=True)
#     if request.method == "GET":
#         serializer = ArticleSerializer(article)
#         return Response(serializer.data)
#     elif request.method == "PUT":
#         serializer = ArticleSerializer(article, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == "DELETE":
#         article.delete()
#         return Response({"detail":"item removed successfully"},status=status.HTTP_204_NO_CONTENT)


# class ArticleDetail(APIView):
#     """getting detail of the article and edit plus removing it"""
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     serializer_class = ArticleSerializer
#
#     def get(self,request,id):
#         """retriving the article data"""
#         article = get_object_or_404(Article, id=id, is_active=True)
#         serializer = self.serializer_class(article)
#         return Response(serializer.data)
#
#     def put(self,request,id):
#         """editing the article data"""
#         article = get_object_or_404(Article, id=id, is_active=True)
#         serializer = self.serializer_class(article, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#
#     def delete(self,request,id):
#         """delete the article by its id"""
#         article = get_object_or_404(Article, id=id, is_active=True)
#         article.delete()
#         return Response({"detail":"item removed successfully"},status=status.HTTP_204_NO_CONTENT)


# class ArticleDetail(RetrieveUpdateDestroyAPIView):
#     """getting detail of the article and edit plus removing it"""
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     serializer_class = ArticleSerializer
#     queryset = Article.objects.filter(is_active=True)
#     lookup_field = 'id'


# class ArticleViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     serializer_class = ArticleSerializer
#     queryset = Article.objects.filter(is_active=True)
#     lookup_field = 'id'
#
#     def list(self,request):
#         serializer = self.serializer_class(self.queryset,many=True)
#         return Response(serializer.data)
#
#     def retrieve(self,request,id=None):
#         article_object = get_object_or_404(self.queryset,id=id)
#         serializer = self.serializer_class(article_object)
#         return Response(serializer.data)
#
#     def create(self,request):
#         pass
#
#     def update(self,request,id=id):
#         pass
#
#     def partial_update(self,request,id=id):
#         pass
#
#     def destroy(self,request,id=id):
#         pass
# =================================================================


class ArticleModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ArticleSerializer
    queryset = Article.objects.filter(is_active=True).order_by('created_date')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['selected_categories', 'author']
    search_fields = ['title', 'text']
    ordering_fields = ['created_date']
    pagination_class = DefaultPagination


class ArticleCategoryModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ArticleCategorySerializer
    queryset = ArticleCategory.objects.all()


# ---------------------------------------------------------------------
# Media file manager
class ArticleMediaFilesViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing ArticleMediaFiles.
    Files are independently uploaded and bound to the uploader.
    - Only the file owner (or an admin) may update the file.
    - Only admin or staff users are allowed to delete a file.
    """
    serializer_class = ArticleMediaFilesSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = DefaultPagination  # Use your custom pagination here
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['media_type', 'is_active']  # Adjust as necessary
    search_fields = ['caption', 'file']  # Include fields for meaningful text-based searching

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('search',
                              openapi.IN_QUERY,
                              description="Search query for caption and file",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('media_type',
                              openapi.IN_QUERY,
                              description="Filter by media type",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('is_active',
                              openapi.IN_QUERY,
                              description="Filter by active status",
                              type=openapi.TYPE_BOOLEAN)
        ]
    )
    def list(self, request, *args, **kwargs):
        # Call the parent's list method to generate the response.
        response = super().list(request, *args, **kwargs)
        # Attach a custom message that the renderer will pick up.
        response.message = "تصاویر مقالات با موفقیت فراخوانی شد."
        return response

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ArticleMediaFiles.objects.none()
        user = self.request.user
        if user.is_superuser or user.is_staff:
            queryset = ArticleMediaFiles.objects.all()
        else:
            queryset = ArticleMediaFiles.objects.filter(user=user)
        # Guarantee consistent ordering for proper pagination.
        return queryset.order_by('id')

    def get_permissions(self):
        if self.action == 'destroy':
            # Only admin/staff can delete the file.
            permission_classes = [permissions.IsAdminUser]
        else:
            # Other actions (GET, POST, PUT, PATCH) require that the file belongs to the request user (or that the user is admin).
            permission_classes = [IsArticleOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Automatically sets the file's user to the authenticated user uploading the file.
        serializer.save(user=self.request.user)

# ------------------------------------------------------------------
# class ArticleModelViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     serializer_class = ArticleSerializer
#     queryset = Article.objects.filter(is_active=True).order_by('created_date')  # Ensure queryset is ordered
#     # queryset = Article.objects.filter(is_active=True)
#     filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
#     filterset_fields = ['selected_categories', 'author']
#     search_fields = ['title', 'text']
#     ordering_fields = ['created_date']
#     pagination_class = DefaultPagination
#
#
#
#
# class ArticleCategoryModelViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     serializer_class = ArticleCategorySerializer
#     queryset = ArticleCategory.objects.all()
