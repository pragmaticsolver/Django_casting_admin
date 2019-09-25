from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from notify.signals import notify

from casting_secret.models import UsersProfile, ActivitySocialAction
from casting_secret.models.wall_models import ActivityReport, Activity, Comments, CommentMention, ActivityMention


@receiver(post_save, sender=ActivityReport)
def notify_admin_for_reported_activity(sender, instance, **kwargs):
    message = render_to_string('emails/notify_admin_for_report_activity.txt', context={'instance': instance})
    send_mail(subject=('Activity [%s] is reported '.format(instance.activity.pk)),
              from_email=None,
              recipient_list=[settings.SUPPORT],
              fail_silently=True,
              html_message=message)

    # get number for blocks
    count = ActivityReport.objects.filter(activity=instance.activity).count()
    if count >= settings.BLOCKED_POST_COUNTER:
        activity = instance.activity
        activity.blocked = True
        activity.save()


@receiver(post_save, sender=Activity)
def notify_activity_creator_for_blocking(sender, instance, **kwargs):
    if instance.blocked:
        message = render_to_string('emails/notify_user_activity_for_blocking.txt', context={'instance': instance})
        send_mail(subject=('Activity [%s] is reported '.format(instance.activity.pk)),
                  from_email=None,
                  recipient_list=[instance.auth_user.email],
                  fail_silently=True,
                  html_message=message)


@receiver(post_save, sender=Comments)
def notify_activity_comment(sender, instance, **kwargs):
    # send notification for activity creator
    activity_creator = None
    if instance.activity.company is not None:
        activity_creator = instance.activity.company.user_profile.auth_user
    if not activity_creator:
        activity_creator = instance.activity.auth_user

    notify.send(instance.auth_user,
                recipient=activity_creator,
                actor=instance.auth_user,
                target=instance.activity,
                verb='commented on you post', nf_type='comment_on_activity')

    rcp_list = instance.activity.activity_comment.all()
    # send notification to activity thread
    notify.send(instance.auth_user,
                recipient_list=[x.auth_user for x in rcp_list],
                actor=instance.auth_user,
                target=instance.activity,
                verb='commented on you post', nf_type='comment_on_activity')


@receiver(post_save, sender=CommentMention)
def comment_mention(sender, instance, **kwargs):
    notify.send(instance.comment.auth_user,
                recipient=instance.comment.auth_user,
                actor=instance.comment.auth_user,
                target=instance.comment.activity,
                verb='mention you on post', nf_type='mention_on_comment')


@receiver(post_save, sender=ActivityMention)
def post_mention(sender, instance, **kwargs):
    sender = instance.activity.company
    if not sender:
        sender = instance.activity.auth_user

    notify.send(sender,
                recipient=instance.auth_user,
                actor=sender,
                target=instance.activity,
                verb='mention you on post', nf_type='mention_on_post')


@receiver(post_save, sender=ActivitySocialAction)
def post_action(sender, instance, **kwargs):
    rcpt = instance.activity.company
    if not rcpt:
        rcpt = instance.activity.auth_user

    verb = None
    nf_type = None
    if instance.has_like:
        verb = 'like your post'
        nf_type = 'like'
    elif instance.has_dislike:
        verb = 'dislike your post'
        nf_type = 'dislike'
    elif instance.has_share:
        verb = 'shared your post'
        nf_type = 'share'

    notify.send(instance.auth_user,
                recipient=rcpt,
                actor=instance.auth_user,
                target=instance.activity,
                verb=verb, nf_type=nf_type)


@receiver(post_save, sender=UsersProfile)
def user_profile_signal(sender, instance, **kwargs):
    print(' New Signup')

# @receiver(post_save, sender=Applicants)
# def users_applied_job(sender, instance, **kwargs):
#     verb = 'applied to ' + instance.job.title
#     nf_type = 'apply_to_job'
#     notify.send(instance.user_profile.auth_user,
#                 recipient=instance.job.auth_user,
#                 actor=instance.user_profile.auth_user,
#                 target=instance.job,
#                 verb=verb, nf_type=nf_type)
