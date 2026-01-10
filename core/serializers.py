from rest_framework import serializers
from .models import CustomUser, Post, PostLike, Comment, Notification


class CustomUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'avatar', 'first_name', 'last_name']

# 2. Profil ushın (Detail) - Tolıq
class CustomUserDetailSerializer(serializers.ModelSerializer):
    posts_count = serializers.IntegerField(read_only=True)
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    is_following = serializers.SerializerMethodField()

    class Meta:
        fields = ['id','username', 'avatar', 'bio', 'website', 'posts_count', 'followers_count', 'following_count', 'is_following', 'created_at']
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers.filter(id=request.user.id).exists()
        return False
    

class FeedAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'avatar']


class FeedPostSerializer(serializers.ModelSerializer):
    author = FeedAuthorSerializer(read_only = True)
    likes_count = serializers.IntegerField(read_only = True)
    comments_count = serializers.IntegerField(read_only = True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'image', 'caption', 'created_at','likes_count', 'comments_count', 'is_liked']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    





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