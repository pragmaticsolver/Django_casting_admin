# Generated by Django 2.1.3 on 2019-05-15 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casting_secret', '0004_profilesettings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profilesettings',
            name='can_friends',
        ),
        migrations.RemoveField(
            model_name='profilesettings',
            name='status',
        ),
        migrations.AddField(
            model_name='profilesettings',
            name='can_see_friends',
            field=models.CharField(blank=True, choices=[('ALL', 'ALL'), ('ONLY_FRIENDS', 'ONLY_FRIENDS'), ('COMPANY', 'COMPANY')], default='ALL', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='profilesettings',
            name='my_status',
            field=models.CharField(blank=True, choices=[('OFFLINE', 'OFFLINE'), ('ONLINE', 'ONLINE')], default='ONLINE', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='profilesettings',
            name='can_comment',
            field=models.CharField(blank=True, choices=[('ALL', 'ALL'), ('ONLY_FRIENDS', 'ONLY_FRIENDS'), ('COMPANY', 'COMPANY')], default='ALL', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='profilesettings',
            name='can_contact_info',
            field=models.CharField(blank=True, choices=[('ALL', 'ALL'), ('ONLY_FRIENDS', 'ONLY_FRIENDS'), ('COMPANY', 'COMPANY')], default='ALL', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='profilesettings',
            name='can_see_profile',
            field=models.CharField(blank=True, choices=[('ALL', 'ALL'), ('ONLY_FRIENDS', 'ONLY_FRIENDS'), ('COMPANY', 'COMPANY')], default='ALL', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='profilesettings',
            name='can_see_wall',
            field=models.CharField(blank=True, choices=[('ALL', 'ALL'), ('ONLY_FRIENDS', 'ONLY_FRIENDS'), ('COMPANY', 'COMPANY')], default='ALL', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='profilesettings',
            name='can_send_message',
            field=models.CharField(blank=True, choices=[('ALL', 'ALL'), ('ONLY_FRIENDS', 'ONLY_FRIENDS'), ('COMPANY', 'COMPANY')], default='ALL', max_length=50, null=True),
        ),
    ]