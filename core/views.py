from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from django.db.models import Count
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import CustomUser, Post, PostLike, Comment, Notification
from .serializers import PostSerializer, CommentSerializer, PostLikeSerializer,CustomUserListSerializer, CustomUserDetailSerializer,NotificationSerializer


"""Profiller ham baylanislar"""
class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username','first_name']

    def get_queryset(self):
        queryset = CustomUser.objects.all()

        if self.action == 'retrieve':
            queryset = queryset.annotate(
                posts_count = Count('posts', distinct=True),
                followers_count = Count('followers', distinct=True),
                following_count = Count('following', distinct=True)
            )
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CustomUserDetailSerializer
        return CustomUserListSerializer
    
    #Follow
    @action(detail=True, methods=['post'], permission_classes = [IsAuthenticated])
    def follow(self, request, pk=None):
        target_user = self.get_object()
        current_user = request.user

        if current_user == target_user:
            return Response({'error': 'Ozinizge-oziniz jazila almaysiz!'}, status=status.HTTP_400_BAD_REQUEST)

        if target_user.followers.filter(id=current_user.id).exists():
            return Response({'status': 'Siz aldin follow qilgansiz!'})

        target_user.followers.add(current_user) 

        return Response({'status': f'{target_user.username} paydalaniwshisina jazildiniz'},status=status.HTTP_201_CREATED)
    
    #Unfollow
    @action(detail=True, methods=['post'],permission_classes=[IsAuthenticated])
    def unfollow(self,request, pk=None):
        target_user = self.get_object()
        current_user = request.user

        if target_user.followers.filter(id=current_user.id).exists():
            target_user.followers.remove(current_user)
            return Response({'status': "Siz unfollow qildiniz"})
        
        return Response({'status': 'Siz bul adamga follow bolmagansiz'})
    
    #Followers
    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        user = self.get_object()
        followers_list = user.followers.all()

        page = self.paginate_queryset(followers_list)
        if page is not None:
            serializer = CustomUserListSerializer(page,many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CustomUserDetailSerializer(followers_list, many=True)
        return Response(serializer.data)
    
    #Following
    @action(detail=True, methods=['get'])
    def following(self,request, pk=None):
        user = self.get_object
        following_list = user.following.all()

        page = self.paginate_queryset(following_list)
        if page is not None:
            serializer = CustomUserListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CustomUserDetailSerializer(following_list,many=True)
        return Response(serializer.data)
    

"""Postlar"""
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]




