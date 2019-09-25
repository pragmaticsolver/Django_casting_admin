from django_elasticsearch_dsl_drf.constants import LOOKUP_FILTER_RANGE, LOOKUP_QUERY_IN
from django_elasticsearch_dsl_drf.filter_backends import FilteringFilterBackend, \
    SearchFilterBackend, OrderingFilterBackend, \
    DefaultOrderingFilterBackend
from django_elasticsearch_dsl_drf.pagination import LimitOffsetPagination
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet

from casting_secret.search_indexes.documents.company import CompanyDocument
from casting_secret.search_indexes.documents.job import JobDocument
from casting_secret.search_indexes.documents.profile import ProfileDocument
from casting_secret.search_indexes.serializers.SearchSerializer import SearchProfileSerializer, SearchCompanySerializer, \
    SearchJobSerializer


class UserDocumentViewSet(DocumentViewSet):
    document = ProfileDocument
    serializer_class = SearchProfileSerializer
    lookup_field = 'id'
    filter_backends = [
        # FacetedSearchFilterBackend,
        FilteringFilterBackend,
        OrderingFilterBackend,
        SearchFilterBackend,
        # GeoSpatialFilteringFilterBackend,
        # GeoSpatialOrderingFilterBackend,
        # NestedFilteringFilterBackend,
        DefaultOrderingFilterBackend,
        # SuggesterFilterBackend,
    ]
    pagination_class = LimitOffsetPagination

    # Define search fields
    search_fields = (
        'auth_user.username',
        'auth_user.last_name',
        'auth_user.first_name',

    )

    # Define filtering fields
    filter_fields = {
        # 'id': None,
        # 'location': 'location',
        'gender': 'gender',
        # 'age': {
        #     'field': 'age',
        #     'lookups': [
        #         LOOKUP_FILTER_RANGE,
        #     ],
        # },
        'fname': 'auth_user.first_name.raw',
        'lname': 'auth_user.last_name.raw',
        'username': 'auth_user.username.raw',
        'has_photo': 'media.has_photo',
        'has_video': 'media.has_video',
        'has_audio': 'media.has_audio',
        'build': 'build.id',
        'height': 'height.id',
        'weight': 'weight.id',
        'hair': 'hair.id',
        'eye': 'eye.id',
        'ethnicity': 'ethnicity.id',

        'tags': {
            'field': 'tags.id',
            'lookups': [
                LOOKUP_QUERY_IN,
            ],
        },

    }

    # Define ordering fields
    ordering_fields = {
        'id': 'id',
        'first_name': 'auth_user.first_name.raw',

    }
    # Specify default ordering
    ordering = ('id', 'first_name',)


class CompanyDocumentViewSet(DocumentViewSet):
    document = CompanyDocument
    serializer_class = SearchCompanySerializer
    lookup_field = 'id'
    filter_backends = [
        # FacetedSearchFilterBackend,
        FilteringFilterBackend,
        OrderingFilterBackend,
        SearchFilterBackend,
        # GeoSpatialFilteringFilterBackend,
        # GeoSpatialOrderingFilterBackend,
        # NestedFilteringFilterBackend,
        DefaultOrderingFilterBackend,
        # SuggesterFilterBackend,
    ]
    pagination_class = LimitOffsetPagination

    # Define search fields
    search_fields = (
        'name',

    )

    # Define filtering fields
    filter_fields = {
        'id': None,
        'size_from': {
            'field': 'size_from',
            'lookups': [
                LOOKUP_FILTER_RANGE,
            ],
        },
        'size_to': {
            'field': 'size_from',
            'lookups': [
                LOOKUP_FILTER_RANGE,
            ],
        },
        'tags': {
            'field': 'tags.id',
            'lookups': [
                LOOKUP_QUERY_IN,
            ],
        },

        'creator': {
            'field': 'creator.id',
            'lookups': [
                LOOKUP_QUERY_IN,
            ],
        }

    }

    # Define ordering fields
    ordering_fields = {
        'name': 'name',

    }

    # Specify default ordering
    ordering = ('id', 'name',)


class JobDocumentViewSet(DocumentViewSet):
    document = JobDocument
    serializer_class = SearchJobSerializer
    lookup_field = 'id'
    filter_backends = [
        # FacetedSearchFilterBackend,
        FilteringFilterBackend,
        OrderingFilterBackend,
        SearchFilterBackend,
        # GeoSpatialFilteringFilterBackend,
        # GeoSpatialOrderingFilterBackend,
        # NestedFilteringFilterBackend,
        DefaultOrderingFilterBackend,
        # SuggesterFilterBackend,
    ]
    pagination_class = LimitOffsetPagination

    # Define search fields
    search_fields = (
        'title',
    )

    # Define filtering fields
    filter_fields = {
        'id': None,
        'male': 'is_male',
        'female': 'is_female',
        'tags': {
            'field': 'tags.id',
            'lookups': [
                LOOKUP_QUERY_IN,
            ],
        },
        'title': 'title',
        'company': {
            'field': 'company.id',
            'lookups': [
                LOOKUP_QUERY_IN,
            ],
        }

    }

    # Define ordering fields
    ordering_fields = {
        'title': 'title',

    }

    # Specify default ordering
    ordering = ('id', 'title',)
