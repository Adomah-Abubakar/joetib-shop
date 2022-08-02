from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("unicorn/", include("django_unicorn.urls")),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('pages/', include('pages.urls')),
    path('store/', include('store.urls', namespace="store")),
    path('messaging/', include('messaging.urls', namespace="messaging")),
    path('', include('shop.urls', namespace="shop")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
] + urlpatterns 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
