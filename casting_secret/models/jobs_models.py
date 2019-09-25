import cloudinary
import django
from django.db import models
from django.utils.text import slugify

from CastingSecret.settings.base import MANAGED
from casting_secret.models import UsersProfile, TalentCategories, Company, dict_to_obj


class Job(models.Model):
    publish_date = models.DateTimeField(default=django.utils.timezone.now)
    title = models.CharField(max_length=250, null=False, unique=True)
    description = models.TextField(null=False)
    have_daily_perks = models.BooleanField(default=False)
    daily_perks_budget = models.DecimalField(max_digits=7, decimal_places=2)
    have_transportation = models.BooleanField(default=False)
    transportation_budget = models.DecimalField(max_digits=7, decimal_places=2)
    have_meal = models.BooleanField(default=False)
    meal_budget = models.DecimalField(max_digits=7, decimal_places=2)
    have_space_rest = models.BooleanField(default=False)
    space_rest_budget = models.DecimalField(max_digits=7, decimal_places=2)
    is_male = models.BooleanField(default=False)
    is_female = models.BooleanField(default=False)
    age = models.IntegerField(null=True)
    hide_company = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    longitude = models.DecimalField(max_digits=7, decimal_places=2, null=True)

    company = models.ForeignKey(Company, related_name='company_jobs', db_column='profile_id',
                                db_index=True,
                                on_delete=models.CASCADE)
    slug = models.SlugField(null=False, db_index=True, unique=True, allow_unicode=True)

    @property
    def tag_field_indexing(self):
        wrapper = []
        try:
            if self.job_category.all():
                for x in self.job_category.all():
                    wrapper.append(dict_to_obj({
                        'id': x.id,
                        'name': x.job_categories.name_en
                    }))
            return wrapper
        except:
            return wrapper

    @property
    def company_indexing(self):
        wrapper = dict_to_obj(
            {
                'name': self.company.name,
                'avatar': self.company.avatar,
                'slug': self.company.slug,
                'pk': self.company.pk
            }
        )
        return wrapper

    @property
    def get_avatar_path(self):
        if self.company.avatar:
            try:
                return cloudinary.api.resource(self.company.avatar)
            except:
                return None
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify('%s %s %s' % (self.title, self.company.user_profile.auth_user.id, self.company.pk),
                                allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        managed = MANAGED
        db_table = 'jobs'


class JobCategory(models.Model):
    job = models.ForeignKey(Job, related_name='job_category', db_column='job_id',
                            db_index=True,
                            on_delete=models.CASCADE)
    job_categories = models.ForeignKey(TalentCategories, related_name='job_categories',
                                       db_column='job_category_id', on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'job_category'


class Applicants(models.Model):
    applied_date = models.DateTimeField(default=django.utils.timezone.now)
    user_profile = models.ForeignKey(UsersProfile, related_name='applicant_applied_jobs', db_column='profile_id',
                                     db_index=True,
                                     on_delete=models.CASCADE)
    job = models.ForeignKey(Job, related_name='applicants', db_column='job_id',
                            db_index=True,
                            on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'job_applicants'


class Shortlisted(models.Model):
    shortlisted_date = models.DateTimeField(default=django.utils.timezone.now)
    user_profile = models.ForeignKey(UsersProfile, related_name='applicant_shortlisted_jobs', db_column='profile_id',
                                     db_index=True,
                                     on_delete=models.CASCADE)
    job = models.ForeignKey(Job, related_name='shortlisted', db_column='job_id',
                            db_index=True,
                            on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'job_shortlisted'


class JobSchedules(models.Model):
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    user_profile = models.ForeignKey(UsersProfile, related_name='interview_applicants', db_column='profile_id',
                                     db_index=True,
                                     on_delete=models.CASCADE)
    job = models.ForeignKey(Job, related_name='interviews', db_column='job_id',
                            db_index=True,
                            on_delete=models.CASCADE)
    interview_date = models.DateTimeField()
    interviewer = models.CharField(max_length=150, null=False)
    location = models.TextField(null=False)

    class Meta:
        managed = MANAGED
        db_table = 'job_schedules'
        ordering = ['interview_date']
