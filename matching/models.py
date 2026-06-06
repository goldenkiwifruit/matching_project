from django.contrib.auth.models import User
from django.db import models
    
class Job(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    reward = models.IntegerField()
    max_workers = models.IntegerField(default=1)
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    STATUS_CHOICES = [
        ("pending", "応募中"),
        ("accepted", "採用"),
        ("rejected", "不採用"),
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

class Contract(models.Model):
    STATUS_CHOICES = [
        ("active", "契約中"),
        ("completed", "契約終了"),
        ("cancelled", "キャンセル"),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    worker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="worker_contracts"
    )

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="client_contracts"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def under_count_for_user(self, user):
        return self.message_set.filter(is_read=False).exclude(sender=user).count()

class Message(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, null=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class Review(models.Model):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews_given"
    )

    reviewee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews_received"
    )

    rating = models.IntegerField() #1~5

    comment = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )