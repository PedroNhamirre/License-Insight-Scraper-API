from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Defina as URLs primeiro
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('swagger/', get_schema_view(
        openapi.Info(
            title="License Insight API",
            default_version='v1',
            description="API documentation for the License Insight project",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="contact@licenseinsight.local"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    ).with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', get_schema_view(
        openapi.Info(
            title="License Insight API",
            default_version='v1',
            description="API documentation for the License Insight project",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="contact@licenseinsight.local"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    ).with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
