import cloudinary
from django.conf import settings
from django.db.models import Q
from django.db.transaction import atomic
from friendship.models import Friend
from rest_framework import decorators
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework_jwt import authentication

from casting_secret.exception import DataNotFoundException
from casting_secret.models import Company
from casting_secret.models.profile_models import Albums, UsersProfile
from casting_secret.models.wall_models import Activity, ActivitySocialAction, Comments, ActivityControl
from casting_secret.profile_session import ProfileSession
from casting_secret.serializers.common_serializers import AuthUserSerializerLogin
from casting_secret.wall.serializers import ActivitySerializer, ActivityCommentSerializer, \
    ActivityAttachmentSerializers, CommentMentionSerializer, ActivityMentionSerializer
from casting_secret.wall.utils import check_file_type, is_image


class Activities(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def get(self, request, format=None):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        # retrieve hidden
        activity_hidden = ActivityControl.objects.filter(auth_user=request.user).filter(
            Q(is_hidden=True) | Q(is_reported=True)).values('activity_id')
        # TODO get connection posts Friends or Company
        friends = Friend.objects.friends(request.user)
        friends.append(request.user)
        # Get company post
        profile_session = ProfileSession(request)
        company = profile_session.get_company()
        if company:
            company = company[1]

        if company:
            print("is company")
            activity_data = Activity.objects.filter(company=company, blocked=False) \
                .exclude(pk__in=[activity_hidden]).prefetch_related('activity_attachment')
        else:
            activity_data = Activity.objects.filter(auth_user__in=[user for user in friends], blocked=False) \
                .exclude(pk__in=[activity_hidden]).prefetch_related('activity_attachment')
        if activity_data:
            result_page = paginator.paginate_queryset(activity_data, request)
            data = ActivitySerializer(instance=result_page, many=True, context={'request': request}).data
            return paginator.get_paginated_response(data)
        else:
            raise DataNotFoundException

        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)

    @atomic
    def post(self, request):
        activity = ActivitySerializer(data=request.data, context={'request': request})
        activity.is_valid(raise_exception=True)
        profile_session = ProfileSession(request)
        company = profile_session.get_company()
        if company and company[0]:
            activity.save(auth_user=request.user, company=Company.objects.get(id=company[1].pk))
        else:
            activity.save(auth_user=request.user)
        if activity and 'mentions' in request.data:
            activity_mention = ActivityMentionSerializer(data=request.data['mentions'], many=True)
            activity_mention.is_valid(raise_exception=True)
            activity_mention.save(activity=activity.instance)
        return Response(data=activity.data, status=HTTP_201_CREATED)

    @atomic
    @decorators.renderer_classes(MultiPartParser)
    def put(self, request, pk):
        profile = get_object_or_404(UsersProfile, auth_user=request.user)
        activity = Activity.objects.get(pk=pk)
        file = request.FILES['file']
        file_type = check_file_type(file)
        album = None
        if is_image(file):
            album, created = Albums.objects.get_or_create(
                album_name=settings.POST_ALBUM,
                user_profile=profile
            )

        if file_type == 'IMG':
            data = cloudinary.uploader.upload(
                request.FILES['file'],
                folder='wall',
                crop='limit',
                use_filename=True,
                eager=[
                    {'width': 528, 'height': 325, 'crop': 'fit', 'format': 'png'},  # 3
                    {'width': 262, 'height': 325, 'crop': 'fit', 'format': 'png'},  # 2
                    {'width': 262, 'height': 120, 'crop': 'fit', 'format': 'png'},  # 1
                    {'width': 170, 'height': 120, 'crop': 'fit', 'format': 'png'},  # 0
                ]
            )
        else:
            data = cloudinary.uploader.upload_large(
                request.FILES['file'],
                resource_type="auto"
            )

        attachment = activity.activity_attachment.create(
            path=data['secure_url'],
            type=file_type,
            auth_user=request.user,
            album=album,
            path_json=data['public_id']
        )

        return Response(data=ActivityAttachmentSerializers(instance=attachment, context={'request': request}).data,
                        status=HTTP_201_CREATED)


class SavedActivities(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def get(self, request, format=None):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        activityControlQueryset = ActivityControl.objects.filter(is_saved=True, auth_user=request.user)

        activity_data = Activity.objects.filter(
            pk__in=[x.activity.pk for x in activityControlQueryset]).prefetch_related('activity_attachment')
        if 'search' in request.GET:
            activity_data = activity_data.filter(content__contains=request.GET.get('search', None))
        if activity_data:
            result_page = paginator.paginate_queryset(activity_data, request)
            data = ActivitySerializer(instance=result_page, many=True, context={'request': request}).data
            return paginator.get_paginated_response(data)
        else:
            raise DataNotFoundException

        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)


class ViewActivity(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    # View post
    def get(self, request, pk, formate=None):
        activity = Activity.objects.get(pk=pk)
        if activity:
            return Response(data=ActivitySerializer(instance=activity, context={'request': request}).data,
                            status=HTTP_200_OK)
        raise DataNotFoundException


class LikeActivity(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def post(self, request, pk, formate=None):
        get_object_or_404(Activity, pk=pk)
        ActivitySocialAction.objects.get_or_create(
            auth_user=request.user, activity_id=pk, has_like=True
        )
        try:
            object = ActivitySocialAction.objects.get(
                auth_user=request.user, activity_id=pk, has_dislike=True
            )

            object.delete()

        except Exception as e:
            pass
        return Response(status=HTTP_201_CREATED)

    def get(self, request, pk, formate=None):
        get_object_or_404(Activity, pk=pk)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        activity_action = ActivitySocialAction.objects.filter(activity_id=pk, has_like=True)
        auth_users = [u.auth_user for u in activity_action]
        result_page = paginator.paginate_queryset(auth_users, request)
        data = AuthUserSerializerLogin(instance=result_page, many=True, context={'request': request}).data
        return paginator.get_paginated_response(data)


class UnlikeActivity(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def post(self, request, pk, formate=None):
        get_object_or_404(Activity, pk=pk)
        ActivitySocialAction.objects.get_or_create(
            auth_user=request.user, activity_id=pk, has_dislike=True
        )
        try:
            object = ActivitySocialAction.objects.get(
                auth_user=request.user, activity_id=pk, has_like=True
            )
            object.delete()
        except Exception as e:
            pass
        return Response(status=HTTP_201_CREATED)

    def get(self, request, pk, formate=None):
        get_object_or_404(Activity, pk=pk)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        activity_action = ActivitySocialAction.objects.filter(activity_id=pk, has_dislike=True)
        auth_users = [u.auth_user for u in activity_action]
        result_page = paginator.paginate_queryset(auth_users, request)
        data = AuthUserSerializerLogin(instance=result_page, many=True, context={'request': request}).data
        return paginator.get_paginated_response(data)


class ShareActivity(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def post(self, request, pk, formate=None):
        activity = get_object_or_404(Activity, pk=pk)
        ActivitySocialAction.objects.get_or_create(
            auth_user=request.user, activity_id=pk, has_share=True
        )

        shared_activity = Activity.objects.create(
            auth_user=request.user,
            original_activity_id=activity.pk,
            content='',
            action='shared %s post' if activity.auth_user == request.user else "shared a %s"
        )

        shared_activity = ActivitySerializer(instance=shared_activity, context={'request': request}).data
        return Response(data=shared_activity, status=HTTP_201_CREATED)


class ActivityBookMark(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def post(self, request, pk, formate=None):
        activity = get_object_or_404(Activity, pk=pk)
        ActivityControl.objects.get_or_create(
            auth_user=request.user, activity=activity, is_saved=True
        )
        return Response(status=HTTP_201_CREATED)


class ActivityRemoveBookmark(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def post(self, request, pk, formate=None):
        activity = get_object_or_404(Activity, pk=pk)
        activity_control = get_object_or_404(ActivityControl, auth_user=request.user, activity=activity, is_saved=True)
        activity_control.is_saved = False
        activity_control.save()
        return Response(status=HTTP_201_CREATED)


class ActivityReportAPI(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def post(self, request, pk, formate=None):
        activity = get_object_or_404(Activity, pk=pk)
        ActivityControl.objects.get_or_create(
            auth_user=request.user, activity=activity, is_reported=True
        )
        return Response(status=HTTP_201_CREATED)


class ActivityHideAPI(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    def post(self, request, pk, formate=None):
        activity = get_object_or_404(Activity, pk=pk)
        ActivityControl.objects.get_or_create(
            auth_user=request.user, activity=activity, is_hidden=True
        )
        return Response(status=HTTP_201_CREATED)


class Comment(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    @atomic
    def post(self, request, pk, formate=None):
        actvity = get_object_or_404(Activity, pk=pk)
        comment = ActivityCommentSerializer(data=request.data)
        comment.is_valid(raise_exception=True)
        comment.save(auth_user=request.user, activity=actvity)
        if comment and 'mentions' in request.data:
            comment_mention = CommentMentionSerializer(data=request.data['mentions'], many=True)
            comment_mention.is_valid(raise_exception=True)
            comment_mention.save(comment=comment.instance)

        return Response(data=comment.data, status=HTTP_201_CREATED)

    def get(self, request, pk, formate=None):
        paginator = PageNumberPagination()
        paginator.page_size = 10

        activity = get_object_or_404(Activity, pk=pk)
        comments = Comments.objects.filter(activity=activity, thread=None).prefetch_related('comment_mention')
        result_page = paginator.paginate_queryset(comments, request)
        data = ActivityCommentSerializer(instance=result_page, many=True).data
        return paginator.get_paginated_response(data)

    def delete(self, request, pk, comment_id, formate=None):
        comment = get_object_or_404(Comments, activity__id=pk, pk=comment_id)
        comment.delete()
        return Response(status=HTTP_200_OK)

    def put(self, request, pk, comment_id, formate=None):
        comment = get_object_or_404(Comments, activity__id=pk, pk=comment_id)
        comment_serializer = ActivityCommentSerializer(instance=comment, data=request.data, partial=True)
        comment_serializer.is_valid(raise_exception=True)
        comment_serializer.save()
        return Response(data=comment_serializer.data, status=HTTP_200_OK)
