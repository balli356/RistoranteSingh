from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('accounts/', include('allauth.urls')),

    path('', include('core.urls', namespace='core')),
    path('utente/', include('utente.urls')),
    path('password/reset', auth_views.PasswordResetView.as_view(template_name='user/reset_password.html'),
         name='reset_password'),

    path('password/reset_sent', auth_views.PasswordResetDoneView.as_view(template_name='user/reset_password_sent.html'),
         name='password_reset_done'),
    path('password/reset_confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='user/reset_password_form.html'),
         name='password_reset_confirm'),
    path('password/reset_complete',
         auth_views.PasswordResetCompleteView.as_view(template_name='user/reset_password_complete.html'),
         name='password_reset_complete'),

    re_path(r'^$', RedirectView.as_view(url='django-ristorante-singh', permanent=False), name='index')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]