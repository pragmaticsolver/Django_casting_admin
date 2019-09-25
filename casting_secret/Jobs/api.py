from django.db.transaction import atomic
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import exceptions, serializers
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt import authentication

from casting_secret.Jobs.JobSerializer import JobSerializer, JobSerializerAdmin, \
    JobSerializerAdminNotDetails, InterviewSerializer, ApplicantSerializer
from casting_secret.exception import GeneralException
from casting_secret.models import Job, JobCategory, UsersProfile, Applicants, Shortlisted, JobSchedules
from casting_secret.profile_session import ProfileSession


class JobView(GenericViewSet):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)

    @atomic
    def post(self, request, slug, formate=None):
        profile_in_session = ProfileSession(request=request).is_authorized_company()
        if not profile_in_session.user_profile.auth_user.username == request.user.username and \
                profile_in_session.slug == slug:
            raise exceptions.PermissionDenied('You are not authorize')
        print(profile_in_session)
        job_serializer = JobSerializerAdmin(data=request.data)
        job_serializer.is_valid(raise_exception=True)
        job_serializer.save(company_id=profile_in_session.id)
        if 'category' in request.data:
            bulk_tags = []
            for category in request.data['category']:
                job_category = JobCategory()
                job_category.job = job_serializer.instance
                job_category.job_categories_id = int(category)
                bulk_tags.append(job_category)

            try:
                JobCategory.objects.bulk_create(bulk_tags)
            except Exception as e:
                raise GeneralException(Exception)
        else:
            raise serializers.ValidationError({
                'Category': ['This field is required.']
            })

        return Response(data=JobSerializerAdmin(job_serializer.instance).data, status=HTTP_201_CREATED)

    @atomic
    def patch(self, request, slug, job_slug, formate=None):
        profile_in_session = ProfileSession(request=request).is_authorized_company()
        if not profile_in_session.user_profile.auth_user.username == request.user.username and \
                profile_in_session.slug == slug:
            raise exceptions.PermissionDenied('You are not authorize')

        job = get_object_or_404(Job, slug=job_slug, company__id=profile_in_session.id)
        job_serializer = JobSerializerAdmin(instance=job, data=request.data, partial=True)
        job_serializer.is_valid(raise_exception=True)
        job_serializer.save(company_id=profile_in_session.id)

        # if 'category' in request.data:
        #     job_category = get_object_or_404(JobCategory, job=job)
        #     job_category_serializer = JobCategorySerializer(instance=job_category, data=request.data['category'],
        #                                                     partial=True, many=True)
        #     job_category_serializer.is_valid(raise_exception=True)
        #     job_category_serializer.save()
        #

        if 'category' in request.data:
            JobCategory.objects.filter(job=job).delete()
            bulk_tags = []
            for category in request.data['category']:
                job_category = JobCategory()
                job_category.job = job_serializer.instance
                job_category.job_categories_id = int(category)
                bulk_tags.append(job_category)

            try:
                JobCategory.objects.bulk_create(bulk_tags)
            except Exception as e:
                raise GeneralException(Exception)
        else:
            raise serializers.ValidationError({
                'Category': ['This field is required.']
            })

        return Response(data=JobSerializerAdmin(job_serializer.instance).data, status=HTTP_201_CREATED)

    def delete(self, request, slug, job_slug, formate=None):
        profile_in_session = ProfileSession(request=request).is_authorized_company()
        if not profile_in_session.user_profile.auth_user.username == request.user.username and \
                profile_in_session.slug == slug:
            raise exceptions.PermissionDenied('You are not authorize')

        job = get_object_or_404(Job, slug=job_slug, company__id=profile_in_session.id)
        job.delete()
        return Response(status=HTTP_200_OK)

    def get(self, request, slug, job_slug, formate=None):
        profile_in_session = ProfileSession(request=request).is_authorized_company()
        print(profile_in_session.id)
        if not profile_in_session.user_profile.auth_user.username == request.user.username and \
                profile_in_session.slug == slug:
            raise exceptions.PermissionDenied('You are not authorize')

        job = get_object_or_404(Job, slug=job_slug, company__id=profile_in_session.id)
        return Response(data=JobSerializerAdmin(job).data, status=HTTP_200_OK)

    @action(methods=['GET'], detail=True, url_name='companies-jobs')
    def get_all_job(self, request, slug, formate=None):
        profile_in_session = ProfileSession(request=request)
        is_logged_in_company = profile_in_session.is_logged_in_company()
        paginator = PageNumberPagination()
        paginator.page_size = 10
        # jobs = get_list_or_404(Job, company__slug=slug)
        jobs = Job.objects.filter(company__slug=slug)
        result_page = paginator.paginate_queryset(jobs, request)
        jobs_serializer = JobSerializerAdminNotDetails(result_page, many=True,
                                                       context={'is_admin': is_logged_in_company})
        return paginator.get_paginated_response(jobs_serializer.data)

    @action(methods=['GET'], detail=True, url_name='job-detail')
    def get_job_for_other(self, request, slug, job_slug, formate=None):

        profile_in_session = ProfileSession(request=request)
        if profile_in_session.is_logged_in_company():
            raise exceptions.PermissionDenied('You are not authorize')
        # job = get_object_or_404(Job, slug=job_slug, company__slug=slug)
        job = Job.objects.get(company__slug=slug, slug=job_slug)
        return Response(data=JobSerializer(job).data, status=HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def apply_for_job(self, request, slug, job_slug, formate=None):
        profile_in_session = ProfileSession(request=request)
        if profile_in_session.is_logged_in_company():
            raise exceptions.PermissionDenied('Company has no authorize to apply for jobs')
        job = Job.objects.get(company__slug=slug, slug=job_slug)
        profile = get_object_or_404(UsersProfile, auth_user=request.user)

        obj, created = job.applicants.get_or_create(
            user_profile=profile
        )

        return Response(status=HTTP_201_CREATED)

    @action(methods=['GET'], detail=True)
    def get_applied(self, request, slug, job_slug, formate=None):
        profile_in_session = ProfileSession(request=request).is_authorized_company()
        if not profile_in_session.user_profile.auth_user.username == request.user.username and \
                profile_in_session.slug == slug:
            raise exceptions.PermissionDenied('You are not authorize')

        paginator = PageNumberPagination()
        paginator.page_size = 10
        applicants_list = get_list_or_404(Applicants, job__slug=job_slug)
        result_page = paginator.paginate_queryset(applicants_list, request)
        applicants_serializer = ApplicantSerializer(instance=result_page, many=True)
        return paginator.get_paginated_response(applicants_serializer.data)

    @action(methods=['GET'], detail=True)
    def get_shortlisted(self, request, slug, job_slug, formate=None):
        profile_in_session = ProfileSession(request=request).is_authorized_company()
        if not profile_in_session.user_profile.auth_user.username == request.user.username and \
                profile_in_session.slug == slug:
            raise exceptions.PermissionDenied('You are not authorize')
        paginator = PageNumberPagination()
        paginator.page_size = 10
        applicants_list = get_list_or_404(Shortlisted, job__slug=job_slug)
        result_page = paginator.paginate_queryset(applicants_list, request)
        applicants_serializer = ApplicantSerializer(instance=result_page, many=True)
        return paginator.get_paginated_response(applicants_serializer.data)

    @action(methods=['GET'], detail=True)
    def get_interview(self, request, slug, job_slug, formate=None):
        profile_in_session = ProfileSession(request=request).is_authorized_company()
        if not profile_in_session.user_profile.auth_user.username == request.user.username and \
                profile_in_session.slug == slug:
            raise exceptions.PermissionDenied('You are not authorize')
        paginator = PageNumberPagination()
        paginator.page_size = 10
        applicants_list = get_list_or_404(JobSchedules, job__slug=job_slug)
        result_page = paginator.paginate_queryset(applicants_list, request)
        interview_serializer = InterviewSerializer(instance=result_page, many=True)
        return paginator.get_paginated_response(interview_serializer.data)

    @action(methods=['POST'], detail=True)
    def shortlist(self, request, slug, job_slug, user_slug, formate=None):
        profile_in_session = ProfileSession(request=request).is_authorized_company()
        if not profile_in_session.user_profile.auth_user.username == request.user.username and \
                profile_in_session.slug == slug:
            raise exceptions.PermissionDenied('You are not authorize')
        job = get_object_or_404(Job, slug=job_slug, company__slug=slug)
        get_object_or_404(Applicants, job=job, user_profile__slug=user_slug)
        profile = get_object_or_404(UsersProfile, slug=user_slug)
        obj, created = job.shortlisted.get_or_create(
            user_profile=profile
        )
        if created:
            Applicants.objects.filter(job=job, user_profile=profile).delete()

        return Response(status=HTTP_201_CREATED)

    @action(methods=['POST'], detail=True)
    def unshortlist(self, request, slug, job_slug, user_slug, formate=None):
        profile_in_session = ProfileSession(request=request).is_authorized_company()
        if not profile_in_session.user_profile.auth_user.username == request.user.username and \
                profile_in_session.slug == slug:
            raise exceptions.PermissionDenied('You are not authorize')
        job = get_object_or_404(Job, slug=job_slug, company__slug=slug)
        shortlist_obj = get_object_or_404(Shortlisted, job=job, user_profile__slug=user_slug)
        shortlist_obj.delete()
        return Response(status=HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def interview(self, request, slug, job_slug, user_slug, formate=None):
        profile_in_session = ProfileSession(request=request).is_authorized_company()
        if not profile_in_session.user_profile.auth_user.username == request.user.username and \
                profile_in_session.slug == slug:
            raise exceptions.PermissionDenied('You are not authorize')
        profile = get_object_or_404(UsersProfile, slug=user_slug)
        job = get_object_or_404(Job, slug=job_slug, company__slug=slug)
        get_object_or_404(Shortlisted, job=job, user_profile__slug=user_slug)

        interview_serializer = InterviewSerializer(data=request.data)
        interview_serializer.is_valid(raise_exception=True)

        obj, created = job.interviews.get_or_create(
            user_profile=profile,
            job=job,
            interview_date=request.data['interview_date'],
            interviewer=request.data['interviewer'],
            location=request.data['location']

        )

        if created:
            Shortlisted.objects.filter(job=job, user_profile=profile).delete()

        return Response(data=InterviewSerializer(obj).data, status=HTTP_201_CREATED)

    @action(methods=['GET'], detail=True)
    def get_my_applied(self, request):

        paginator = PageNumberPagination()
        paginator.page_size = 10
        # jobs = get_list_or_404(Job, company__slug=slug)
        applied = Applicants.objects.filter(user_profile__auth_user=request.user)
        jobs = Job.objects.filter(pk__in=[x.job.pk for x in applied])
        if request.GET.get('title', None):
            jobs.filter(title__contains=request.GET['title'])
        result_page = paginator.paginate_queryset(jobs, request)
        jobs_serializer = JobSerializerAdminNotDetails(result_page, many=True, context={'is_admin': False})
        return paginator.get_paginated_response(jobs_serializer.data)

    @action(methods=['GET'], detail=True)
    def get_my_created_job(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        # jobs = get_list_or_404(Job, company__slug=slug)
        jobs = Job.objects.filter(company__user_profile__auth_user=request.user)
        if request.GET.get('title', None):
            jobs.filter(title__contains=request.GET['title'])
        result_page = paginator.paginate_queryset(jobs, request)
        jobs_serializer = JobSerializerAdminNotDetails(result_page, many=True, context={'is_admin': True})
        return paginator.get_paginated_response(jobs_serializer.data)


class RandomJobs(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, formate=None):
        jobs = Job.objects.all().order_by("?")[:6]
        jobs_serializer = JobSerializerAdminNotDetails(jobs, many=True, context={'is_admin': False})
        return Response(data=jobs_serializer.data, status=HTTP_200_OK)
