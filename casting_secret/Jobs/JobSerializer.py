from rest_framework import serializers

from casting_secret.models import Job, JobCategory, Applicants, Shortlisted, JobSchedules
from casting_secret.serializers.common_serializers import TalentCategoriesSerializer
from casting_secret.user_profile.serializers import UserProfileSerializer


class JobCategorySerializer(serializers.ModelSerializer):
    job_categories = TalentCategoriesSerializer(read_only=True)

    class Meta:
        model = JobCategory
        fields = ('job_categories',)


class ApplicantSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = Applicants
        exclude = ('job',)


class ShortlistedSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = Shortlisted
        exclude = ('job',)


class InterviewSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = JobSchedules
        exclude = ('job',)
        read_only_fields = ('user_profile',)


class JobSerializer(serializers.ModelSerializer):
    job_category = JobCategorySerializer(many=True, read_only=True)
    is_applied_before = serializers.SerializerMethodField()

    def is_applied_before(self, obj):
        return obj.applicants.filter(user_profile__auth_user=self.context['request'].user).exists()

    def to_representation(self, obj):
        ret = super(JobSerializer, self).to_representation(obj)
        if obj.hide_company:
            ret.pop('company')

        return ret

    class Meta:
        model = Job
        exclude = ('company', 'slug')


class JobSerializerAdmin(serializers.ModelSerializer):
    job_category = JobCategorySerializer(many=True, read_only=True)

    # applicants = ApplicantSerializer(many=True, read_only=True)
    # shortlisted = ShortlistedSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        exclude = ('company', 'slug')


class JobSerializerAdminNotDetails(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()
    job_category = JobCategorySerializer(many=True, read_only=True)

    def is_admin(self):
        return self.context['is_admin']

    class Meta:
        model = Job
        exclude = ('company',)
