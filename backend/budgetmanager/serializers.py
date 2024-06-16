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
        if self.instance and self.instance.name == value:
            raise serializers.ValidationError("The new name cannot be the same as the current name.")
        return value

class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = '__all__'
        
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class UserAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccess
        fields = '__all__'

#class AccessRequestSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = AccessRequest
#        fields = '__all__'

class AccessRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRequest
        fields = '__all__'
        #read_only_fields = ('user', 'budget_manager', 'created_at', 'updated_at', 'status')

    #def update(self, instance, validated_data):
    #    if 'status' in validated_data:
    #        new_status = validated_data['status']
    #        if new_status == AccessRequest.ACCEPTED and instance.status == AccessRequest.PENDING:
    #            UserAccess.objects.create(user=instance.user, budget_manager=instance.budget_manager, role=UserAccess.READ_ONLY)
    #    return super().update(instance, validated_data)