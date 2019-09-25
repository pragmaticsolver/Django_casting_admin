import cloudinary
from django.conf import settings
from django.db.models import Q
from django.db.transaction import atomic
from django.shortcuts import get_list_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from friendship.models import Friend, FriendshipRequest
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import APIView
from rest_framework_jwt import authentication

from casting_secret.exception import DataNotFoundException
from casting_secret.models import ProfileSettings, ProfileViewers
from casting_secret.models.profile_models import AgeRangeLookUp, HeightRangeLookUp, WeightRangeLookUp, BuildLookUp, \
    HairLookUp, EyesLookUp, EthnicitiesLookUp, HobbiesLookUp, UsersProfile, ProfileTraining, ProfileSocialLinks, Albums, \
    ProfileHobbies
from casting_secret.models.wall_models import Activity, ActivityAttachment, ActivityControl
from casting_secret.profile_session import ProfileSession
from casting_secret.serializers.common_serializers import AuthUserSerializerLogin
from casting_secret.user_profile.serializers import AgeRangeLookUpSerializer, HeightRangeLookUpSerializer, \
    WeightRangeLookUpSerializer, BuildLookUpSerializer, HairLookUpSerializer, EyesLookUpSerializer, \
    EthnicitiesLookUpSerializer, HobbiesLookUpSerializer, UserProfileSerializer, ProfileTrainingSerializer, \
    ProfileSocialSerializer, ProfileHobbiessSerializer, UserProfileUpdateSerializer, \
    UserProfileSettingsSerializer
from casting_secret.wall.serializers import ActivitySerializer, ActivityAttachmentSerializers, AlbumSerializer
from casting_secret.wall.utils import check_file_type, is_image


class Lookups(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    @method_decorator(cache_page(timeout=(60 * 60 * 5), key_prefix='profile-lookup'))
    @method_decorator(vary_on_cookie)
    def get(self, request, formate=None):
        age_range_query_set = AgeRangeLookUp.objects.all()
        height_range_query_set = HeightRangeLookUp.objects.all()
        weight_range_query_set = WeightRangeLookUp.objects.all()
        build_query_set = BuildLookUp.objects.all()
        hair_query_set = HairLookUp.objects.all()
        eyes_query_set = EyesLookUp.objects.all()
        ethnicities_query_set = EthnicitiesLookUp.objects.all()
        hobbies_query_set = HobbiesLookUp.objects.all()

        age_range_serializer = AgeRangeLookUpSerializer(instance=age_range_query_set, many=True)
        height_range_serializer = HeightRangeLookUpSerializer(instance=height_range_query_set, many=True)
        weight_range_serializer = WeightRangeLookUpSerializer(instance=weight_range_query_set, many=True)
        build_serializer = BuildLookUpSerializer(instance=build_query_set, many=True)
        hair_serializer = HairLookUpSerializer(instance=hair_query_set, many=True)
        eyes_serializer = EyesLookUpSerializer(instance=eyes_query_set, many=True)
        ethnicities_serializer = EthnicitiesLookUpSerializer(instance=ethnicities_query_set, many=True)
        hobbies_serializer = HobbiesLookUpSerializer(instance=hobbies_query_set, many=True)

        context = {
            'height_range': height_range_serializer.data,
            'weight_range': weight_range_serializer.data,
            'build': build_serializer.data,
            'hair': hair_serializer.data,
            'eye': eyes_serializer.data,
            'ethnicities': ethnicities_serializer.data,
            'hobbies': hobbies_serializer.data
        }

        return Response(data=context, status=HTTP_200_OK)


class ProfileDetails(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def get(self, request, slug, formate=None):
        profile_object = UsersProfile.objects.filter(slug=slug).prefetch_related('users_profile_social',
                                                                                 'users_profile_hobbies',
                                                                                 'users_profile_courses')
        if profile_object:
            profile_serializer = UserProfileSerializer(instance=profile_object, context={'request': request},
                                                       many=True).data
            if profile_object[0].auth_user != request.user:
                p = ProfileViewers()
                p.user_profile = profile_object[0]
                p.visitor_profile = UsersProfile.objects.get(auth_user=request.user)
                p.save()

            return Response(data=profile_serializer[0], status=HTTP_200_OK)

        else:
            raise DataNotFoundException


class ProfileUpdate(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def patch(self, request, slug, formate=None):
        profile = get_object_or_404(UsersProfile, auth_user=request.user)
        profile = UserProfileUpdateSerializer(profile, data=request.data, partial=True)
        profile.is_valid(raise_exception=True)
        profile.save(auth_user=request.user)
        return Response(status=HTTP_200_OK)


class ProfileTrainingView(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def post(self, request, slug, formate=None):
        profile = get_object_or_404(UsersProfile, auth_user=request.user)
        if type(request.data) is list:
            profile_training = ProfileTrainingSerializer(data=request.data, many=True)
        else:
            profile_training = ProfileTrainingSerializer(data=request.data)
        profile_training.is_valid(raise_exception=True)
        profile_training.save(user_profile=profile)
        return Response(data=profile_training.data, status=HTTP_201_CREATED)

    def delete(self, request, slug, pk, formate=None):
        try:
            training = ProfileTraining.objects.get(pk=pk, user_profile__auth_user=request.user)
            training.delete()
            return Response(status=HTTP_200_OK)
        except Exception:
            raise DataNotFoundException

    def put(self, request, slug, pk, formate=None):
        try:
            profile_training = ProfileTraining.objects.get(pk=pk, user_profile__auth_user=request.user)
            profile_training = ProfileTrainingSerializer(profile_training, data=request.data)
            profile_training.is_valid(raise_exception=True)
            profile_training.save()
            return Response(data=profile_training.data, status=HTTP_200_OK)
        except Exception:
            raise DataNotFoundException


class ProfileSocial(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def post(self, request, slug, formate=None):
        profile = get_object_or_404(UsersProfile, auth_user=request.user)
        if type(request.data) is list:
            profile_social = ProfileSocialSerializer(data=request.data, many=True)
        else:
            profile_social = ProfileSocialSerializer(data=request.data)
        profile_social.is_valid(raise_exception=True)
        profile_social.save(user_profile=profile)
        return Response(data=profile_social.data, status=HTTP_201_CREATED)

    def put(self, request, slug, pk, formate=None):
        profile = get_object_or_404(UsersProfile, auth_user=request.user)
        profile_social = get_object_or_404(ProfileSocialLinks, user_profile=profile, pk=pk)
        profile_social = ProfileSocialSerializer(profile_social, data=request.data)
        profile_social.is_valid(raise_exception=True)
        profile_social.save(user_profile=profile, pk=pk)
        return Response(data=profile_social.data, status=HTTP_200_OK)

    def delete(self, request, slug, pk, formate=None):
        user_profile = get_object_or_404(UsersProfile, auth_user=request.user)
        profile_social = get_object_or_404(ProfileSocialLinks, user_profile=user_profile, pk=pk)
        profile_social.delete()
        return Response(status=HTTP_200_OK)


class ProfileFriendsAPI(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    @staticmethod
    def get(request, slug, ):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        profile = get_object_or_404(UsersProfile, slug=slug)
        friends = Friend.objects.friends(profile.auth_user)
        if 'query' in request.GET and len(request.GET['query']) > 3:
            friends = [x for x in friends if request.GET['query'] in x.first_name + ' ' + x.last_name]
        if friends:
            result_page = paginator.paginate_queryset(friends, request)
            data = AuthUserSerializerLogin(instance=result_page, many=True, context={'request': request}).data
            return paginator.get_paginated_response(data)
        else:
            raise DataNotFoundException
        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, slug, formate=None):
        profile = get_object_or_404(UsersProfile, slug=slug)
        Friend.objects.add_friend(
            request.user,  # The sender
            profile.auth_user,  # The recipient
            message='Hi! I would like to add you')  # This message is optional
        return Response(status=HTTP_201_CREATED)

    def delete(self, request, slug, formate=None):
        profile = get_object_or_404(UsersProfile, slug=slug)
        Friend.objects.remove_friend(request.user, profile.auth_user)
        return Response(status=HTTP_200_OK)


class ProfileFriendRequestsAPI(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def get(self, request, slug, formate=None):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        friends = Friend.objects.unread_requests(user=request.user)
        if friends:
            friends = [friend.from_user for friend in friends]
            result_page = paginator.paginate_queryset(friends, request)
            data = AuthUserSerializerLogin(instance=result_page, many=True, context={'request': request}).data
            return paginator.get_paginated_response(data)
        else:
            raise DataNotFoundException
        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileActivity(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def get(self, request, slug, formate=None):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        profile = get_object_or_404(UsersProfile, slug=slug)
        activity_data = Activity.objects.filter(auth_user=profile.auth_user).prefetch_related('activity_attachment')
        if activity_data:
            result_page = paginator.paginate_queryset(activity_data, request)
            data = ActivitySerializer(instance=result_page, many=True, context={'request': request}).data
            return paginator.get_paginated_response(data)
        else:
            raise DataNotFoundException

        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileActivityBookMarked(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def get(self, request, slug, formate=None):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        profile = get_object_or_404(UsersProfile, slug=slug)
        bookmarked_activity = ActivityControl.objects.filter(auth_user=profile.auth_user, is_saved=True).values(
            'activity_id')
        bookmarked_activity.exclude(is_hidden=True)
        bookmarked_activity.exclude(is_reported=False)
        bookmarked_activity = bookmarked_activity.values('activity_id')
        activity_data = Activity.objects.filter(pk__in=[bookmarked_activity]).prefetch_related('activity_attachment')
        if activity_data:
            result_page = paginator.paginate_queryset(activity_data, request)
            data = ActivitySerializer(instance=result_page, many=True, context={'request': request}).data
            return paginator.get_paginated_response(data)
        else:
            raise DataNotFoundException

        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileAcceptFriendShip(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def post(self, request, slug, formate=None):
        profile = get_object_or_404(UsersProfile, slug=slug)
        friend_request = FriendshipRequest.objects.get(from_user=profile.auth_user)
        friend_request.accept()
        return Response(status=HTTP_201_CREATED)


class ProfileRejectFriendShip(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def post(self, request, slug, formate=None):
        profile = get_object_or_404(UsersProfile, slug=slug)
        friend_request = FriendshipRequest.objects.get(from_user=profile.auth_user)
        friend_request.reject()
        return Response(status=HTTP_201_CREATED)


class ProfileHobbiesAPI(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def post(self, request, slug, formate=None):
        profile = get_object_or_404(UsersProfile, auth_user=request.user)
        if type(request.data) is list:
            serilzier = ProfileHobbiessSerializer(data=request.data, many=True)
        else:
            serilzier = ProfileHobbiessSerializer(data=request.data, many=False)
        # serilzier.validate(request.data)
        serilzier.is_valid(raise_exception=True)
        serilzier.save(user_profile=profile)
        return Response(data=serilzier.data, status=HTTP_201_CREATED)

    def put(self, request, slug, pk, formate=None):
        profile = get_object_or_404(UsersProfile, auth_user=request.user)
        serilzier = get_object_or_404(ProfileHobbies, pk=pk, user_profile=profile)
        serilzier = ProfileHobbiessSerializer(serilzier, data=request.data, many=False)
        serilzier.is_valid(raise_exception=True)
        serilzier.save(pk=pk)
        return Response(data=serilzier.data, status=HTTP_200_OK)

    def delete(self, request, slug, pk, formate=None):
        profile = get_object_or_404(UsersProfile, auth_user=request.user)
        hobby = get_object_or_404(ProfileHobbies, pk=pk, user_profile=profile)
        hobby.delete()
        return Response(status=HTTP_200_OK)


class ProfileMediaVideo(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    @atomic
    def post(self, request, slug, formate=None):
        activity = Activity(
            content=None,
            auth_user=request.user
        )

        activity.save()
        file = request.FILES['file']
        file_type = check_file_type(file)

        data = cloudinary.uploader.upload_large(
            request.FILES['file'],
            resource_type="video"
        )

        # TODO need more enhancement
        attachment = activity.activity_attachment.create(
            path=data['secure_url'],
            type=file_type,
            auth_user=request.user
        )
        return Response(data=ActivitySerializer(instance=attachment.activity, context={'request': request}).data,
                        status=HTTP_201_CREATED)

    def get(self, request, slug, formate=None):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        profile = get_object_or_404(UsersProfile, slug=slug)
        attachment = ActivityAttachment.objects.filter(auth_user=profile.auth_user, type='VIDEO')
        # retrieve hidden
        activity_hidden = ActivityControl.objects.filter(auth_user=request.user).filter(
            Q(is_hidden=True) | Q(is_reported=True)).values('activity_id')

        activity_data = Activity.objects.filter(pk__in=[activity.activity.pk for activity in attachment]) \
            .exclude(pk__in=[activity_hidden])

        if activity_data:
            result_page = paginator.paginate_queryset(activity_data, request)
            data = ActivitySerializer(instance=result_page, many=True, context={'request': request}).data
            return paginator.get_paginated_response(data)
        else:
            raise DataNotFoundException

        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileMediaAudio(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    @atomic
    def post(self, request, slug, formate=None):
        activity = Activity(
            content=None,
            auth_user=request.user
        )

        activity.save()
        file = request.FILES['file']
        file_type = check_file_type(file)

        data = cloudinary.uploader.upload_large(
            request.FILES['file'],
            resource_type="video"
        )
        # TODO need more enhancement

        attachment = activity.activity_attachment.create(
            path=data['secure_url'],
            type=file_type,
            auth_user=request.user
        )
        return Response(data=ActivityAttachmentSerializers(instance=attachment, context={'request': request}).data,
                        status=HTTP_201_CREATED)

    def get(self, request, slug, formate=None):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        profile = get_object_or_404(UsersProfile, slug=slug)
        attachment = ActivityAttachment.objects.filter(auth_user=profile.auth_user, type='AUDIO')
        # retrieve hidden
        activity_hidden = ActivityControl.objects.filter(auth_user=request.user).filter(
            Q(is_hidden=True) | Q(is_reported=True)).values('activity_id')

        activity_data = Activity.objects.filter(pk__in=[activity.activity.pk for activity in attachment]) \
            .exclude(pk__in=[activity_hidden])
        if activity_data:
            result_page = paginator.paginate_queryset(activity_data, request)
            data = ActivitySerializer(instance=result_page, many=True, context={'request': request}).data
            return paginator.get_paginated_response(data)
        else:
            raise DataNotFoundException

        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileAvatar(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    @atomic
    def patch(self, request, slug):
        profile = get_object_or_404(UsersProfile, auth_user=request.user)
        file = request.FILES['file']
        is_image(file)

        data = cloudinary.uploader.upload(file, folder=settings.AVATAR, crop='limit', use_filename=True,
                                          eager=[{'width': 200, 'height': 200, 'crop': 'thumb', 'gravity': 'face',
                                                  'radius': 'max', 'effect': 'sepia'},
                                                 {'width': 100, 'height': 150, 'crop': 'fit', 'format': 'png'}
                                                 ]
                                          )
        profile.avatar = data['public_id']
        profile.save()

        album, created = Albums.objects.get_or_create(album_name=settings.AVATAR_ALBUM, user_profile=profile)

        activity = Activity(content=None, auth_user=request.user, action='change %s profile picture')

        activity.save()

        activity.activity_attachment.create(path=file, type='IMG', auth_user=request.user, album=album)
        data = UserProfileSerializer(profile, context={'request': request}).data
        return Response(data=data, status=HTTP_200_OK)


class ProfileCover(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    @atomic
    def post(self, request, slug):
        profile = get_object_or_404(UsersProfile, auth_user=request.user)
        profile.cover = None
        profile.save()
        return Response(status=HTTP_200_OK)

    @atomic
    def patch(self, request, slug):
        profile = get_object_or_404(UsersProfile, auth_user=request.user)
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
        profile.cover = data['public_id']
        profile.save()

        album, created = Albums.objects.get_or_create(
            album_name=settings.COVER_ALBUM,
            user_profile=profile
        )

        activity = Activity(
            content=None,
            auth_user=request.user,
            action='change %s profile cover'
        )

        activity.save()

        activity.activity_attachment.create(
            path=file,
            type='IMG',
            auth_user=request.user,
            album=album

        )

        return Response(data=UserProfileSerializer(profile, context={'request': request}).data,
                        status=HTTP_200_OK)


class ProfileAlbum(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def post(self, request, slug, formate=None):
        profile = get_object_or_404(UsersProfile, slug=slug)
        album_serializer = AlbumSerializer(data=request.data)
        album_serializer.is_valid(raise_exception=True)
        album_serializer.save(user_profile=profile)
        return Response(data=album_serializer.data, status=HTTP_201_CREATED)

    def get(self, request, slug, formate=None):
        profile = get_object_or_404(UsersProfile, slug=slug)
        album_query_set = Albums.objects.filter(user_profile=profile)
        album_serializer = AlbumSerializer(album_query_set, many=True)
        return Response(data=album_serializer.data, status=HTTP_200_OK)


class ProfilePictureAlbum(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def get(self, request, slug, formate=None):
        paginator = PageNumberPagination()
        paginator.page_size = 10

        profile = get_object_or_404(UsersProfile, slug=slug)
        if 'limit' in request.GET:
            attachment = ActivityAttachment.objects.filter(auth_user=profile.auth_user, type='IMG')
            activity_hidden = ActivityControl.objects.filter(auth_user=profile.auth_user).filter(
                Q(is_hidden=True) | Q(is_reported=True)).values('activity_id')
            activity_data = Activity.objects.filter(pk__in=[activity.activity.pk for activity in attachment]).exclude(
                pk__in=[activity_hidden])[:4]

        else:
            attachment = ActivityAttachment.objects.filter(auth_user=profile.auth_user, type='IMG')
            activity_hidden = ActivityControl.objects.filter(auth_user=profile.auth_user).filter(
                Q(is_hidden=True) | Q(is_reported=True)).values('activity_id')
            activity_data = Activity.objects.filter(pk__in=[activity.activity.pk for activity in attachment]).exclude(
                pk__in=[activity_hidden])
        if activity_data:
            result_page = paginator.paginate_queryset(activity_data, request)
            data = ActivitySerializer(instance=result_page, many=True, context={'request': request}).data
            return paginator.get_paginated_response(data)
        else:
            raise DataNotFoundException

        return Response(data=album_serializer.data, status=HTTP_200_OK)


class ProfileAlbumUpload(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def get(self, request, slug, pk, formate=None):
        profile = get_object_or_404(UsersProfile, slug=slug)
        album = get_object_or_404(Albums, pk=pk, user_profile=profile)
        activity_hidden = ActivityControl.objects.filter(auth_user=request.user).filter(
            Q(is_hidden=True) | Q(is_reported=True)).values('activity_id')
        activity_attachement_list = get_list_or_404(ActivityAttachment, ~Q(pk__in=[activity_hidden]), album=album)
        activity_list = get_list_or_404(Activity,
                                        pk__in=[attachment.activity.pk for attachment in activity_attachement_list])

        return Response(data=ActivitySerializer(instance=activity_list, many=True, context={'request': request}).data,
                        status=HTTP_200_OK)

    @atomic
    def post(self, request, slug, formate=None):
        profile = get_object_or_404(UsersProfile, auth_user=request.user)
        file = request.FILES['file']
        is_image(file)
        album, created = Albums.objects.get_or_create(
            album_name=settings.UNTITLED_ALBUM,
            user_profile=profile
        )

        activity = Activity(
            auth_user=request.user,
            content='',
            is_active=False
        )

        activity.save()

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

        activity.activity_attachment.create(
            path=data['secure_url'],
            type='IMG',
            auth_user=request.user,
            album=album
        )

        return Response(data=ActivitySerializer(instance=activity, context={'request': request}).data,
                        status=HTTP_201_CREATED)

    @atomic
    def put(self, request, slug, pk, formate=None):
        get_object_or_404(UsersProfile, auth_user=request.user)
        activity = get_object_or_404(Activity, pk=pk, is_active=False)
        activity.is_active = True
        activity.content = request.data['content']
        activity.save()

        if 'album_id' in request.data:
            attachment = ActivityAttachment.objects.get(activity=activity)
            attachment.album_id = request.data['album_id']
            attachment.save()
        return Response(data=ActivitySerializer(instance=activity, context={'request': request}).data,
                        status=HTTP_201_CREATED)


class Switchtouser(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def post(self, request, slug):
        user = get_object_or_404(UsersProfile, auth_user=request.user, slug=slug)
        user_serializer = UserProfileSerializer(user, context={'request': request}).data
        profile_session = ProfileSession(request, user_serializer)
        profile_session.switch_to_user()
        return Response(data=user_serializer, status=HTTP_200_OK)


class ProfileSettingsAPI(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    @staticmethod
    def get(request, slug):
        profile = get_object_or_404(UsersProfile, slug=slug)
        settings_model, created = ProfileSettings.objects.get_or_create(user_profile=profile)
        settings_serializer = UserProfileSettingsSerializer(settings_model, context={'request': request}).data
        return Response(data=settings_serializer, status=HTTP_200_OK)

    @staticmethod
    def patch(self, request, slug):
        profile = get_object_or_404(UsersProfile, auth_user=request.user, slug=slug)
        settings_object = get_object_or_404(ProfileSettings, user_profile=profile)
        profile_settings = UserProfileSettingsSerializer(instance=settings_object, data=request.data, partial=True)
        profile_settings.is_valid(raise_exception=True)
        profile_settings.save()
        return Response(status=HTTP_200_OK)


class ProfileVisitor(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def get(self, request, slug, formate=None):
        profile = get_object_or_404(UsersProfile, slug=slug, auth_user=request.user)
        viewers = ProfileViewers.objects.get(user_profile=profile)
        viewers_serializer = ProfileViewers(viewers, context={'request': request}).data
        return Response(data=viewers_serializer, status=HTTP_200_OK)


class RandomProfiles(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, formate=None):
        users = UsersProfile.objects.all().order_by("?")[:10]
        data = UserProfileSerializer(instance=users, context={'request': request},
                                     many=True).data
        return Response(data=data, status=HTTP_200_OK)
