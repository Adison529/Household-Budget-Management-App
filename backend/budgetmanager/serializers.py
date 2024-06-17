from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import OperationCategory, OperationType, BudgetManager, Operation, UserAccess, AccessRequest

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

class OperationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationCategory
        fields = '__all__'

class OperationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationType
        fields = '__all__'

class BudgetManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetManager
        fields = '__all__'
        read_only_fields = ['id', 'unique_id', 'admin']

    def validate_name(self, value):
        request = self.context['request']
        user = request.user

        if self.instance and self.instance.name == value:
            raise serializers.ValidationError("The new name cannot be the same as the current name.")
        
        if BudgetManager.objects.filter(admin=user, name=value).exists():
            raise serializers.ValidationError("You already have a budget with this name.")
        return value

class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = '__all__'
        read_only_fields = ['budget_manager']
        
    def validate_by(self, value):
        request = self.context.get('request')
        budget_manager_id = self.context['view'].kwargs.get('budget_manager_id')
        
        # Check if the user specified in 'by' is a member of the BudgetManager
        try:
            budget_manager = BudgetManager.objects.get(id=budget_manager_id)
        except BudgetManager.DoesNotExist:
            raise serializers.ValidationError("Invalid budget_manager_id.")
        
        if not UserAccess.objects.filter(user=value, budget_manager=budget_manager).exists():
            raise serializers.ValidationError("The specified user is not a member of this budget manager.")
        
        return value
    
    def validate(self, data):
        # Check if 'category' is provided in the request data
        if self.context['request'].method == 'POST':  # Check if method is POST
            if 'category' not in data:
                raise serializers.ValidationError({'category': 'This field is required.'})

        return data
    
    def create(self, validated_data):
        # Fetch budget_manager_id from view kwargs (URL parameter)
        budget_manager_id = self.context['view'].kwargs.get('budget_manager_id')

        # Retrieve the BudgetManager object based on budget_manager_id
        try:
            budget_manager = BudgetManager.objects.get(id=budget_manager_id)
        except BudgetManager.DoesNotExist:
            raise serializers.ValidationError("Invalid budget_manager_id.")

        # Assign the budget_manager to the validated data
        validated_data['budget_manager'] = budget_manager

        # Create and return the Operation object
        return Operation.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class UserAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccess
        fields = '__all__'
        read_only_fields = ['budget_manager']

    def validate(self, data):
        request = self.context['request']
        budget_manager_id = self.context['view'].kwargs['budget_manager_id']
        user = request.user

        try:
            budget_manager = BudgetManager.objects.get(id=budget_manager_id)
        except BudgetManager.DoesNotExist:
            raise serializers.ValidationError("BudgetManager does not exist.")

        # Check if the requesting user is the admin of the BudgetManager
        if budget_manager.admin != user or not UserAccess.objects.filter(user=user, budget_manager=budget_manager, role=UserAccess.ADMIN).exists():
            raise serializers.ValidationError("Only the admin can add user access.")
        
        # Check if 'role' is not provided or is set to 'admin' or 'edit'
        if request.data.get('role') in ['admin', 'edit']:
            raise serializers.ValidationError("Role cannot be set to 'admin' or 'edit'.")
        
        # Automatically set 'role' to 'read_only'
        data['role'] = UserAccess.READ_ONLY

        # Check if a UserAccess object already exists for the given user and budget_manager
        user_id = data['user'].id
        if UserAccess.objects.filter(budget_manager_id=budget_manager_id, user_id=user_id).exists():
            raise serializers.ValidationError("User already has access to this budget manager.")

        return data
    
class UserAccessUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccess
        fields = ['role']

    def validate_role(self, value):
        if value not in [UserAccess.READ_ONLY, UserAccess.EDIT]:
            raise serializers.ValidationError("Role can only be changed to 'read_only' or 'edit'.")
        return value

    def validate(self, data):
        request = self.context['request']
        budget_manager_id = self.context['view'].kwargs['budget_manager_id']
        user = request.user
        
        # Ensure the user making the request is the admin of the BudgetManager
        try:
            budget_manager = BudgetManager.objects.get(id=budget_manager_id)
        except BudgetManager.DoesNotExist:
            raise serializers.ValidationError("BudgetManager does not exist.")
        
        if budget_manager.admin != user:
            raise serializers.ValidationError("Only the admin can change user roles.")

        # Prevent admin from downgrading their own role
        user_access_instance = self.instance
        if user_access_instance.user == user and user_access_instance.role == UserAccess.ADMIN:
            raise serializers.ValidationError("Admin cannot downgrade their own role.")
        
        return data

    # def __init__(self, *args, **kwargs):
    #     # Exclude 'role' field if specified in context
    #     exclude_fields = kwargs.pop('exclude_fields', [])
    #     super().__init__(*args, **kwargs)

    #     if 'role' in exclude_fields:
    #         self.fields.pop('role')

#class AccessRequestSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = AccessRequest
#        fields = '__all__'

# class AccessRequestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AccessRequest
#         fields = '__all__'
#         #read_only_fields = ('user', 'budget_manager', 'created_at', 'updated_at', 'status')

#     #def update(self, instance, validated_data):
#     #    if 'status' in validated_data:
#     #        new_status = validated_data['status']
#     #        if new_status == AccessRequest.ACCEPTED and instance.status == AccessRequest.PENDING:
#     #            UserAccess.objects.create(user=instance.user, budget_manager=instance.budget_manager, role=UserAccess.READ_ONLY)
#     #    return super().update(instance, validated_data)

# class AccessRequestSerializer(serializers.ModelSerializer):
#     unique_id = serializers.UUIDField(write_only=True)

#     class Meta:
#         model = AccessRequest
#         fields = ['id', 'user', 'budget_manager', 'status', 'created_at', 'updated_at', 'unique_id']
#         read_only_fields = ['id', 'user', 'budget_manager', 'status', 'created_at', 'updated_at']

#     def create(self, validated_data):
#         unique_id = validated_data.pop('unique_id')
#         budget_manager = get_object_or_404(BudgetManager, unique_id=unique_id)
#         user = self.context['request'].user  # Get the user from the request context
#         return AccessRequest.objects.create(user=user, budget_manager=budget_manager, **validated_data)

class AccessRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRequest
        fields = ['id', 'user', 'budget_manager', 'status', 'created_at', 'updated_at']
        read_only_fields = ['budget_manager', 'status', 'created_at', 'updated_at']

class AccessRequestCreateSerializer(serializers.ModelSerializer):
    unique_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = AccessRequest
        fields = ['unique_id']

    def validate(self, data):
        request = self.context['request']
        user = request.user
        unique_id = data.get('unique_id')

        try:
            budget_manager = BudgetManager.objects.get(unique_id=unique_id)
        except BudgetManager.DoesNotExist:
            raise serializers.ValidationError("BudgetManager does not exist with the provided unique_id.")

        # Check for existing pending access request
        if AccessRequest.objects.filter(user=user, budget_manager=budget_manager, status=AccessRequest.PENDING).exists():
            raise serializers.ValidationError("There is already a pending access request for this user.")

        # Check for existing user access
        if UserAccess.objects.filter(user=user, budget_manager=budget_manager).exists():
            raise serializers.ValidationError("User already has access to this budget manager.")

        data['budget_manager'] = budget_manager
        return data

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        budget_manager = validated_data['budget_manager']
        return AccessRequest.objects.create(user=user, budget_manager=budget_manager)

class AccessRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRequest
        fields = ['status']

    def validate_status(self, value):
        if value not in [AccessRequest.ACCEPTED, AccessRequest.DENIED]:
            raise serializers.ValidationError("Status must be either 'accepted' or 'denied'.")
        return value

    def update(self, instance, validated_data):
        request = self.context['request']
        user = request.user
        budget_manager_id = self.context['view'].kwargs['budget_manager_id']

        try:
            budget_manager = BudgetManager.objects.get(id=budget_manager_id)
        except BudgetManager.DoesNotExist:
            raise serializers.ValidationError("BudgetManager does not exist.")

        if budget_manager.admin != user:
            raise serializers.ValidationError("Only the admin can update access requests.")

        instance.status = validated_data.get('status', instance.status)
        instance.save()

        # If status is accepted, create a UserAccess entry
        if instance.status == AccessRequest.ACCEPTED:
            UserAccess.objects.create(
                user=instance.user,
                budget_manager=instance.budget_manager,
                role=UserAccess.READ_ONLY
            )

        return instance