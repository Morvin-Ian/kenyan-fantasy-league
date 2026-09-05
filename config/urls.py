from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("guardian/", admin.site.urls),
    path("api/v1/auth/", include("djoser.urls")),
    path("api/v1/auth/", include("djoser.urls.jwt")),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/profile/", include("apps.profiles.urls")),
    path("api/v1/kpl/", include("apps.kpl.urls")),
    path("api/v1/fantasy/", include("apps.fantasy.urls")),
]

# Team badges live under MEDIA_ROOT and are referenced by the API as
# /mediafiles/... . nginx serves that path in both the local and production
# stacks, but the Vite dev server proxies straight to Django, so without this
# every badge 404s when developing against :3000. DEBUG-only: in production
# nginx serves the files and Django must never be in that path.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Fantasy Kenyan League"
admin.site.site_title = "Fantasy League Admin Portal"
admin.site.index_title = "Welcome to The Realm"
