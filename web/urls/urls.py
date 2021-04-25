from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.common.views import ClassifyFormView


admin.site.site_header = 'Classifier'
admin.site.index_title = 'Site administration'
admin.site.site_title = 'Classifier Admin'

urlpatterns = [
    path("", ClassifyFormView.as_view()),
    path("admin/", admin.site.urls),
    path('health-check/', include('health_check.urls')),
]

if settings.ENVIRONMENT == 'local':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
