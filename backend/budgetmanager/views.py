
from django.forms import ValidationError
from rest_framework import generics, status
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from .models import OperationCategory, OperationType, BudgetManager, Operation, UserAccess, AccessRequest
from .serializers import OperationCategorySerializer, OperationTypeSerializer, BudgetManagerSerializer, OperationSerializer, UserAccessSerializer, UserAccessUpdateSerializer
from .serializers import AccessRequestSerializer, AccessRequestCreateSerializer, AccessRequestUpdateSerializer
from .permissions import IsAuthenticated, IsSuperuserOrReadOnly, IsBudgetEditorOrAdmin, IsAdminOfBudgetManager, IsAdminOfRelatedBudgetManager, IsBudgetMember

# user registration
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # maybe should create new permission class IsUnauthentiacted and change it here
    serializer_class = RegisterSerializer

# user log in
# custom TokenObtain due to the addition of username to the token
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class OperationCategoryListView(generics.ListAPIView):
    queryset = OperationCategory.objects.all()
    serializer_class = OperationCategorySerializer
    permission_classes = [IsAuthenticated]

# class OperationCategoryListCreateView(generics.ListCreateAPIView):
#     queryset = OperationCategory.objects.all()
#     serializer_class = OperationCategorySerializer
#     permission_classes = [IsAuthenticated, IsSuperuserOrReadOnly]

#     # only superuser can create new operation categories
#     # operation categories are intended to be defined by the admin at the start of the web app's lifespan
#     # if any new categories should be added in the future, it should be done so via Django admin panel
#     def create(self, request, *args, **kwargs):
#         if not request.user.is_superuser:
#             return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
#         return super().create(request, *args, **kwargs)

class OperationTypeListView(generics.ListAPIView):
    queryset = OperationType.objects.all()
    serializer_class = OperationTypeSerializer
    permission_classes = [IsAuthenticated]

# class OperationTypeListCreateView(generics.ListCreateAPIView):
#     queryset = OperationType.objects.all()
#     serializer_class = OperationTypeSerializer
#     permission_classes = [IsAuthenticated, IsSuperuserOrReadOnly]

#     # only superuser can create new operation types
#     # operation types are intended to be predefined at the start of the web app's lifespan and never altered
#     def create(self, request, *args, **kwargs):
#         if not request.user.is_superuser:
#             return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
#         return super().create(request, *args, **kwargs)

class BudgetManagerMembersView(generics.ListAPIView):
    serializer_class = UserAccessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        budget_manager_id = self.kwargs['budget_manager_id']
        return UserAccess.objects.filter(budget_manager_id=budget_manager_id)

    def list(self, request, *args, **kwargs):
        budget_manager_id = self.kwargs['budget_manager_id']
        try:
            budget_manager = BudgetManager.objects.get(id=budget_manager_id)
        except BudgetManager.DoesNotExist:
            return Response({"detail": "BudgetManager does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if not UserAccess.objects.filter(budget_manager=budget_manager, user=request.user).exists():
            return Response({"detail": "You do not have access to this BudgetManager."}, status=status.HTTP_403_FORBIDDEN)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class BudgetManagerListCreateView(generics.ListCreateAPIView):
    queryset = BudgetManager.objects.all()
    serializer_class = BudgetManagerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(
            models.Q(admin=user) | models.Q(memberships__user=user)
        ).distinct()

    def perform_create(self, serializer):
        # Automatically assign current user as admin of the BudgetManager
        instance = serializer.save(admin=self.request.user)
        
        # Create UserAccess entry for admin role
        UserAccess.objects.create(user=self.request.user, budget_manager=instance, role=UserAccess.ADMIN)
    
class BudgetManagerUpdateView(generics.UpdateAPIView):
    queryset = BudgetManager.objects.all()
    serializer_class = BudgetManagerSerializer
    permission_classes = [IsAuthenticated, IsAdminOfBudgetManager]

    # def get_queryset(self):
    #     user = self.request.user
    #     return self.queryset.filter(
    #         models.Q(admin=user) | models.Q(memberships__user=user)
    #     ).distinct()
    
class BudgetManagerDeleteView(generics.DestroyAPIView):
    queryset = BudgetManager.objects.all()
    serializer_class = BudgetManagerSerializer
    permission_classes = [IsAuthenticated, IsAdminOfBudgetManager]

    # def get_object(self):
    #     # Retrieve the BudgetManager instance based on the URL parameter (pk)
    #     obj = super().get_object()
        
    #     # Check if the authenticated user is an admin of this BudgetManager
    #     user = self.request.user
    #     if user != obj.admin:
    #         raise PermissionDenied("You do not have permission to perform this action.")

    #     return obj


class OperationListView(generics.ListAPIView):
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated, IsBudgetMember]

    def get_queryset(self):
        budget_manager_id = self.kwargs['budget_manager_id']
        return Operation.objects.filter(budget_manager_id=budget_manager_id)

class OperationCreateView(generics.CreateAPIView):
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated, IsBudgetEditorOrAdmin]

    def get_serializer_context(self):
        # Include the view instance in the serializer context
        context = super().get_serializer_context()
        context['view'] = self
        return context
    
    def perform_create(self, serializer):
        budget_manager_id = self.kwargs['budget_manager_id']
        serializer.save(budget_manager_id=budget_manager_id)

# class OperationListCreateView(generics.ListCreateAPIView):
#     queryset = Operation.objects.all()
#     serializer_class = OperationSerializer
#     permission_classes = [IsAuthenticated, IsBudgetMember]

#     def get_queryset(self):
#         user = self.request.user
#         budget_manager_id = self.kwargs.get('budget_manager_id')
#         budget_manager = get_object_or_404(BudgetManager, id=budget_manager_id)
        
#         # Check if the user has access to this budget manager
#         user_access = UserAccess.objects.filter(
#             user=user, 
#             budget_manager=budget_manager
#         )
        
#         if not user_access.exists() and not user.is_superuser:
#             raise PermissionDenied("You do not have permission to view operations for this budget manager.")

#         return self.queryset.filter(budget_manager=budget_manager)
    
#     def perform_create(self, serializer):
#         budget_manager_id = self.request.data.get('budget_manager')
#         budget_manager = get_object_or_404(BudgetManager, id=budget_manager_id)
        
#         # Superusers can create operations in any budget
#         if self.request.user.is_superuser:
#             serializer.save(by=self.request.user, budget_manager=budget_manager)
#             return
        
#         # Check if user is a member with 'edit' or 'admin' role
#         user_access = UserAccess.objects.filter(
#             user=self.request.user, 
#             budget_manager=budget_manager, 
#             role__in=['edit', 'admin']
#         )
        
#         if not user_access.exists():
#             raise PermissionDenied({'detail': 'You do not have permission to perform this action.'})
        
#         serializer.save(by=self.request.user, budget_manager=budget_manager)

class OperationUpdateView(generics.UpdateAPIView):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated, IsBudgetEditorOrAdmin]

    def get_object(self):
        budget_manager_id = self.kwargs.get('budget_manager_id')
        operation_id = self.kwargs.get('pk')
        
        # Ensure the operation belongs to the budget manager
        obj = Operation.objects.filter(budget_manager_id=budget_manager_id, id=operation_id).first()
        if not obj:
            raise PermissionDenied("Operation not found in the specified budget manager.")

        return obj
    
    # def get_object(self):
    #     obj = super().get_object()
    #     user = self.request.user
    #     budget_manager = obj.budget_manager

    #     if user.is_superuser:
    #         return obj

    #     user_access = UserAccess.objects.filter(
    #         user=user,
    #         budget_manager=budget_manager,
    #         role__in=['edit', 'admin']
    #     )

    #     if not user_access.exists():
    #         raise PermissionDenied("You do not have permission to edit this operation.")

    #     return obj
    
class OperationDeleteView(generics.DestroyAPIView):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated, IsBudgetEditorOrAdmin]

    def get_object(self):
        budget_manager_id = self.kwargs.get('budget_manager_id')
        operation_id = self.kwargs.get('pk')
        
        # Ensure the operation belongs to the budget manager
        obj = Operation.objects.filter(budget_manager_id=budget_manager_id, id=operation_id).first()
        if not obj:
            raise PermissionDenied("Operation not found in the specified budget manager.")

        return obj

    # def get_object(self):
    #     obj = super().get_object()
    #     user = self.request.user
    #     budget_manager = obj.budget_manager

    #     if user.is_superuser:
    #         return obj

    #     user_access = UserAccess.objects.filter(
    #         user=user,
    #         budget_manager=budget_manager,
    #         role__in=['edit', 'admin']
    #     )

    #     if not user_access.exists():
    #         raise PermissionDenied("You do not have permission to delete this operation.")

    #     return obj

# Handle GET and POST requests to UserAccess
# Authenticated users can retrieve UserAccess data only for households they are a member of (NOT IMPLEMENTED YET)
# Authenticated users can add new UserAccess entries only for households they are an admin of and it can be only "read_only" role
class UserAccessListView(generics.ListAPIView):
    queryset = UserAccess.objects.all()
    serializer_class = UserAccessSerializer
    permission_classes = [IsAuthenticated, IsBudgetMember]

    def get_queryset(self):
        budget_manager_id = self.kwargs.get('budget_manager_id')
        return UserAccess.objects.filter(budget_manager_id=budget_manager_id)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Check if the user is admin or editor
        user = self.request.user
        budget_manager_id = self.kwargs.get('budget_manager_id')
        user_access = UserAccess.objects.filter(user=user, budget_manager_id=budget_manager_id).first()

        # if user_access and user_access.role in ['admin', 'edit']:
        #     serializer = self.get_serializer(queryset, many=True)
        # else:
        #     # For read_only users, remove the role field from serializer
        #     serializer = UserAccessSerializer(queryset, many=True, exclude_fields=['role'])

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    # def perform_create(self, serializer):
    #     user = self.request.user
    #     budget_manager_id = self.request.data.get('budget_manager')
    #     role = self.request.data.get('role')

    #     # Ensure the user is an admin of the specified budget manager
    #     budget_manager = get_object_or_404(BudgetManager, id=budget_manager_id)
    #     if budget_manager.admin != user:
    #         raise PermissionDenied('You do not have permission to add users to this budget manager.')

    #     # Restrict the role to 'read_only'
    #     if role != UserAccess.READ_ONLY:
    #         raise PermissionDenied('You can only assign the read_only role.')

    #     serializer.save()

class UserAccessCreateView(generics.CreateAPIView):
    serializer_class = UserAccessSerializer
    permission_classes = [IsAuthenticated, IsBudgetEditorOrAdmin]
    
    def perform_create(self, serializer):
        budget_manager_id = self.kwargs['budget_manager_id']
        serializer.save(budget_manager_id=budget_manager_id)

# Handle PUT requests to UserAccess
# Authenticated users can change UserAccess entries only when these relate to the households that the authenticated user is an admin of
# can only change the "role" value to "read_only" or "edit"
class UserAccessUpdateView(UpdateModelMixin, generics.GenericAPIView):
    queryset = UserAccess.objects.all()
    serializer_class = UserAccessUpdateSerializer
    permission_classes = [IsAuthenticated, IsBudgetEditorOrAdmin]

    def get_queryset(self):
        budget_manager_id = self.kwargs['budget_manager_id']
        return UserAccess.objects.filter(budget_manager_id=budget_manager_id)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

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

class AccessRequestListView(generics.ListAPIView):
    serializer_class = AccessRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        budget_manager_id = self.kwargs['budget_manager_id']
        budget_manager = BudgetManager.objects.get(id=budget_manager_id)
        if budget_manager.admin != self.request.user:
            raise PermissionDenied("You do not have permission to view these access requests.")
        return AccessRequest.objects.filter(budget_manager_id=budget_manager_id)
    
class AccessRequestCreateView(generics.CreateAPIView):
    serializer_class = AccessRequestCreateSerializer
    permission_classes = [IsAuthenticated]

class AccessRequestUpdateView(generics.UpdateAPIView):
    serializer_class = AccessRequestUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        budget_manager_id = self.kwargs['budget_manager_id']
        return AccessRequest.objects.filter(budget_manager_id=budget_manager_id)

    def perform_update(self, serializer):
        serializer.save()


# class AccessRequestListCreateView(generics.ListCreateAPIView):
#     queryset = AccessRequest.objects.all()
#     serializer_class = AccessRequestSerializer
#     permission_classes = [IsAuthenticated]

#     # def get_queryset(self):
#     #     user = self.request.user
#     #     return self.queryset.filter(budget_manager__admin=user)
    
#     def get_queryset(self):
#         user = self.request.user
#         return self.queryset.filter(
#             models.Q(budget_manager__admin=user) | models.Q(budget_manager__memberships__user=user)
#         ).distinct()

#     # def perform_create(self, serializer):
#     #     requested_user_id = self.request.data.get('user')
#     #     if requested_user_id != self.request.user.id:
#     #         raise PermissionDenied("You cannot create an access request on behalf of another user.")
        
#     #     budget_manager_id = self.request.data.get('budget_manager')
#     #     budget_manager = get_object_or_404(BudgetManager, id=budget_manager_id)

#     #     if UserAccess.objects.filter(user=self.request.user, budget_manager=budget_manager).exists():
#     #         raise PermissionDenied({'detail': 'You already have access to this budget manager.'})
        
#     #     if AccessRequest.objects.filter(user=self.request.user, budget_manager=budget_manager, status=AccessRequest.PENDING).exists():
#     #         raise PermissionDenied({'detail': 'You have already requested access to this budget manager.'})

#     #     serializer.save(user=self.request.user, budget_manager=budget_manager)

#     def perform_create(self, serializer):
#         # Retrieve the unique_id from the request data
#         unique_id = self.request.data.get('unique_id')
#         if not unique_id:
#             raise ValidationError({'unique_id': 'This field is required.'})
        
#         # Find the BudgetManager using the unique_id
#         budget_manager = get_object_or_404(BudgetManager, unique_id=unique_id)

#         # Check if the user already has access to the BudgetManager
#         if UserAccess.objects.filter(user=self.request.user, budget_manager=budget_manager).exists():
#             raise PermissionDenied({'detail': 'You already have access to this budget manager.'})
        
#         # Check if there is already a pending access request
#         if AccessRequest.objects.filter(user=self.request.user, budget_manager=budget_manager, status=AccessRequest.PENDING).exists():
#             raise PermissionDenied({'detail': 'You have already requested access to this budget manager.'})

#         # Save the AccessRequest
#         serializer.save()

# class AccessRequestUpdateView(generics.UpdateAPIView):
#     queryset = AccessRequest.objects.all()
#     serializer_class = AccessRequestSerializer
#     permission_classes = [IsAuthenticated, IsAdminOfBudgetManager]

#     def perform_update(self, serializer):
#         access_request = self.get_object()
#         if access_request.status != AccessRequest.PENDING:
#             raise PermissionDenied('This access request has already been processed.')

#         if serializer.validated_data['status'] == AccessRequest.ACCEPTED:
#             UserAccess.objects.create(
#                 user=access_request.user,
#                 budget_manager=access_request.budget_manager,
#                 role=UserAccess.READ_ONLY
#             )

#         serializer.save()