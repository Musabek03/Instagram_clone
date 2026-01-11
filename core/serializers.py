from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Post, Comment, Notification

User = get_user_model()


class CustomUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "avatar", "first_name", "last_name"]


# 2. Profil ushın (Detail) - Tolıq
class CustomUserDetailSerializer(serializers.ModelSerializer):
    posts_count = serializers.IntegerField(read_only=True)
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "avatar",
            "bio",
            "website",
            "posts_count",
            "followers_count",
            "following_count",
            "is_following",
            "created_at",
        ]

    @extend_schema_field(serializers.BooleanField)
    def get_is_following(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.followers.filter(id=request.user.id).exists()
        return False


class FeedAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "avatar"]


class FeedPostSerializer(serializers.ModelSerializer):
    author = FeedAuthorSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "image",
            "caption",
            "created_at",
            "likes_count",
            "comments_count",
            "is_liked",
        ]

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "user", "text", "created_at"]
        read_only_fields = ["created_at"]


class NotificationSerializer(serializers.ModelSerializer):

    sender = FeedAuthorSerializer(read_only=True)
    post_image = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "sender",
            "type",
            "post_image",
            "message",
            "is_read",
            "created_at",
        ]

    @extend_schema_field(serializers.CharField)
    def get_post_image(self, obj):
        if obj.post and obj.post.image:
            return obj.post.image.url
        return None

    @extend_schema_field(serializers.CharField)
    def get_message(self, obj):
        if obj.type == "like":
            return f"{obj.sender.username} senin postina like basti"
        elif obj.type == "comment":
            return f"{obj.sender.username} senin postina kommentariya jazdi"
        elif obj.type == "follow":
            return f"{obj.sender.username} sagan follow etti"
        return "Jana xabar"


class PostSerializer(serializers.ModelSerializer):
    author = FeedAuthorSerializer(read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "image",
            "caption",
            "created_at",
            "likes_count",
            "comments_count",
            "is_liked",
        ]
        read_only_fields = ["created_at"]

    @extend_schema_field(serializers.CharField)
    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password_confirm"]

    def validate(self, keys):
        if keys["password"] != keys["password_confirm"]:
            raise serializers.ValidationError({"password": "Paroller saykes kelmedi"})
        return keys

    def create(self, validate_data):
        validate_data.pop("password_confirm", None)
        user = User.objects.create_user(**validate_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Eski parol qate")
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance
