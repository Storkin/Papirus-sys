from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import set_language

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
    path('', include('inventory.urls')),
    path('', include('django.contrib.auth.urls')),
]