from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title='DRINKJOY API',
        default_version='v1',
        description='API DRINKJOY предоставляет доступ к различным запросам, требующим аутентификации '
        'с помощью токена Bearer. '
        "Для аутентификации включите 'Bearer {access_token}' в заголовок 'Authorization'.",
        terms_of_service='https://www.yourcompany.com/terms/',
        contact=openapi.Contact(email='contact@yourcompany.local'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts'), name='accounts'),
]

if settings.DEBUG:
    urlpatterns += [
        path('docs<format>', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]
