
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from django.contrib import admin
from django.urls import path, include

from elonuz import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('root.url')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)