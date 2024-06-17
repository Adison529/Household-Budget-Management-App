from django.db import models
from django.contrib.auth.models import User
import uuid

# operation category, e.g. groceries, cosmetics, car expenses, rent etc. as well as 'no category' to handle such cases
class OperationCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

# operation type, there are only 2 intended types: expense, income
class OperationType(models.Model):
    name = models.CharField(max_length=7, unique=True)

    def __str__(self):
        return self.name

# budget manager for a household, includes unique id required to request access, name, admin (owner/creator)
class BudgetManager(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=64)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_budgetmanagers')

    def __str__(self):
        return self.name

# operation, either an expense or income
# includes FK to the household it's tied to, type (expense/income), date, title (brief description for the operation), category, value
# optional "by" field if you want to add an user who created this operation
class Operation(models.Model):
    INCOME = 'income'
    EXPENSE = 'expense'
    
    OPERATION_TYPES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense')
    ]
    
    budget_manager = models.ForeignKey(BudgetManager, on_delete=models.CASCADE, related_name='operations')
    #type = models.CharField(max_length=7, choices=OPERATION_TYPES)
    type = models.ForeignKey(OperationType, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    title = models.CharField(max_length=128)
    category = models.ForeignKey(OperationCategory, on_delete=models.SET_NULL, null=True)
    value = models.DecimalField(max_digits=8, decimal_places=2)
    by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operations')

    def __str__(self):
        return f"{self.title} ({self.type}) - {self.value}"

# user access type in a household's budget manager (read_only/edit/admin)
class UserAccess(models.Model):
    READ_ONLY = 'read_only'
    EDIT = 'edit'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (READ_ONLY, 'Read Only'),
        (EDIT, 'Edit'),
        (ADMIN, 'Admin')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    budget_manager = models.ForeignKey(BudgetManager, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'budget_manager')

    def __str__(self):
        return f"{self.user.username} - {self.budget_manager.name} ({self.role})"
    
class AccessRequest(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    DENIED = 'denied'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (DENIED, 'Denied')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_requests')
    budget_manager = models.ForeignKey(BudgetManager, on_delete=models.CASCADE, related_name='access_requests')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} request to {self.budget_manager.name} ({self.status})"