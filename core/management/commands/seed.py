import random
import io
from PIL import Image
from faker import Faker
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from core.models import Post, Comment

# User modeldi alıw
User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Bazani feyk magliwmatlar ham JPEG suwretler menen toltiriw"

    def handle(self, *args, **kwargs):
        self.stdout.write("Skript iske tusti...")

        # 1. Userler
        users = self.create_users(20)  # 20 paydalanıwshı (tezirek bolıwı ushın)

        # 2. Follows
        self.create_follows(users)

        # 3. Postlar
        posts = self.create_posts(users, 50)  # 50 post

        # 4. Interactions (Likes & Comments)
        self.create_interactions(users, posts)

        self.stdout.write(self.style.SUCCESS("Barliq jumislar juwmaqlandi!"))

    def get_random_image(self, width=600, height=600):
        """
        Random rendegi JPEG suwret jaratip beredi.
        """
        # Random reń (R, G, B)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # Súwret jaratıw
        image = Image.new("RGB", (width, height), color)

        # Fayldı yadta (RAM) saqlaw
        file_obj = io.BytesIO()
        image.save(file_obj, format="JPEG")  # JPEG formatına ótkeriw

        return ContentFile(file_obj.getvalue())

    def create_users(self, n):
        self.stdout.write(f" {n} paydalaniwshi jaratilip atir...")
        users = []
        for _ in range(n):
            username = fake.user_name()
            while User.objects.filter(username=username).exists():
                username = username + str(random.randint(1, 999))

            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password="password123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                bio=fake.text(max_nb_chars=100),
                website=fake.url(),
            )

            # Avatar ushın 200x200 súwret
            file_name = f"avatar_{user.id}.jpg"
            image_content = self.get_random_image(200, 200)
            user.avatar.save(file_name, image_content, save=True)

            users.append(user)
        return users

    def create_follows(self, users):
        self.stdout.write(" Follow baylanislari jaratilip atir...")
        count = 0
        for user in users:
            possible_friends = [u for u in users if u != user]
            to_follow = random.sample(possible_friends, k=random.randint(3, 10))
            user.followers.add(*to_follow)
            count += len(to_follow)
        self.stdout.write(f"Jami {count} follow baylanisi ornatildi!")

    def create_posts(self, users, n):
        self.stdout.write(f"{n} post jaratilip atir...")
        posts = []
        for _ in range(n):
            author = random.choice(users)
            post = Post(
                author=author,
                caption=fake.paragraph(nb_sentences=3),
            )

            # Post ushın 800x600 súwret
            file_name = f"post_{random.randint(1000,9999)}.jpg"
            image_content = self.get_random_image(800, 600)
            post.image.save(file_name, image_content, save=False)

            post.save()
            posts.append(post)
        return posts

    def create_interactions(self, users, posts):
        self.stdout.write(" Like ham Kommentariyalar jaratilip atir...")
        like_count = 0
        comment_count = 0

        for post in posts:
            # Likes
            likers = random.sample(users, k=random.randint(0, min(10, len(users))))
            for liker in likers:
                if liker != post.author:
                    post.likes.add(liker)
                    like_count += 1

            # Comments
            num_comments = random.randint(0, 5)
            for _ in range(num_comments):
                commenter = random.choice(users)
                Comment.objects.create(user=commenter, post=post, text=fake.sentence())
                comment_count += 1

        self.stdout.write(
            f"{like_count} like ham {comment_count} kommentariya qosildi!")
