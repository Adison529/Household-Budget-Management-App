from rest_framework import permissions

from .models import UserAccess, AccessRequest

# Custom permission to allow only authenticated users to access the view
class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsSuperuserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Allow GET, HEAD, OPTIONS requests
        return request.user and request.user.is_superuser
    
class IsBudgetEditorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        budget_manager_id = view.kwargs.get('budget_manager_id') or request.data.get('budget_manager')
        
        if user.is_superuser:
            return True
        
        if budget_manager_id:
            return UserAccess.objects.filter(
                user=user,
                budget_manager_id=budget_manager_id,
                role__in=['edit', 'admin']
            ).exists()
        
        return False
    
class IsAdminOfBudgetManager(permissions.BasePermission):
    def has_permission(self, request, view):
        #if request.user.is_superuser:
        #    return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        #if request.user.is_superuser:
        #    return True
        return obj.budget_manager.admin == request.user

# unsure what is this permission class for
class IsAdminOfRelatedBudgetManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if isinstance(obj, AccessRequest):
            return obj.budget_manager.admin == request.user
        if isinstance(obj, UserAccess):
            return obj.budget_manager.admin == request.user
        return False