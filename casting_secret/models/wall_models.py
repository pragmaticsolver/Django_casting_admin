import django
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from casting_secret.models import Company, MANAGED
from casting_secret.models.profile_models import Albums


class Activity(models.Model):
    auth_user = models.ForeignKey(User, related_name='auth_user_activity', db_index=True, db_column='auth_user_id',
                                  on_delete=models.CASCADE)
    content = models.TextField(null=True)
    publish_date = models.DateTimeField(default=django.utils.timezone.now)
    blocked = models.BooleanField(default=False, db_column='is_blocked')
    action = models.CharField(max_length=150, null=True)
    is_active = models.BooleanField(default=True)
    original_activity = models.ForeignKey('self', related_name='original_post', db_column='original_activity',
                                          null=True, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name='company_activity', db_index=True, db_column='company_id',
                                on_delete=models.CASCADE, null=True, default=None)

    @property
    def comments_count(self):
        return self.activity_comment.count()

    @property
    def share_count(self):
        return self.activity_action.filter(has_share=True).count()

    @property
    def like_count(self):
        return self.activity_action.filter(has_like=True).count()

    @property
    def dislike_count(self):
        return self.activity_action.filter(has_dislike=True).count()

    @property
    def marked_as_saved(self):
        return self.activity_control.filter(is_saved=True).exists()

    def get_absolute_url(self):
        return reverse('activity_view_post', kwargs={'pk': self.pk})

    class Meta:
        managed = MANAGED
        db_table = 'activity'
        ordering = ['-publish_date']


class Comments(models.Model):
    comment = models.TextField(null=False)
    publish_date = models.DateTimeField(default=django.utils.timezone.now)
    thread = models.ForeignKey('self', related_name='comment_thread', db_column='thread_id', null=True,
                               on_delete=models.CASCADE)
    auth_user = models.ForeignKey(User, related_name='auth_user_comments', db_index=True, db_column='auth_user_id',
                                  on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, related_name='activity_comment', db_column='activity_id', db_index=True,
                                 on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'comments'
        ordering = ['-publish_date']


class ActivitySocialAction(models.Model):
    publish_date = models.DateTimeField(default=django.utils.timezone.now)
    has_like = models.BooleanField(default=False, db_index=True)
    has_dislike = models.BooleanField(default=False, db_index=True)
    has_share = models.BooleanField(default=False, db_index=True)
    auth_user = models.ForeignKey(User, related_name='auth_user_activity_action', db_index=True,
                                  db_column='auth_user_id', on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, related_name='activity_action', db_column='activity_id', db_index=True,
                                 on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'activity_social_actions'
        ordering = ['-publish_date']


class ActivityControl(models.Model):
    publish_date = models.DateTimeField(default=django.utils.timezone.now)
    is_hidden = models.BooleanField(default=False)
    is_saved = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)
    activity = models.ForeignKey(Activity, related_name='activity_control', db_column='activity_id', db_index=True,
                                 on_delete=models.CASCADE)
    auth_user = models.ForeignKey(User, related_name='auth_user_activity_control', db_index=True,
                                  db_column='auth_user_id', on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'activity_control'
        # unique_together = ['is_reported', 'auth_user']


class ActivityAttachment(models.Model):
    publish_date = models.DateTimeField(default=django.utils.timezone.now)
    # path = models.FileField(upload_to=settings.ACTIVITY_ATTACHMENT, null=False, validators=[
    #     FileExtensionValidator(allowed_extensions=['jpeg', 'png', 'gif', 'tiff', 'mp4', 'mp3'])])
    path = models.TextField(null=True)
    type = models.CharField(max_length=25, null=False, default='IMG')
    activity = models.ForeignKey(Activity, related_name='activity_attachment', db_column='activity_id', db_index=True,
                                 on_delete=models.CASCADE)
    auth_user = models.ForeignKey(User, related_name='auth_user_activity_video', db_index=True,
                                  db_column='auth_user_id', on_delete=models.CASCADE)

    album = models.ForeignKey(Albums, related_name='auth_user_album', db_index=True,
                              db_column='album_id', on_delete=models.CASCADE, null=True)

    path_json = models.CharField(max_length=150, null=False)

    # def get_absolute_url(self):
    #     return reverse('media', kwargs={'path': self.path.url})

    # @property
    # def get_path(self):
    #     if self.path:
    #         try:
    #             return self.path['secure_url']
    #         except:
    #             return None
    #     return None

    class Meta:
        managed = MANAGED
        db_table = 'activity_attachment'


class ActivityBookmark(models.Model):
    publish_date = models.DateTimeField(default=django.utils.timezone.now)
    activity = models.ForeignKey(Activity, related_name='activity_bookmark', db_column='activity_id', db_index=True,
                                 on_delete=models.CASCADE)
    auth_user = models.ForeignKey(User, related_name='auth_user_activity_bookmark', db_index=True,
                                  db_column='auth_user_id', on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'activity_bookmark'


class ActivityReport(models.Model):
    publish_date = models.DateTimeField(default=django.utils.timezone.now)
    activity = models.ForeignKey(Activity, related_name='activity_report', db_column='activity_id', db_index=True,
                                 on_delete=models.CASCADE)
    auth_user = models.ForeignKey(User, related_name='auth_user_activity_report', db_index=True,
                                  db_column='auth_user_id', on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'activity_report'


class ActivityIgnore(models.Model):
    publish_date = models.DateTimeField(default=django.utils.timezone.now)
    activity = models.ForeignKey(Activity, related_name='activity_ignore', db_column='activity_id', db_index=True,
                                 on_delete=models.CASCADE)
    auth_user = models.ForeignKey(User, related_name='auth_user_activity_ignore', db_index=True,
                                  db_column='auth_user_id', on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'activity_ignore'


class CommentMention(models.Model):
    publish_date = models.DateTimeField(default=django.utils.timezone.now)
    auth_user = models.ForeignKey(User, related_name='auth_user_comment_mention', db_index=True,
                                  db_column='auth_user_id', on_delete=models.CASCADE)
    comment = models.ForeignKey(Comments, related_name='comment_mention', db_column='comment_id', db_index=True,
                                on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'comment_mention'
        ordering = ['pk']


class ActivityMention(models.Model):
    publish_date = models.DateTimeField(default=django.utils.timezone.now)
    auth_user = models.ForeignKey(User, related_name='auth_user_activity_mention', db_index=True,
                                  db_column='auth_user_id', on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, related_name='activity_mention', db_column='activity_id', db_index=True,
                                 on_delete=models.CASCADE)

    class Meta:
        managed = MANAGED
        db_table = 'activity_mention'
        ordering = ['pk']
