from django.contrib import admin
from .models import OperationCategory, OperationType, BudgetManager, Operation, UserAccess, AccessRequest

admin.site.register(OperationCategory)
admin.site.register(OperationType)
admin.site.register(BudgetManager)
admin.site.register(Operation)
admin.site.register(UserAccess)
admin.site.register(AccessRequest)
