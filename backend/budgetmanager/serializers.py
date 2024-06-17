from datetime import date
import re
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import OperationCategory, OperationType, BudgetManager, Operation, UserAccess, AccessRequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def validate_password(self, value):
        # Check if password meets complexity requirements
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        # Regex to check for at least one uppercase, one lowercase, one digit, and one special character
        if not re.search(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', value):
            raise serializers.ValidationError("Password must include at least one uppercase letter, one lowercase letter, one digit, and one special character.")
        
        return value

    def validate(self, data):
        # Check if 'username' and 'password' are provided in the request data
        required_fields = ['username', 'password']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise serializers.ValidationError({field: 'This field is required.' for field in missing_fields})

        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            #email=validated_data['email'],  # Ensure 'email' is present in validated_data
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
    admin = UserSerializer(read_only=True)

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

    def create(self, validated_data):
        request = self.context['request']
        # Automatically assign the current user as the admin
        validated_data['admin'] = request.user
        return super().create(validated_data)

class OperationListSerializer(serializers.ModelSerializer):
    by = UserSerializer()
    category = OperationCategorySerializer()
    type = OperationTypeSerializer()
    budget_manager = BudgetManagerSerializer()

    class Meta:
        model = Operation
        fields = '__all__'

class OperationSerializer(serializers.ModelSerializer):
    by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    category = serializers.PrimaryKeyRelatedField(queryset=OperationCategory.objects.all())
    type = serializers.PrimaryKeyRelatedField(queryset=OperationType.objects.all())
    budget_manager = BudgetManagerSerializer(read_only=True, required=False)

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
    
    def validate_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("The date cannot be in the future.")
        return value
    
    def validate_value(self, value):
        if value <= 0:
            raise serializers.ValidationError("The value must be greater than zero.")
        return value
    
    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'POST':
            # Check if 'category', 'type', 'date', 'title', and 'value' are provided in the request data
            required_fields = ['category', 'type', 'date', 'title', 'value']
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                raise serializers.ValidationError({field: 'This field is required.' for field in missing_fields})

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

        # Optionally set the 'by' field to the current user if not provided
        # if 'by' not in validated_data:
        #     validated_data['by'] = self.context['request'].user

        # Create and return the Operation object
        return Operation.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class UserAccessSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    budget_manager = BudgetManagerSerializer()
    
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

class AccessRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    budget_manager = BudgetManagerSerializer()
    
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