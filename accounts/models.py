from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    ROLE_CHOICES = (
        ("user", "ユーザー"),
        ("company", "企業"),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="user"
    )

    age = models.IntegerField(null=True, blank=True)
    bio = models.TextField(blank=True)

# accounts/models.py
class ProfileImage(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="profile_images/")
    order = models.IntegerField(default=0)
