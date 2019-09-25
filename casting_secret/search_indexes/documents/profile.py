from django.conf import settings
from django_elasticsearch_dsl import Index, fields, KeywordField
from django_elasticsearch_dsl.documents import DocType
from django_elasticsearch_dsl_drf.compat import StringField
from elasticsearch_dsl import analyzer

# Name of the Elasticsearch index
from casting_secret.models import UsersProfile

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])

# See Elasticsearch Indices API reference for available settings
INDEX.settings(
    number_of_shards=1,
    number_of_replicas=1
)

html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


@INDEX.doc_type
class ProfileDocument(DocType):
    # ID
    id = fields.IntegerField(attr='id')

    # ********************************************************************
    # *********************** Main data fields for search ****************
    # ********************************************************************

    gender = StringField(
        analyzer=html_strip,
        fields={
            'raw': KeywordField(),
        }
    )

    location = StringField(
        analyzer=html_strip,
        fields={
            'raw': KeywordField()
        }
    )
    avatar = fields.TextField()
    about = fields.TextField()
    phone = fields.StringField()
    slug = fields.StringField()
    # age = fields.IntegerField()

    height = fields.ObjectField(
        attr='height_field_indexing',
        properties={
            'name': StringField(
                analyzer=html_strip
            ),
            'id': fields.IntegerField()}
    )

    weight = fields.ObjectField(
        attr='weight_field_indexing',
        properties={
            'name': StringField(
                analyzer=html_strip
            ),
            'id': fields.IntegerField()}
    )

    build = fields.ObjectField(
        attr='build_field_indexing',
        properties={
            'name': StringField(
                analyzer=html_strip
            ),
            'id': fields.IntegerField()}
    )

    hair = fields.ObjectField(
        attr='hair_field_indexing',
        properties={
            'name': StringField(
                analyzer=html_strip
            ),
            'id': fields.IntegerField()}
    )

    eye = fields.ObjectField(
        attr='eye_field_indexing',
        properties={
            'name': StringField(
                analyzer=html_strip
            ),
            'id': fields.IntegerField()}
    )

    ethnicity = fields.ObjectField(
        attr='ethnicity_field_indexing',
        properties={
            'name': StringField(
                analyzer=html_strip
            ),
            'id': fields.IntegerField()}
    )

    auth_user_nested = fields.NestedField(
        attr='auth_user_field_indexing',
        properties={
            'first_name': StringField(
                analyzer=html_strip,
                fields={
                    'raw': KeywordField(),
                    'suggest': fields.CompletionField(),
                }
            ),
            'last_name': StringField(
                analyzer=html_strip,
                fields={
                    'raw': KeywordField(),
                    'suggest': fields.CompletionField(),
                }
            ),
            'username': StringField(
                analyzer=html_strip,
                fields={
                    'raw': KeywordField(),
                    'suggest': fields.CompletionField(),
                }
            )}
    )

    auth_user = fields.ObjectField(
        attr='auth_user_field_indexing',
        properties={
            'first_name': StringField(
                analyzer=html_strip,
                fields={
                    'raw': KeywordField(),
                    'suggest': fields.CompletionField(),
                }
            ),
            'last_name': StringField(
                analyzer=html_strip,
                fields={
                    'raw': KeywordField(),
                    'suggest': fields.CompletionField(),
                }
            ),
            'username': StringField(
                analyzer=html_strip,
                fields={
                    'raw': KeywordField(),
                    'suggest': fields.CompletionField(),
                }
            )}
    )

    media = fields.ObjectField(
        attr='media_field_indexing',
        properties={
            'has_photo': fields.BooleanField(),
            'has_video': fields.BooleanField(
            ),
            'has_audio': fields.BooleanField(
            ),

        }
    )

    tags = fields.ObjectField(
        attr='tag_field_indexing',
        properties={
            'id': fields.IntegerField(),
            'name': fields.StringField()

        }
    )

    class Django:
        model = UsersProfile
