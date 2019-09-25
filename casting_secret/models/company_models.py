from django.db import models
from django_elasticsearch_dsl_drf.wrappers import dict_to_obj

from CastingSecret.settings.base import MANAGED
from casting_secret.models.models import TalentCategories
from casting_secret.models.profile_models import UsersProfile


class Company(models.Model):
    avatar = models.CharField(max_length=150, null=True)
    cover = models.CharField(max_length=150, null=True)
    name = models.CharField(max_length=150, null=False)
    about = models.TextField(null=True)
    headquarter = models.TextField(null=True)
    is_address_public = models.BooleanField(default=True, null=False)
    website = models.URLField(null=True)
    since = models.TextField(max_length=4, null=True)
    size_from = models.IntegerField(null=True)
    size_to = models.IntegerField(null=True)
    # category = models.ForeignKey(TalentCategories, related_name='company_category', on_delete=models.CASCADE,
    #                              db_column='category_id')
    user_profile = models.ForeignKey(UsersProfile, related_name='profile_company', db_column='profile_id',
                                     db_index=True,
                                     on_delete=models.CASCADE)
    slug = models.SlugField(null=False, db_index=True)

    @property
    def tag_field_indexing(self):
        wrapper = []
        if self.tags.all():
            for x in self.tags.all():
                wrapper.append(dict_to_obj({
                    'id': x.id,
                    'name': x.category.name_en
                }))
        return wrapper

    @property
    def create_field_indexing(self):
        return dict_to_obj({
            'id': self.user_profile.auth_user.pk,
        })

    class Meta:
        managed = MANAGED
        db_table = 'company'


class CompanyTags(models.Model):
    category = models.ForeignKey(TalentCategories, related_name='company_category', on_delete=models.CASCADE,
                                 db_column='category_id')

    company = models.ForeignKey(Company, related_name='tags',
                                db_column='company_id',
                                db_index=True, on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'company_tags'
