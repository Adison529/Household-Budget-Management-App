from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from .models import OperationCategory, OperationType, BudgetManager, Operation, UserAccess, AccessRequest
from .serializers import OperationCategorySerializer, OperationTypeSerializer, BudgetManagerSerializer, OperationSerializer, UserAccessSerializer, AccessRequestSerializer
from .permissions import IsAuthenticated, IsSuperuserOrReadOnly, IsBudgetEditorOrAdmin, IsAdminOfBudgetManager, IsAdminOfRelatedBudgetManager

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class OperationCategoryListCreateView(generics.ListCreateAPIView):
    queryset = OperationCategory.objects.all()
    serializer_class = OperationCategorySerializer
    permission_classes = [IsAuthenticated, IsSuperuserOrReadOnly]

    # only superuser can create new operation categories
    # operation categories are intended to be defined by the admin at the start of the web app's lifespan
    # if any new categories should be added in the future, it should be done so via Django admin panel
    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

class OperationTypeListCreateView(generics.ListCreateAPIView):
    queryset = OperationType.objects.all()
    serializer_class = OperationTypeSerializer
    permission_classes = [IsAuthenticated, IsSuperuserOrReadOnly]

    # only superuser can create new operation types
    # operation types are intended to be predefined at the start of the web app's lifespan and never altered
    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

class BudgetManagerListCreateView(generics.ListCreateAPIView):
    queryset = BudgetManager.objects.all()
    serializer_class = BudgetManagerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically assign current user as admin of the BudgetManager
        instance = serializer.save(admin=self.request.user)
        
        # Create UserAccess entry for admin role
        UserAccess.objects.create(user=self.request.user, budget_manager=instance, role=UserAccess.ADMIN)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset.all()
        return self.queryset.filter(
            models.Q(admin=user) | models.Q(memberships__user=user)
        ).distinct()
    
class BudgetManagerUpdateView(generics.UpdateAPIView):
    queryset = BudgetManager.objects.all()
    serializer_class = BudgetManagerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset.all()
        return self.queryset.filter(admin=user)
    
class BudgetManagerDeleteView(generics.DestroyAPIView):
    queryset = BudgetManager.objects.all()
    serializer_class = BudgetManagerSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve the BudgetManager instance based on the URL parameter (pk)
        obj = super().get_object()
        
        # Check if the authenticated user is an admin of this BudgetManager
        user = self.request.user
        if user != obj.admin:
            raise PermissionDenied("You do not have permission to perform this action.")

        return obj

class OperationListCreateView(generics.ListCreateAPIView):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated, IsBudgetEditorOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset.all()
        return self.queryset.filter(budget_manager__memberships__user=self.request.user)
    
    def perform_create(self, serializer):
        budget_manager_id = self.request.data.get('budget_manager')
        budget_manager = get_object_or_404(BudgetManager, id=budget_manager_id)
        
        # Superusers can create operations in any budget
        if self.request.user.is_superuser:
            serializer.save(by=self.request.user, budget_manager=budget_manager)
            return
        
        # Check if user is a member with 'edit' or 'admin' role
        user_access = UserAccess.objects.filter(
            user=self.request.user, 
            budget_manager=budget_manager, 
            role__in=['edit', 'admin']
        )
        
        if not user_access.exists():
            raise PermissionDenied({'detail': 'You do not have permission to perform this action.'})
        
        serializer.save(by=self.request.user, budget_manager=budget_manager)

# Handle GET and POST requests to UserAccess
# Authenticated users can retrieve UserAccess data only for households they are a member of (NOT IMPLEMENTED YET)
# Authenticated users can add new UserAccess entries only for households they are an admin of and it can be only "read_only" role
class UserAccessListCreateView(generics.ListCreateAPIView):
    queryset = UserAccess.objects.all()
    serializer_class = UserAccessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        budget_manager_id = self.request.data.get('budget_manager')
        role = self.request.data.get('role')

        # Ensure the user is an admin of the specified budget manager
        budget_manager = get_object_or_404(BudgetManager, id=budget_manager_id)
        if budget_manager.admin != user:
            raise PermissionDenied('You do not have permission to add users to this budget manager.')

        # Restrict the role to 'read_only'
        if role != UserAccess.READ_ONLY:
            raise PermissionDenied('You can only assign the read_only role.')

        serializer.save()

# Handle PUT requests to UserAccess
# Authenticated users can change UserAccess entries only when these relate to the households that the authenticated user is an admin of
# can only change the "role" value to "read_only" or "edit"
class UserAccessUpdateView(generics.UpdateAPIView):
    queryset = UserAccess.objects.all()
    serializer_class = UserAccessSerializer
    permission_classes = [IsAuthenticated, IsAdminOfBudgetManager]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset.all()
        return self.queryset.filter(budget_manager__admin=user)

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        new_role = self.request.data.get('role')

        # Check if the user is an admin of the budget manager
        budget_manager = instance.budget_manager
        if budget_manager.admin != user:
            raise PermissionDenied('You do not have permission to update this UserAccess entry.')

        # Prevent setting the role to 'admin'
        if new_role == UserAccess.ADMIN:
            raise PermissionDenied('You cannot assign the admin role.')

        # Enforce role transition rules
        if instance.role == UserAccess.READ_ONLY and new_role != UserAccess.EDIT:
            raise PermissionDenied('You can only change the \"read_only\" role to \"edit\".')
        if instance.role == UserAccess.EDIT and new_role != UserAccess.READ_ONLY:
            raise PermissionDenied('You can only change the \"edit\" role to \"read_only\".')
        
        # Prevent admin from downgrading their own role
        if instance.user == user:
            raise PermissionDenied('You cannot change your own role.')

        
        serializer.save()

# Handle DELETE requests to UserAccess
# Authenticated users can remove UserAccess entries for users that have access to the household budgets they administer
# Administrator can't remove his own UserAccess entry
class UserAccessDeleteView(generics.DestroyAPIView):
    queryset = UserAccess.objects.all()
    serializer_class = UserAccessSerializer
    permission_classes = [IsAuthenticated, IsAdminOfRelatedBudgetManager]

    def perform_destroy(self, instance):
        # Prevent admin from deleting their own UserAccess entry
        if instance.user == self.request.user and instance.role == UserAccess.ADMIN:
            raise PermissionDenied('You cannot remove your own admin access.')

        if not (self.request.user == instance.budget_manager.admin or self.request.user.is_superuser):
            raise PermissionDenied('You do not have permission to delete this user access.')

        instance.delete()

class AccessRequestListCreateView(generics.ListCreateAPIView):
    queryset = AccessRequest.objects.all()
    serializer_class = AccessRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset.all()
        return self.queryset.filter(budget_manager__admin=user)

    def perform_create(self, serializer):
        requested_user_id = self.request.data.get('user')
        if requested_user_id != self.request.user.id:
            raise PermissionDenied("You cannot create an access request on behalf of another user.")
        
        budget_manager_id = self.request.data.get('budget_manager')
        budget_manager = get_object_or_404(BudgetManager, id=budget_manager_id)

        if UserAccess.objects.filter(user=self.request.user, budget_manager=budget_manager).exists():
            raise PermissionDenied({'detail': 'You already have access to this budget manager.'})
        
        if AccessRequest.objects.filter(user=self.request.user, budget_manager=budget_manager, status=AccessRequest.PENDING).exists():
            raise PermissionDenied({'detail': 'You have already requested access to this budget manager.'})

        serializer.save(user=self.request.user, budget_manager=budget_manager)

class AccessRequestUpdateView(generics.UpdateAPIView):
    queryset = AccessRequest.objects.all()
    serializer_class = AccessRequestSerializer
    permission_classes = [IsAuthenticated, IsAdminOfBudgetManager]

    def perform_update(self, serializer):
        access_request = self.get_object()
        if access_request.status != AccessRequest.PENDING:
            raise PermissionDenied('This access request has already been processed.')

        if serializer.validated_data['status'] == AccessRequest.ACCEPTED:
            UserAccess.objects.create(
                user=access_request.user,
                budget_manager=access_request.budget_manager,
                role=UserAccess.READ_ONLY
            )

        serializer.save()