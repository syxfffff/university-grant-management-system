from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class GrantCall(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateField()
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    currency = models.CharField(max_length=3, default="MYR")
    is_open = models.BooleanField(default=True)

    class Meta:
        ordering = ["deadline", "title"]
        constraints = [models.CheckConstraint(condition=Q(max_amount__gt=0), name="call_positive_amount")]

    def __str__(self):
        return self.title


class Application(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    call = models.ForeignKey(GrantCall, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    abstract = models.TextField(max_length=10000)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(condition=Q(amount__gt=0), name="application_positive_amount"),
            models.CheckConstraint(condition=Q(status__in=["draft", "submitted", "approved", "rejected"]), name="application_valid_status"),
        ]

    def __str__(self):
        return self.title


class Decision(models.Model):
    application = models.OneToOneField(Application, on_delete=models.PROTECT)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    outcome = models.CharField(max_length=12, choices=[("approved", "Approved"), ("rejected", "Rejected")])
    feedback = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(outcome__in=["approved", "rejected"]), name="decision_valid_outcome")]
