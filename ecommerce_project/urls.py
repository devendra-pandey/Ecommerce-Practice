from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ecommerce_app.urls')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]

# Add media URL patterns after urlpatterns is defined
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
