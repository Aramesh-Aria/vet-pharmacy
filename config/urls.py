"""Root URL configuration."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.pages.sitemaps import SITEMAPS
from apps.pages.views import healthz, robots_txt

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("animals/", include("apps.animals.urls")),
    path("shop/", include("apps.pharmacy.urls")),
    path("clinic/", include("apps.appointments.urls")),
    path("payments/", include("apps.payments.urls")),
    path("c/", include("apps.catalog.urls")),
    # SEO + ops
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots"),
    path("healthz", healthz, name="healthz"),
    path("", include("apps.pages.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
