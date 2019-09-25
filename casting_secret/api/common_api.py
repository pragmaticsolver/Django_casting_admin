import datetime
import json

from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.shortcuts import get_list_or_404, get_object_or_404
from notify.models import Notification
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt import authentication

from casting_secret.models.models import TalentCategories, Subscription
from casting_secret.serializers.common_serializers import TalentCategoriesSerializer, NotificationSerializer


class ListTalentCategories(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, formate=None):
        talent_categories = TalentCategories.objects.all()
        data = TalentCategoriesSerializer(talent_categories, many=True).data
        return Response(data, status=HTTP_200_OK)
        talent_categoires = TalentCategories.objects.all()
        data = TalentCategoriesSerializer(talent_categoires, many=True).data
        if data:
            return Response(data, status=HTTP_200_OK)
        else:
            return Response('No data found', status=HTTP_204_NO_CONTENT)


class VerifyUsernameEmail(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, formate=None):
        recieved = json.loads(request.body)
        if User.objects.filter(username=recieved['username']).exists():
            return Response('1')
        elif User.objects.filter(email=recieved['email']).exists():
            return Response('1')
        else:
            return Response('0')


class NotificationAPI(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def get(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        if 'year' in request.GET and 'month' in request.GET and request.GET['year'] and request.GET['month']:
            list_notification = get_list_or_404(Notification, recipient=request.user,
                                                created__year=request.GET['year'],
                                                created__month=request.GET['month'])
        else:
            list_notification = get_list_or_404(Notification, recipient=request.user,
                                                created__gt=datetime.datetime.today() - datetime.timedelta(days=30))
        result_page = paginator.paginate_queryset(list_notification, request)
        data = NotificationSerializer(instance=result_page, many=True, context={'request': request}).data
        return paginator.get_paginated_response(data)

    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        notification.read = True
        notification.save()
        return Response(status=HTTP_200_OK)


class EmailHandlerAPI(GenericViewSet):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    @action(methods=['POST'], detail=True)
    def make_email_primary(self, request, email, formate=None):
        email_object = get_object_or_404(EmailAddress, email=email, user=request.user)
        email_object.set_as_primary()
        return Response(status=HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def send_confirmation(self, request, email, formate=None):
        email_object = get_object_or_404(EmailAddress, email=email, user=request.user)
        email_object.send_confirmation()
        return Response(status=HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def change_email(self, request, email, formate=None):
        email_object = get_object_or_404(EmailAddress, email=email, user=request.user)
        email_object.change(request=request, new_email=request.POST.get('new_email'))
        return Response(status=HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def add_email(self, request, formate=None):
        EmailAddress.objects.get_or_create(email=request.POST.get('new_email'), user=request.user)
        return Response(status=HTTP_200_OK)


class SubscriptionAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, formate=None):
        Subscription.objects.get_or_create(email=request.POST.get('email'))
        return Response(status=HTTP_200_OK)
