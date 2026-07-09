from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CharField, Model, TextField, DecimalField, ForeignKey, CASCADE,
    DateTimeField, ImageField, BooleanField, PositiveIntegerField,
    TextChoices, IntegerField
)


class CustomUserManager(BaseUserManager):
    def _create_user(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number kiritilishi shart")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", "user")

        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser uchun is_staff=True bo‘lishi kerak")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser uchun is_superuser=True bo‘lishi kerak")

        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    class Role(TextChoices):
        USER = "user", "Foydalanuvchi"
        ADMIN = "admin", "Administrator"

    full_name = CharField(max_length=155)
    username = None
    phone_number = CharField(max_length=20, unique=True)
    avatar = ImageField(upload_to='avatars/', null=True, blank=True)
    role = CharField(max_length=10, choices=Role.choices, default=Role.USER)
    is_verified = BooleanField(default=False)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return self.full_name or self.phone_number


class Category(Model):
    name = CharField(max_length=50)
    icon = CharField(max_length=10, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Post(Model):
    class Status(TextChoices):
        PENDING = "pending", "Ko'rib chiqilmoqda"
        ACTIVE = "active", "Faol"
        SOLD = "sold", "Sotilgan"
        REJECTED = "rejected", "Rad etilgan"


    user = ForeignKey(User, on_delete=CASCADE, related_name="posts")
    category = ForeignKey(Category, on_delete=CASCADE, related_name="posts")
    title = CharField(max_length=50)
    desc = TextField()
    price = DecimalField(max_digits=17, decimal_places=2)
    city = CharField(max_length=50)
    status = CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    reject_reason = CharField(max_length=255, null=True, blank=True)
    reviewed_by = ForeignKey(
        User, on_delete=CASCADE, null=True, blank=True, related_name="reviewed_posts"
    )
    is_premium = BooleanField(default=False)
    views_count = PositiveIntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class PostImage(Model):
    post = ForeignKey(Post, on_delete=CASCADE, related_name="images")
    image = ImageField(upload_to='post_images/', null=True, blank=True)
    order = IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.post.title} — image {self.order}"


class Favorite(Model):
    user = ForeignKey(User, on_delete=CASCADE, related_name="favorites")
    post = ForeignKey(Post, on_delete=CASCADE, related_name="favorited_by")
    created_at = DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("user", "post")
    def __str__(self):
        return f"{self.user} → {self.post}"
