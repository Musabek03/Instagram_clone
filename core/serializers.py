from rest_framework import serializers
from .models import CustomUser, Post, PostLike, Comment, Notification


class CustomUserSerializer(serializers.Serializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

class PostSerializer(serializers.Serializer):
    class Meta:
        model = Post
        fields = "__all__"

class PostLikeSerializer(serializers.Serializer):
    class Meta:
        model = PostLike
        fields = "__all__"

class CommentSerializer(serializers.Serializer):
    class Meta:
        model = Comment
        fields = "__all__"

class NotificationSerializer(serializers.Serializer):
    class Meta:
        model = Notification
        fields = "__all__"