from django.conf import settings
from django_elasticsearch_dsl import Index, fields, KeywordField
from django_elasticsearch_dsl.documents import DocType
from django_elasticsearch_dsl_drf.compat import StringField
from elasticsearch_dsl import analyzer

from casting_secret.models import Job

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
class JobDocument(DocType):
    # ID
    id = fields.IntegerField(attr='id')
    title = StringField(analyzer=html_strip, fields={
        'raw': KeywordField(),
    })
    description = fields.TextField()
    have_daily_perks = fields.BooleanField()
    daily_perks_budget = fields.DoubleField()
    have_transportation = fields.BooleanField()
    transportation_budget = fields.DoubleField()
    have_meal = fields.BooleanField()
    meal_budget = fields.DoubleField()
    have_space_rest = fields.BooleanField()
    space_rest_budget = fields.DoubleField()
    is_male = fields.BooleanField()
    is_female = fields.BooleanField()
    age = fields.IntegerField()
    hide_company = fields.BooleanField()
    latitude = fields.GeoPointField()
    longitude = fields.GeoPointField()
    slug = fields.StringField()
    publish_date = fields.DateField()

    tags = fields.ObjectField(
        attr='tag_field_indexing',
        properties={
            'id': fields.IntegerField(),
            'name': fields.StringField()

        }
    )

    company = fields.ObjectField(
        attr='company_indexing',
        properties={
            'name': fields.StringField(),
            'avatar': fields.StringField(),
            'slug': fields.StringField(),
            'pk': fields.IntegerField()
        }
    )

    class Django:
        model = Job
