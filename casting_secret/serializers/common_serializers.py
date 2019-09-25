import cloudinary
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.utils.text import slugify
from notify.models import Notification
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

from casting_secret.models.models import TalentCategories, Subscription
from casting_secret.models.profile_models import UsersProfileTalentCategories


class TalentCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentCategories
        fields = '__all__'


class AuthUserSerializerLogin(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    def get_slug(self, obj):
        profile = obj.auth_user_profile.get()
        return profile.slug

    def get_avatar(self, obj):
        profile = obj.auth_user_profile.get()
        if profile.avatar:
            try:
                return cloudinary.api.resource(profile.avatar)
            except:
                return None
        return None

    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'email', 'username', 'slug', 'avatar')


class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'email', 'username')
        read_only_fields = ('email', 'username',)


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(max_length=128, required=True)
    last_name = serializers.CharField(max_length=128, required=True)
    category = serializers.ListField(required=True)
    about = serializers.CharField(max_length=5000, required=True)

    def custom_signup(self, request, user):
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        user.save()

        # create profile
        profile = user.auth_user_profile.create(
            slug=slugify('%s %s' % (user.get_full_name(), user.id), allow_unicode=True),
            about=self.validated_data.get('about', '')
        )

        # create profile talent category
        categories = self.validated_data.get('category', None)
        bulk_category = []
        for category in categories:
            usersProfileTalentCategories = UsersProfileTalentCategories()
            usersProfileTalentCategories.user_profile = profile
            usersProfileTalentCategories.talent_categories_id = category
            bulk_category.append(usersProfileTalentCategories)
        try:
            UsersProfileTalentCategories.objects.bulk_create(bulk_category)
        except Exception:
            pass


class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()

    def get_actor(self, obj):
        return AuthUserSerializerLogin(instance=User.objects.get(pk=obj.actor_object_id)).data

    class Meta:
        model = Notification
        fields = ('id', 'verb', 'actor', 'created', 'nf_type', 'target_url', 'read')


class EmailAddressesSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmailAddress
        exclude = ('user',)


class SubscribeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Subscription
