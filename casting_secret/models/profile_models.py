import django
from django.contrib.auth.models import User
from django.db import models
from django_elasticsearch_dsl_drf.wrappers import dict_to_obj

from CastingSecret.settings.base import MANAGED
from casting_secret.models.models import TalentCategories


class AgeRangeLookUp(models.Model):
    name = models.CharField(max_length=50, null=True, unique=True)

    class Meta:
        managed = MANAGED
        db_table = 'age_range_lookup'

    def __str__(self):
        return self.name


class HeightRangeLookUp(models.Model):
    name = models.CharField(max_length=50, null=True, unique=True)

    class Meta:
        managed = MANAGED
        db_table = 'height_range_lookup'

    def __str__(self):
        return self.name


class WeightRangeLookUp(models.Model):
    name = models.CharField(max_length=50, null=True, unique=True)

    class Meta:
        managed = MANAGED
        db_table = 'weight_range_lookup'

    def __str__(self):
        return self.name


class BuildLookUp(models.Model):
    name = models.CharField(max_length=50, null=True, unique=True)

    class Meta:
        managed = MANAGED
        db_table = 'build_lookup'

    def __str__(self):
        return self.name


class HairLookUp(models.Model):
    name = models.CharField(max_length=50, null=True, unique=True)

    class Meta:
        managed = MANAGED
        db_table = 'hair_lookup'

    def __str__(self):
        return self.name


class EyesLookUp(models.Model):
    name = models.CharField(max_length=50, null=True, unique=True)

    class Meta:
        managed = MANAGED
        db_table = 'eye_lookup'

    def __str__(self):
        return self.name


class EthnicitiesLookUp(models.Model):
    name = models.CharField(max_length=150, null=True, unique=True)

    class Meta:
        managed = MANAGED
        db_table = 'ethnicities_lookup'

    def __str__(self):
        return self.name


class HobbiesLookUp(models.Model):
    name = models.CharField(max_length=150, null=True, unique=True)

    class Meta:
        managed = MANAGED
        db_table = 'hobbies_lookup'

    def __str__(self):
        return self.name


class UsersProfile(models.Model):
    auth_user = models.ForeignKey(User, related_name='auth_user_profile', db_column='auth_user_id', db_index=True,
                                  on_delete=models.CASCADE)
    avatar = models.CharField(max_length=150, null=True)
    cover = models.CharField(max_length=150, null=True)
    gender = models.CharField(max_length=50, null=True)
    location = models.CharField(max_length=150, null=True)
    about = models.TextField(null=True)
    phone = models.CharField(max_length=50, null=True, unique=True)
    slug = models.SlugField(null=False, db_index=True)
    age_from = models.IntegerField(default=0, null=True)
    age_to = models.IntegerField(default=0, null=True)
    height = models.ForeignKey(HeightRangeLookUp, related_name='profile_height', db_index=True, db_column='height_id',
                               null=True, on_delete=models.CASCADE)
    weight = models.ForeignKey(WeightRangeLookUp, related_name='profile_weight', db_index=True, db_column='weight_id',
                               null=True, on_delete=models.CASCADE)
    build = models.ForeignKey(BuildLookUp, related_name='profile_build', db_index=True, db_column='build_id', null=True
                              , on_delete=models.CASCADE)
    hair = models.ForeignKey(HairLookUp, related_name='profile_hair', db_index=True, db_column='hair_id', null=True
                             , on_delete=models.CASCADE)
    eye = models.ForeignKey(EyesLookUp, related_name='profile_eye', db_index=True, db_column='eye_id', null=True
                            , on_delete=models.CASCADE)
    ethnicity = models.ForeignKey(EthnicitiesLookUp, related_name='profile_ethnicity', db_index=True,
                                  db_column='ethnicity_id', null=True, on_delete=models.CASCADE)

    @property
    def auth_user_field_indexing(self):
        wrapper = dict_to_obj(
            {
                'first_name': self.auth_user.first_name,
                'last_name': self.auth_user.last_name,
                'username': self.auth_user.username,
            }
        )
        return wrapper

    @property
    def media_field_indexing(self):
        wrapper = dict_to_obj(
            {
                'has_photo': self.auth_user.auth_user_activity_video.filter(type='IMG').exists(),
                'has_video': self.auth_user.auth_user_activity_video.filter(type='VIDEO').exists(),
                'has_audio': self.auth_user.auth_user_activity_video.filter(type='AUDIO').exists(),
            }
        )
        return wrapper

    @property
    def height_field_indexing(self):
        wrapper = {}

        if self.height:
            wrapper = dict_to_obj({
                'id': self.height.pk,
                'name': self.height.name
            })
        return wrapper

    @property
    def weight_field_indexing(self):
        wrapper = {}
        if self.weight:
            wrapper = dict_to_obj({
                'id': self.weight.pk,
                'name': self.weight.name
            })
        return wrapper

    @property
    def build_field_indexing(self):
        wrapper = {}
        if self.build:
            wrapper = dict_to_obj({
                'id': self.build.pk,
                'name': self.build.name
            })
        return wrapper

    @property
    def hair_field_indexing(self):
        wrapper = {}

        if self.hair:
            wrapper = dict_to_obj({
                'id': self.hair.pk,
                'name': self.hair.name
            })
        return wrapper

    @property
    def eye_field_indexing(self):
        wrapper = {}
        if self.eye:
            wrapper = dict_to_obj({
                'id': self.eye.pk,
                'name': self.eye.name
            })
        return wrapper

    @property
    def ethnicity_field_indexing(self):
        wrapper = {}
        if self.ethnicity:
            wrapper = dict_to_obj({
                'id': self.ethnicity.pk,
                'name': self.ethnicity.name
            })
        return wrapper

    @property
    def tag_field_indexing(self):
        wrapper = []
        if self.users_profile_categories.all():
            for x in self.users_profile_categories.all():
                wrapper.append(dict_to_obj({
                    'id': x.pk,
                    'name': x.talent_categories.name_en
                }))
        return wrapper

    @property
    def applied_job(self):
        return self.applicant_applied_jobs.count()

    class Meta:
        managed = MANAGED
        db_table = 'users_profile'
        verbose_name = 'Users profile'

    def __str__(self):
        return "This profile is for %s" % self.auth_user


class UsersProfileTalentCategories(models.Model):
    user_profile = models.ForeignKey(UsersProfile, related_name='users_profile_categories', db_column='user_profile_id',
                                     db_index=True, on_delete=models.CASCADE)
    talent_categories = models.ForeignKey(TalentCategories, related_name='talent_categories',
                                          db_column='talent_category_id', on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'users_profile_categories'
        unique_together = ['user_profile', 'talent_categories']

    def __str__(self):
        return self.user_profile


class ProfileSocialLinks(models.Model):
    user_profile = models.ForeignKey(UsersProfile, related_name='users_profile_social', db_column='user_profile_id',
                                     db_index=True, on_delete=models.CASCADE)
    network = models.CharField(max_length=50, null=True)
    url = models.URLField(null=True, unique=True)

    class Meta:
        managed = MANAGED
        db_table = 'profile_social_networks'

    def __str__(self):
        return self.user_profile


class ProfileHobbies(models.Model):
    # custom = models.CharField(max_length=50, null=False)
    hobbies = models.ForeignKey(HobbiesLookUp, related_name='hobbies', db_column='hobbies_id', db_index=True,
                                on_delete=models.CASCADE, null=False)
    user_profile = models.ForeignKey(UsersProfile, related_name='users_profile_hobbies', db_column='user_profile_id',
                                     db_index=True, on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'profile_hobbies'
        unique_together = ['hobbies', 'user_profile']

    def __str__(self):
        return self.user_profile


class ProfileTraining(models.Model):
    course_name = models.CharField(max_length=150, null=False)
    institute = models.CharField(max_length=150, null=False)
    user_profile = models.ForeignKey(UsersProfile, related_name='users_profile_courses', db_column='user_profile_id',
                                     db_index=True, on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'profile_training'
        unique_together = ['course_name', 'institute', 'user_profile']

    def __str__(self):
        return self.user_profile


class Albums(models.Model):
    publish_date = models.DateTimeField(default=django.utils.timezone.now)
    album_name = models.CharField(max_length=150, null=False)
    user_profile = models.ForeignKey(UsersProfile, related_name='users_profile_album', db_column='user_profile_id',
                                     db_index=True, on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'profile_album'
        unique_together = ['album_name', 'user_profile']

    def __str__(self):
        return self.user_profile


class ProfileSettings(models.Model):
    STATUSES = (
        (u'ALL', u'ALL'),
        (u'ONLY_FRIENDS', u'ONLY_FRIENDS'),
        (u'COMPANY', u'COMPANY'),
    )

    ONLINE_STATUS = (
        (u'OFFLINE', u'OFFLINE'),
        (u'ONLINE', u'ONLINE'),
    )

    can_see_profile = models.CharField(max_length=50, null=True, blank=True, choices=STATUSES, default='ALL')
    can_see_wall = models.CharField(max_length=50, null=True, blank=True, choices=STATUSES, default='ALL')
    can_comment = models.CharField(max_length=50, null=True, blank=True, choices=STATUSES, default='ALL')
    can_contact_info = models.CharField(max_length=50, null=True, blank=True, choices=STATUSES, default='ALL')
    can_see_friends = models.CharField(max_length=50, null=True, blank=True, choices=STATUSES, default='ALL')
    can_send_message = models.CharField(max_length=50, null=True, blank=True, choices=STATUSES, default='ALL')
    my_status = models.CharField(max_length=50, null=True, blank=True, choices=ONLINE_STATUS, default='ONLINE')
    response_all_time = models.BooleanField(default=False)
    response_from = models.DateTimeField(null=True)
    response_to = models.DateTimeField(null=True)
    response_message = models.TextField(null=True)
    auto_play_video = models.BooleanField(default=False)
    jobs_notification = models.BooleanField(default=False)
    user_profile = models.ForeignKey(UsersProfile, on_delete=models.CASCADE, related_name='profile_settings',
                                     db_column='user_profile_id')

    class Meta:
        managed = MANAGED
        db_table = 'profile_settings'
        verbose_name = "Profile Setting"
        verbose_name_plural = "Profile Settings"


class ProfileViewers(models.Model):
    user_profile = models.ForeignKey(UsersProfile, on_delete=models.CASCADE, related_name='profile_viewers',
                                     db_column='user_profile_id')
    visitor_profile = models.ForeignKey(UsersProfile, on_delete=models.CASCADE,
                                        db_column='visitor_profile_id', null=True)

    class Meta:
        managed = MANAGED
        db_table = 'profile_viewers'

    def __str__(self):
        return self.user_profile + "has visited " + self.visitor_profile
