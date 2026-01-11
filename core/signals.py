from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from .models import Post, Comment, CustomUser, Notification


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        if instance.user != instance.post.author:
            Notification.objects.create(
                sender=instance.user,
                receiver=instance.post.author,
                type="comment",
                post=instance.post,
                is_read=False,
            )


@receiver(m2m_changed, sender=Post.likes.through)
def create_like_notification(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for user_id in pk_set:
            liker = CustomUser.objects.get(pk=user_id)
            if liker != instance.author:
                Notification.objects.get_or_create(
                    sender=liker,
                    receiver=instance.author,
                    type="like",
                    post=instance,
                    defaults={"is_read": False},
                )


@receiver(m2m_changed, sender=CustomUser.followers.through)
def create_follow_notification(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for follower_id in pk_set:
            follower_user = CustomUser.objects.get(pk=follower_id)
            Notification.objects.get_or_create(
                sender=follower_user,
                receiver=instance,
                type="follow",
                post=None,
                defaults={"is_read": False},)
