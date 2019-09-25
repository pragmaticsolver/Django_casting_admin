import cloudinary
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers

from casting_secret.search_indexes.documents.company import CompanyDocument
from casting_secret.search_indexes.documents.job import JobDocument
from casting_secret.search_indexes.documents.profile import ProfileDocument


class SearchProfileSerializer(DocumentSerializer):
    """Serializer for address document."""

    avatar = serializers.SerializerMethodField('get_avatar_path')

    def get_avatar_path(self, obj):
        if obj.avatar:
            try:
                return cloudinary.api.resource(obj.avatar)
            except:
                return None
        return None

    class Meta(object):
        """Meta options."""

        document = ProfileDocument
        fields = (
            'id',
            'gender',
            'location',
            'avatar',
            'about',
            'phone',
            'slug',
            'age',
            'height',
            'weight',
            'build',
            'hair',
            'eye',
            'ethnicity',
            'auth_user',
            'media',
            'tags',
        )


class SearchCompanySerializer(DocumentSerializer):
    avatar = serializers.SerializerMethodField('get_avatar_path')

    def get_avatar_path(self, obj):
        if obj.avatar:
            try:
                return cloudinary.api.resource(obj.avatar)
            except:
                return None
        return None

    class Meta(object):
        document = CompanyDocument
        fields = (
            'id',
            'avatar',
            'slug',
            'about',
            'headquarter',
            'is_address_public',
            'website',
            'since',
            'size_from',
            'size_to',
            'tags',
            'name',)


class SearchJobSerializer(DocumentSerializer):
    class Meta(object):
        document = JobDocument
        fields = (
            'id',
            'title',
            'description',
            'have_daily_perks',
            'daily_perks_budget',
            'have_transportation',
            'transportation_budget',
            'have_meal',
            'meal_budget',
            'have_space_rest',
            'space_rest_budget',
            'is_male',
            'is_female',
            'age',
            'hide_company',
            'latitude',
            'longitude',
            'slug',
            'tags',
            'publish_date',
            'company'
        )
