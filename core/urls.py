from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet,PostViewSet,FeedAPIView, NotificationViewSet

router = DefaultRouter()

router.register(r"users", CustomUserViewSet, basename='user')
router.register(r"posts",PostViewSet,basename="post")
router.register(r"feed", FeedAPIView, basename='feed')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = router.urls