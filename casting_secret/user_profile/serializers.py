import cloudinary
from allauth.account.models import EmailAddress
from friendship.models import Friend
from rest_framework import serializers

from casting_secret.models import ProfileSettings
from casting_secret.models.profile_models import AgeRangeLookUp, HeightRangeLookUp, WeightRangeLookUp, BuildLookUp, \
    HairLookUp, EyesLookUp, EthnicitiesLookUp, HobbiesLookUp, UsersProfile, ProfileSocialLinks, ProfileTraining, \
    ProfileHobbies
from casting_secret.serializers.common_serializers import AuthUserSerializer, AuthUserSerializerLogin, \
    EmailAddressesSerializers


class AgeRangeLookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgeRangeLookUp
        fields = '__all__'


class HeightRangeLookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeightRangeLookUp
        fields = '__all__'


class WeightRangeLookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightRangeLookUp
        fields = '__all__'


class BuildLookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildLookUp
        fields = '__all__'


class HairLookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = HairLookUp
        fields = '__all__'


class EyesLookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = EyesLookUp
        fields = '__all__'


class EthnicitiesLookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = EthnicitiesLookUp
        fields = '__all__'


class HobbiesLookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = HobbiesLookUp
        fields = '__all__'


class ProfileSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileSocialLinks
        fields = '__all__'
        read_only_fields = ('user_profile',)


class ProfileTrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileTraining
        fields = '__all__'
        read_only_fields = ('user_profile',)


class ProfileHobbiesSerializer(serializers.ModelSerializer):
    hobbies = HobbiesLookUpSerializer(read_only=True)

    class Meta:
        model = ProfileHobbies
        fields = '__all__'


class ProfileHobbiessSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if 'hobbies' not in data and 'custom' not in data:
            raise serializers.ValidationError("hobbies or custom are required")
        return super(ProfileHobbiessSerializer, self).validate(data)

    class Meta:
        model = ProfileHobbies
        fields = '__all__'
        read_only_fields = ('user_profile',)
        validators = []


class UserProfileSerializer(serializers.ModelSerializer):
    users_profile_social = ProfileSocialSerializer(many=True, read_only=True)
    users_profile_courses = ProfileTrainingSerializer(many=True, read_only=True)
    auth_user = AuthUserSerializer(read_only=True)
    users_profile_hobbies = ProfileHobbiesSerializer(many=True, read_only=True)
    height = HeightRangeLookUpSerializer(read_only=True)
    weight = WeightRangeLookUpSerializer(read_only=True)
    build = BuildLookUpSerializer(read_only=True)
    hair = HairLookUpSerializer(read_only=True)
    eye = EyesLookUpSerializer(read_only=True)
    ethnicities = EthnicitiesLookUpSerializer(read_only=True)

    avatar = serializers.SerializerMethodField('get_avatar_path')
    cover = serializers.SerializerMethodField('get_cover_path')
    is_friends = serializers.SerializerMethodField()
    applied_jobs = serializers.SerializerMethodField()

    def get_applied_jobs(self, obj):
        if obj.applied_job:
            try:
                return obj.applied_job
            except:
                return 0
        return 0

    def get_avatar_path(self, obj):
        if obj.avatar:
            try:
                return cloudinary.api.resource(obj.avatar)
            except:
                return None
        return None

    def get_cover_path(self, obj):
        if obj.cover:
            try:
                return cloudinary.api.resource(obj.cover)
            except:
                return None
        return None

    def get_is_friends(self, obj):
        try:
            return Friend.objects.are_friends(self.context['request'].user, obj.auth_user)
        except:
            return False

    class Meta:
        model = UsersProfile
        fields = '__all__'
        read_only_fields = ('slug',)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    users_profile_social = ProfileSocialSerializer(many=True, read_only=True)
    users_profile_courses = ProfileTrainingSerializer(many=True, read_only=True)
    auth_user = AuthUserSerializer(read_only=True)

    class Meta:
        model = UsersProfile
        fields = '__all__'
        read_only_fields = ('slug',)


class UserProfilePlainSerializer(serializers.ModelSerializer):
    auth_user = AuthUserSerializerLogin(read_only=True)

    class Meta:
        model = UsersProfile
        fields = ('auth_user',)
        read_only_fields = ('slug',)


class UserProfileSettingsSerializer(serializers.ModelSerializer):
    emails = serializers.SerializerMethodField()

    def get_emails(self, obj):
        user = self.context['request'].user
        email_addresses = EmailAddress.objects.filter(user=user)
        data = EmailAddressesSerializers(instance=email_addresses, many=True).data
        return data

    class Meta:
        model = ProfileSettings
        exclude = ('user_profile',)


class ProfileViewers(serializers.ModelSerializer):
    visitor_profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = ProfileSettings
        exclude = ('user_profile',)
