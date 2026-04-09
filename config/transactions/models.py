from django.db import models
from django.conf import settings
from django.db.models import Q

User = settings.AUTH_USER_MODEL

class FinancialRecord(models.Model):

    TYPE_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES,default='income')
    category = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(amount__gt=0),
                name="amount_positive"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.amount}({self.type})"