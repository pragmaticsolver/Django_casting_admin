"""CastingSecret URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_vie  w(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import re_path, path
from django.views.static import serve
from rest_auth.registration.views import SocialAccountListView, SocialAccountDisconnectView, VerifyEmailView
from rest_auth.views import PasswordResetConfirmView,PasswordResetView
from rest_framework_jwt.views import verify_jwt_token, refresh_jwt_token, obtain_jwt_token

from casting_secret.Jobs.urls import job_url_patterns
from casting_secret.api.common_api import VerifyUsernameEmail, ListTalentCategories, NotificationAPI, EmailHandlerAPI, SubscriptionAPI
from casting_secret.company.urls import company_url
from casting_secret.search_indexes import urls as search_index_urls
from casting_secret.user_profile.urls import profile_url_pattern
from casting_secret.views import schema_view, FacebookLogin, TwitterLogin, FacebookConnect, TwitterConnect
from casting_secret.wall.urls import wall_url_patterns


urlpatterns = [
    url(r'^$', schema_view),
    url('^admin/', admin.site.urls),
    url(r'^auth/', include('rest_auth.urls')),
    url(r'^auth/registration/', include('rest_auth.registration.urls')),
    re_path(r'^auth/registration/account-confirm-email/', VerifyEmailView.as_view(),
            name='account_email_verification_sent'),
    url(r'^password/reset/$', PasswordResetView.as_view(),
        name='rest_password_reset'),
    re_path(
        r'^rest-auth/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # re_path(r'^auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$', VerifyEmailView.as_view(), name='account_confirm_email'),
    url(r'^auth/facebook/$', FacebookLogin.as_view(), name='fb_login'),
    url(r'^auth/twitter/$', TwitterLogin.as_view(), name='twitter_login'),
    url(r'^auth/facebook/connect/$', FacebookConnect.as_view(), name='fb_connect'),
    url(r'^auth/twitter/connect/$', TwitterConnect.as_view(), name='twitter_connect'),
    url(r'^social-accounts/$', SocialAccountListView.as_view(), name='social_account_list'),
    url(r'^social-accounts/(?P<pk>\d+)/disconnect/$', SocialAccountDisconnectView.as_view(),
        name='social_account_disconnect'),
    url(r'^api-token-verify/', verify_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^api-token-auth/', obtain_jwt_token),

    path('email/<email>/change', EmailHandlerAPI.as_view({'post': 'change_email'}), name='change_email'),
    path('email/<email>/primary', EmailHandlerAPI.as_view({'post': 'make_email_primary'}), name='make_email_primary'),
    path('email/<email>/verify', EmailHandlerAPI.as_view({'post': 'send_confirmation'}), name='send_confirmation'),
    path('email/new', EmailHandlerAPI.as_view({'post': 'add_email'}), name='add_email'),

    # serve media
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }, name='media'),
    url(r'^api/search/', include(search_index_urls)),

    url(r'^api/notification$', NotificationAPI.as_view()),
    url(r'^api/notification/(?P<pk>\d+)/read$', NotificationAPI.as_view()),
    url(r'^api/subscribe$', SubscriptionAPI.as_view()),

]

# Common
urlpatterns += [
    url(r'^api/talent-categories/$', ListTalentCategories.as_view(), name='talent-categories'),
    url(r'^api/verifyusernameemail/$', VerifyUsernameEmail.as_view(), name='verifyusernameemail'),
]

# wall
urlpatterns += wall_url_patterns
# profile
urlpatterns += profile_url_pattern
# company
urlpatterns += company_url
# jobs
urlpatterns += job_url_patterns
