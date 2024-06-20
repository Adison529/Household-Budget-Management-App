from rest_framework import generics, status
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import JsonResponse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from .models import OperationCategory, OperationType, BudgetManager, Operation, UserAccess, AccessRequest
from .serializers import OperationCategorySerializer, OperationTypeSerializer # Serializers for OperationCategory and OperationType
from .serializers import BudgetManagerSerializer # Serializer for BudgetManager
from .serializers import OperationSerializer, OperationListSerializer # Serializers for Operation
from .serializers import UserAccessSerializer, UserAccessUpdateSerializer # Serializers for UserAccess
from .serializers import AccessRequestSerializer, AccessRequestCreateSerializer, AccessRequestUpdateSerializer # Serializers for AccessRequest
from .permissions import IsUnauthenticated, IsAuthenticated, IsBudgetEditorOrAdmin, IsAdminOfBudgetManager, IsAdminOfRelatedBudgetManager, IsBudgetMember

# user registration
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsUnauthenticated]
    serializer_class = RegisterSerializer

# user log in
# custom TokenObtain due to the addition of username to the token
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [IsUnauthenticated]
    serializer_class = CustomTokenObtainPairSerializer

class EmailConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Invalid user ID'}, status=400)

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return JsonResponse({'status': 'success', 'message': 'Email confirmed successfully'})
        else:
            if user is not None:
                user.delete()
            return JsonResponse({'status': 'error', 'message': 'Invalid or expired token'}, status=400)
        
class OperationCategoryListView(generics.ListAPIView):
    queryset = OperationCategory.objects.all()
    serializer_class = OperationCategorySerializer
    permission_classes = [IsAuthenticated]

class OperationTypeListView(generics.ListAPIView):
    queryset = OperationType.objects.all()
    serializer_class = OperationTypeSerializer
    permission_classes = [IsAuthenticated]

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
        instance = serializer.save()
        # Create UserAccess entry for admin role
        UserAccess.objects.create(user=self.request.user, budget_manager=instance, role=UserAccess.ADMIN)
    
class BudgetManagerUpdateView(generics.UpdateAPIView):
    queryset = BudgetManager.objects.all()
    serializer_class = BudgetManagerSerializer
    permission_classes = [IsAuthenticated, IsAdminOfBudgetManager]
    
class BudgetManagerDeleteView(generics.DestroyAPIView):
    queryset = BudgetManager.objects.all()
    serializer_class = BudgetManagerSerializer
    permission_classes = [IsAuthenticated, IsAdminOfBudgetManager]

class OperationListView(generics.ListAPIView):
    serializer_class = OperationListSerializer
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

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

class UserAccessCreateView(generics.CreateAPIView):
    serializer_class = UserAccessSerializer
    permission_classes = [IsAuthenticated, IsBudgetEditorOrAdmin]
    
    def perform_create(self, serializer):
        budget_manager_id = self.kwargs['budget_manager_id']
        serializer.save(budget_manager_id=budget_manager_id)

class UserAccessUpdateView(UpdateModelMixin, generics.GenericAPIView):
    queryset = UserAccess.objects.all()
    serializer_class = UserAccessUpdateSerializer
    permission_classes = [IsAuthenticated, IsBudgetEditorOrAdmin]

    def get_queryset(self):
        budget_manager_id = self.kwargs['budget_manager_id']
        return UserAccess.objects.filter(budget_manager_id=budget_manager_id)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class UserAccessDeleteView(generics.DestroyAPIView):
    queryset = UserAccess.objects.all()
    serializer_class = UserAccessSerializer
    permission_classes = [IsAuthenticated, IsAdminOfRelatedBudgetManager]

    def perform_destroy(self, instance):
        user = instance.user
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