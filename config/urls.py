from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('pages/', include('apps.pages.urls')),
    path('', include('apps.shop.urls', namespace="shop")),
    path('store/', include('apps.store.urls', namespace="store")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
] + urlpatterns 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
