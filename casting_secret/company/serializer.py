import cloudinary
from friendship.models import Follow
from rest_framework import serializers

from casting_secret.models.company_models import Company, CompanyTags
from casting_secret.serializers.common_serializers import TalentCategoriesSerializer
from casting_secret.user_profile.serializers import UserProfilePlainSerializer


class CompanyTagSerializer(serializers.ModelSerializer):
    category = TalentCategoriesSerializer(read_only=True)

    class Meta:
        model = CompanyTags
        fields = ('category',)


class CompanySerializer(serializers.ModelSerializer):
    tags = CompanyTagSerializer(read_only=True, many=True)
    user_profile = UserProfilePlainSerializer(read_only=True)

    def to_representation(self, obj):
        ret = super(CompanySerializer, self).to_representation(obj)
        # remove 'url' field if mobile request
        if not obj.is_address_public and self.context['request'].user != obj.user_profile.auth_user:
            ret.pop('headquarter')

        return ret

    is_admin = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField('get_avatar_path')
    cover = serializers.SerializerMethodField('get_cover_path')
    is_follow = serializers.SerializerMethodField()

    def get_is_admin(self, obj):
        if obj.user_profile.auth_user == self.context['request'].user:
            return True
        return False

    def get_is_follow(self, obj):
        return Follow.objects.follows(self.context['request'].user, obj.user_profile.auth_user)

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

    class Meta:
        model = Company
        read_only_fields = ('user_profile', 'slug')
        fields = '__all__'
