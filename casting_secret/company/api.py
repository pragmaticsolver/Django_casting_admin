import cloudinary
from django.conf import settings
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils.text import slugify
from friendship.models import Follow
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt import authentication

from casting_secret.company.serializer import CompanySerializer
from casting_secret.models.company_models import Company, CompanyTags
from casting_secret.models.profile_models import UsersProfile
from casting_secret.profile_session import ProfileSession
from casting_secret.wall.utils import is_image


class CompanyView(GenericViewSet):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    @atomic
    @action(methods=['POST'], detail=True)
    def create_new_company(self, request, slug):
        profile = get_object_or_404(UsersProfile, auth_user=request.user)
        company_serializer = CompanySerializer(data=request.data, context={'request': request})
        company_serializer.is_valid(raise_exception=True)
        company_serializer.save(user_profile=profile,
                                slug=slugify('%s %s' % (request.data['name'], profile.auth_user.id),
                                             allow_unicode=True))
        # create profile talent category
        categories = request.data.get('tags', list())
        bulk_tags = []
        for category in categories:
            tags = CompanyTags()
            tags.company = company_serializer.instance
            tags.category_id = category
            bulk_tags.append(tags)
        try:
            CompanyTags.objects.bulk_create(bulk_tags)
        except Exception as e:
            return Response(data=str(e), status=HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=company_serializer.data, status=HTTP_201_CREATED)

    @atomic
    @action(methods=['PATCH'], detail=True)
    def update_company(self, request, slug):
        company = get_object_or_404(Company, user_profile__auth_user=request.user, slug=slug)
        company_serializer = CompanySerializer(instance=company, data=request.data, partial=True,
                                               context={'request': request})
        company_serializer.is_valid(raise_exception=True)
        company_serializer.save()

        # create profile talent category
        categories = request.data.get('tags', list())
        if categories:
            company.tags.all().delete()

        bulk_tags = []
        for category in categories:
            tags = CompanyTags()
            tags.company = company_serializer.instance
            tags.category_id = category['category']['id']
            bulk_tags.append(tags)
        try:
            CompanyTags.objects.bulk_create(bulk_tags)
        except Exception as e:
            return Response(data=str(e), status=HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=company_serializer.data, status=HTTP_200_OK)

    @action(methods=['PATCH'], url_name='company_upload_avatar', detail=True)
    def upload_avatar(self, request, slug):
        company = get_object_or_404(Company, user_profile__auth_user=request.user, slug=slug)
        file = request.FILES['file']
        is_image(file)
        data = cloudinary.uploader.upload(
            request.FILES['file'],
            folder=settings.AVATAR,
            crop='limit',
            use_filename=True,
            eager=[
                {'width': 200, 'height': 200,
                 'crop': 'thumb', 'gravity': 'face',
                 'radius': 'max', 'effect': 'sepia'},
                {'width': 100, 'height': 150,
                 'crop': 'fit', 'format': 'png'}
            ]
        )

        company.avatar = data['public_id']
        company.save()
        company_serializer = CompanySerializer(company, context={'request': request})
        return Response(data=company_serializer.data, status=HTTP_201_CREATED)

    @action(methods=['PATCH'], url_name='company_upload_cover', detail=True)
    def upload_cover(self, request, slug, formate=None):
        company = get_object_or_404(Company, user_profile__auth_user=request.user, slug=slug)
        file = request.FILES['file']
        is_image(file)
        data = cloudinary.uploader.upload(
            request.FILES['file'],
            folder=settings.AVATAR,
            crop='limit',
            use_filename=True,
            eager=[
                {'width': 200, 'height': 200,
                 'crop': 'thumb', 'gravity': 'face',
                 'radius': 'max', 'effect': 'sepia'},
                {'width': 100, 'height': 150,
                 'crop': 'fit', 'format': 'png'}
            ]
        )
        company.cover = data['public_id']
        company.save()
        company_serializer = CompanySerializer(company, context={'request': request})
        return Response(data=company_serializer.data, status=HTTP_201_CREATED)

    @action(methods=['GET'], url_name='company', detail=True)
    def get_profile_companies(self, request, slug):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        list_company = get_list_or_404(Company, user_profile__auth_user=request.user, user_profile__slug=slug)
        result_page = paginator.paginate_queryset(list_company, request)
        company_serializer = CompanySerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(company_serializer.data)

    @staticmethod
    def delete(self, request, slug):
        company = get_object_or_404(Company, user_profile__auth_user=request.user, slug=slug)
        company.delete()
        return Response(status=HTTP_200_OK)

    @staticmethod
    def get(self, request, slug):
        company = get_object_or_404(Company, slug=slug)
        serializer = CompanySerializer(company, context={'request': request})
        return Response(data=serializer.data, status=HTTP_200_OK)

    @staticmethod
    @action(methods=['POST'], detail=True)
    def switch_to_company(self, request, slug):
        company = get_object_or_404(Company, user_profile__auth_user=request.user, slug=slug)
        company_serializer = CompanySerializer(company, context={'request': request}).data
        profile_session = ProfileSession(request, company)
        profile_session.switch_to_company()
        return Response(data=company_serializer, status=HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def follow_company(self, request, slug, formate=None):
        company = get_object_or_404(Company, slug=slug)
        Follow.objects.add_follower(request.user, company.user_profile.auth_user)
        return Response(status=HTTP_201_CREATED)

    @action(methods=['POST'], detail=True)
    def unfollow_company(self, request, slug, formate=None):
        company = get_object_or_404(Company, slug=slug)
        Follow.objects.remove_follower(request.user, company.user_profile.auth_user)
        return Response(status=HTTP_201_CREATED)

    @action(methods=['GET'], detail=True)
    def get_loggedin_follow_company(self, request):
        following = Follow.objects.followers(request.user)
        companies = Company.objects.filter(user_profile__auth_user__in=[f for f in following])
        if request.GET.get('name', None):
            companies.filter(name__contains=request.GET.get('name'))

        if request.GET.get('tags__in', None):
            companies.filter(id__in=[tags.company.pk for tags in CompanyTags.objects.filter(
                id__in=[x for x in request.GET.get('tags__in').split(',')])])
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(companies, request)
        company_serializer = CompanySerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(company_serializer.data)

    @action(methods=['GET'], detail=True)
    def get_my_own_company(self, request):
        following = Follow.objects.followers(request.user)
        companies = Company.objects.filter(user_profile__auth_user=request.user)
        if request.GET.get('name', None):
            companies.filter(name__contains=request.GET.get('name'))

        if request.GET.get('tags__in', None):
            companies.filter(id__in=[tags.company.pk for tags in CompanyTags.objects.filter(
                id__in=[x for x in request.GET.get('tags__in').split(',')])])
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(companies, request)
        company_serializer = CompanySerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(company_serializer.data)
