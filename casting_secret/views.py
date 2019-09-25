from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from django.shortcuts import render, HttpResponse

# Create your views here.
from rest_auth.registration.views import SocialLoginView, SocialConnectView
from rest_auth.social_serializers import TwitterLoginSerializer, TwitterConnectSerializer
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Casting Secret API')


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class TwitterLogin(SocialLoginView):
    serializer_class = TwitterLoginSerializer
    adapter_class = TwitterOAuthAdapter


class FacebookConnect(SocialConnectView):
    adapter_class = FacebookOAuth2Adapter


class TwitterConnect(SocialConnectView):
    serializer_class = TwitterConnectSerializer
    adapter_class = TwitterOAuthAdapter
