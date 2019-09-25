from django.conf import settings
from django_elasticsearch_dsl import Index, fields, KeywordField
from django_elasticsearch_dsl.documents import DocType
from django_elasticsearch_dsl_drf.compat import StringField
from elasticsearch_dsl import analyzer

# Name of the Elasticsearch index
from casting_secret.models import Company

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
class CompanyDocument(DocType):
    # ID
    id = fields.IntegerField(attr='id')
    avatar = fields.TextField()
    slug = fields.StringField()
    name = StringField(analyzer=html_strip,
                       fields={
                           'raw': KeywordField(),
                       })

    about = fields.TextField()
    headquarter = fields.TextField()
    is_address_public = fields.BooleanField()
    website = fields.StringField()
    since = fields.StringField()
    size_from = fields.IntegerField()
    size_to = fields.IntegerField()
    creator = fields.ObjectField(
        attr='create_field_indexing',
        properties={
            'id': fields.IntegerField()
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
        model = Company
