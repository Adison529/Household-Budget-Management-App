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
    
class IsBudgetMember(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user      
        budget_manager_id = view.kwargs.get('budget_manager_id')

        if not budget_manager_id:
            return False

        # Check if the user has an entry in UserAccess for the BudgetManager
        return UserAccess.objects.filter(
            user=user,
            budget_manager_id=budget_manager_id
        ).exists()

class IsBudgetEditorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        budget_manager_id = view.kwargs.get('budget_manager_id') or request.data.get('budget_manager')
        
        if budget_manager_id:
            return UserAccess.objects.filter(
                user=user,
                budget_manager_id=budget_manager_id,
                role__in=['edit', 'admin']
            ).exists()
        
        return False
    
# class IsAdminOfBudgetManager(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated

#     def has_object_permission(self, request, view, obj):
#         return obj.budget_manager.admin == request.user

class IsAdminOfBudgetManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Check if the user is the admin of the BudgetManager object
        is_admin_of_budget_manager = obj.admin == user

        # Check if the user has an entry in UserAccess with role 'admin' for the BudgetManager
        has_admin_role_in_user_access = UserAccess.objects.filter(
            user=user,
            budget_manager=obj,
            role=UserAccess.ADMIN
        ).exists()

        return is_admin_of_budget_manager and has_admin_role_in_user_access

# unsure what is this permission class for
class IsAdminOfRelatedBudgetManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, AccessRequest):
            return obj.budget_manager.admin == request.user
        if isinstance(obj, UserAccess):
            return obj.budget_manager.admin == request.user
        return False