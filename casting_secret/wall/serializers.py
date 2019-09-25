import cloudinary
from friendship.models import Friend
from rest_framework import serializers

from casting_secret.company.serializer import CompanySerializer
from casting_secret.models.profile_models import Albums, ProfileSettings
from casting_secret.models.wall_models import Activity, ActivitySocialAction, Comments, ActivityAttachment, \
    CommentMention, ActivityMention
from casting_secret.serializers.common_serializers import AuthUserSerializerLogin
from casting_secret.user_profile.serializers import UserProfileSettingsSerializer


class CommentMentionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentMention
        fields = '__all__'
        read_only_fields = ('comment',)


class ListCommentMentionSerializer(serializers.ModelSerializer):
    auth_user = AuthUserSerializerLogin(read_only=True)

    class Meta:
        model = CommentMention
        fields = ('auth_user',)


class ActivityMentionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityMention
        fields = '__all__'
        read_only_fields = ('activity',)


class ListActivityMentionSerializer(serializers.ModelSerializer):
    auth_user = AuthUserSerializerLogin(read_only=True)

    class Meta:
        model = ActivityMention
        fields = ('auth_user',)


class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class RecursiveActivitySerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.__class__(value, context=self.context)
        return serializer.data


class ActivityCommentSerializer(serializers.ModelSerializer):
    comment_thread = RecursiveSerializer(many=True, read_only=True)
    auth_user = AuthUserSerializerLogin(read_only=True)
    comment_mention = ListCommentMentionSerializer(many=True, read_only=True)

    class Meta:
        model = Comments
        fields = '__all__'
        read_only_fields = ('auth_user', 'activity',)


class AlbumSerializer(serializers.ModelSerializer):
    item_count = serializers.SerializerMethodField('count_items')
    image = serializers.SerializerMethodField('get_logo')

    def get_logo(self, obj):
        attachement = obj.auth_user_album.first()
        if attachement:
            return attachement.path
        return None

    def count_items(self, obj):
        return obj.auth_user_album.all().count()

    class Meta:
        model = Albums
        fields = '__all__'
        read_only_fields = ('user_profile',)


class ActivityAttachmentSerializers(serializers.ModelSerializer):
    album = AlbumSerializer(read_only=True)
    eager = serializers.SerializerMethodField()

    def get_eager(self, obj):
        if obj.path:
            try:
                return cloudinary.api.resource(obj.path_json)
            except Exception as e:
                return None
        return None

    class Meta:
        model = ActivityAttachment
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    like_count = serializers.ReadOnlyField()
    url = serializers.SerializerMethodField()
    share_count = serializers.ReadOnlyField()
    company = CompanySerializer(read_only=True)
    dislike_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    auth_user = AuthUserSerializerLogin(read_only=True)
    is_friends = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField('is_liked')
    author_settings = serializers.SerializerMethodField()
    shared = serializers.SerializerMethodField('is_shared')
    disLiked = serializers.SerializerMethodField('is_disliked')
    bookmarked = serializers.SerializerMethodField('is_bookmarked')
    original_activity = RecursiveActivitySerializer(read_only=True)
    activity_mention = ListActivityMentionSerializer(many=True, read_only=True)
    activity_attachment = ActivityAttachmentSerializers(many=True, read_only=True)

    def is_shared(self, obj):
        return obj.activity_action.filter(has_share=True, auth_user=self.context['request'].user).exists()

    def is_liked(self, obj):
        return obj.activity_action.filter(has_like=True, auth_user=self.context['request'].user).exists()

    def is_disliked(self, obj):
        return obj.activity_action.filter(has_dislike=True, auth_user=self.context['request'].user).exists()

    def is_bookmarked(self, obj):
        return obj.activity_control.filter(is_saved=True, auth_user=self.context['request'].user).exists()

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(location="/") + obj.get_absolute_url()[1:]

    def get_is_friends(self, obj):
        try:
            return Friend.objects.are_friends(self.context['request'].user, obj.auth_user)
        except:
            return False

    def get_author_settings(self, obj):
        instance = ProfileSettings.objects.get(user_profile__auth_user=obj.auth_user)
        return UserProfileSettingsSerializer(instance=instance, context={'request': self.context['request']}).data

    class Meta:
        model = Activity
        fields = '__all__'
        read_only_fields = ('action', 'liked', 'disLiked', 'is_friends', 'author_settings')


class ActivitySocialActionSerializers(serializers.ModelSerializer):
    class Meta:
        model = ActivitySocialAction
        fields = '__all__'
