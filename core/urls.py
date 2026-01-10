from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet,PostViewSet

router = DefaultRouter()

router.register(r"users", CustomUserViewSet, basename='user')
router.register(r"posts",PostViewSet,basename="post")

urlpatterns = router.urls