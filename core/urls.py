from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('accounts.urls')),
    path('establishments/', include('establishments.urls')),
    path('', include('menu.urls')),
    path('orders/', include('orders.urls')),
    path('support/', include('support.urls')),
    path('subscriptions/', include('subscriptions.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path('schema', SpectacularAPIView.as_view(), name='schema'),
        # Optional UI:
        path('docs', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('redoc', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
