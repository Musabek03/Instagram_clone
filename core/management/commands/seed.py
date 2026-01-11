from django.core.management.base import BaseCommand
from faker import Faker
import random

from core.models import CustomUser, Post, Comment, Notification

fake = Faker()

class Command(BaseCommand):
    help = "Fill database with fake data"

    def handle(self, *args, **kwargs):

        self.stdout.write("Seeding data...")

        # ---------- USERS ----------
        users = []
        for i in range(20):
            user = CustomUser.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password="12345678",
                bio=fake.text(max_nb_chars=150),
                website=fake.url(),
            )
            users.append(user)

        # ---------- FOLLOWERS ----------
        for user in users:
            following = random.sample(users, k=random.randint(0, 5))
            user.followers.add(*following)

        # ---------- POSTS ----------
        posts = []
        for user in users:
            for _ in range(random.randint(1, 5)):
                post = Post.objects.create(
                    author=user,
                    caption=fake.text(max_nb_chars=200)
                )
                posts.append(post)

        # ---------- LIKES ----------
        for post in posts:
            liked_users = random.sample(users, k=random.randint(0, 7))
            post.likes.add(*liked_users)

        # ---------- COMMENTS ----------
        for post in posts:
            for _ in range(random.randint(0, 5)):
                Comment.objects.create(
                    user=random.choice(users),
                    post=post,
                    text=fake.sentence()
                )

        # ---------- NOTIFICATIONS ----------
        for _ in range(30):
            sender = random.choice(users)
            receiver = random.choice(users)

            if sender != receiver:
                Notification.objects.create(
                    sender=sender,
                    receiver=receiver,
                    type=random.choice(['like', 'comment', 'follow']),
                    post=random.choice(posts),
                    is_read=random.choice([True, False])
                )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))