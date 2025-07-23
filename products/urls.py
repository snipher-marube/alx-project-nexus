from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'brands', views.BrandViewSet, basename='brand')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'product-images', views.ProductImageViewSet, basename='product-image')
router.register(r'product-variants', views.ProductVariantViewSet, basename='product-variant')
router.register(r'product-attributes', views.ProductAttributeViewSet, basename='product-attribute')
router.register(r'product-attribute-values', views.ProductAttributeValueViewSet, basename='product-attribute-value')
router.register(r'product-variant-attributes', views.ProductVariantAttributeViewSet, basename='product-variant-attribute')
router.register(r'product-reviews', views.ProductReviewViewSet, basename='product-review')
router.register(r'product-specifications', views.ProductSpecificationViewSet, basename='product-specification')


urlpatterns = [
    path('', include(router.urls)),
    path('products/<slug:slug>/reviews/', 
         views.ProductViewSet.as_view({'get': 'reviews'}), 
         name='product-reviews'),
    path('products/<slug:slug>/add-review/', 
         views.ProductViewSet.as_view({'post': 'add_review'}), 
         name='add-review'),
    path('products/<slug:slug>/add-image/', 
         views.ProductViewSet.as_view({'post': 'add_image'}), 
         name='add-image'),
]