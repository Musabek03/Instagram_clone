from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet,PostViewSet,FeedAPIView

router = DefaultRouter()

router.register(r"users", CustomUserViewSet, basename='user')
router.register(r"posts",PostViewSet,basename="post")
router.register(r"feed", FeedAPIView, basename='feed')

urlpatterns = router.urls