from django.shortcuts import render
from rest_framework import viewsets, filters,mixins
from rest_framework.decorators import action
from django.db.models import Count
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import CustomUser, Post, Comment, Notification
from .serializers import ( 
                          CommentSerializer,CustomUserListSerializer,CustomUserDetailSerializer,
                          PostSerializer,FeedPostSerializer,NotificationSerializer
                          )

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
        user = self.get_object()
        following_list = user.following.all()

        page = self.paginate_queryset(following_list)
        if page is not None:
            serializer = CustomUserListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CustomUserDetailSerializer(following_list,many=True)
        return Response(serializer.data)
    

"""Postlar + Reakciyalar"""
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    #Like basiw
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self,request,pk=None):
        post =self.get_object()
        user = request.user

        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            return Response({'status':'Unliked', 'likes_count':post.likes.count()})
        else:
            post.likes.add(user)

        return Response({'status': 'liked', 'likes_count': post.likes.count()})
    
    #Like basqanlar dizimi
    @action(detail=True, methods=['get'])
    def likes(self,request, pk=None):
        post = self.get_object()
        users = post.likes.all()

        page = self.paginate_queryset(users)
        if page is not None:
            serializer = CustomUserListSerializer(page,many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CustomUserDetailSerializer(page,many=True)
        return Response(serializer.data)
    
    #Comment jaziw
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self,request, pk=None):
        post = self.get_object()
        user = request.user 
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=user,post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Comment jazganlar dizimi
    @action(detail=True, methods=['get'])
    def comments(self,request,pk=None):
        post = self.get_object()
        comments = Comment.objects.filter(post=post).order_by('-created_at')

        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentSerializer(page,many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CommentSerializer(comments,many=True)
        return Response(serializer.data)


"""NewsFeed"""
class FeedPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

# generics.ListAPIView ornina  mixins.ListModelMixin, viewsets.GenericViewSet islettim. urls.py da router paydalana aliw ushin
class FeedAPIView(mixins.ListModelMixin, viewsets.GenericViewSet):
        serializer_class = FeedPostSerializer
        permission_classes = [IsAuthenticated]
        pagination_class = FeedPagination

        def get_queryset(self):
            user = self.request.user
            following_users = user.following.all()
            queryset = Post.objects.filter(author__in=following_users).select_related('author')\
            .annotate(
                likes_count = Count('likes', distinct=True), 
                comments_count = Count('comments', distinct=True))\
            .order_by('-created_at')

            return queryset
        

"""Notifications"""
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user).order_by('-created_at')
    





