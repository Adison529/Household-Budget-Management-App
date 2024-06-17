from django.urls import path
from .views import RegisterView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import OperationCategoryListView, OperationTypeListView
from .views import BudgetManagerListCreateView, BudgetManagerUpdateView, BudgetManagerDeleteView, BudgetManagerMembersView
from .views import OperationListView, OperationCreateView, OperationUpdateView, OperationDeleteView
from .views import UserAccessListView, UserAccessCreateView, UserAccessUpdateView, UserAccessDeleteView
from .views import AccessRequestListView, AccessRequestCreateView, AccessRequestUpdateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # new categories/types should be added via Django admin panel
    path('operation-categories/', OperationCategoryListView.as_view(), name='operation_category_list'), # GET for operation categories
    path('operation-types/', OperationTypeListView.as_view(), name='operation_type_list'), # GET for operation types

    path('budget-managers/', BudgetManagerListCreateView.as_view(), name='budget_manager_list_create'), # GET & POST for household budget managers
    path('budget-managers/<int:pk>/edit/', BudgetManagerUpdateView.as_view(), name='budget-manager-update'), # PUT for household budget managers
    path('budget-managers/<int:pk>/delete/', BudgetManagerDeleteView.as_view(), name='budget-manager-delete'), # DELETE for household budget managers

    path('budget-managers/<int:budget_manager_id>/members/', BudgetManagerMembersView.as_view(), name='budget-manager-members'), # GET for members of a household budget

    path('budget-managers/<int:budget_manager_id>/operations/', OperationListView.as_view(), name='operation-list'), # GET for operations within a household with id of budget_manager_id
    path('budget-managers/<int:budget_manager_id>/operations/add/', OperationCreateView.as_view(), name='operation-create'), # POST for operations
    path('budget-managers/<int:budget_manager_id>/operations/<int:pk>/edit/', OperationUpdateView.as_view(), name='operation-edit'), # PATCH for operations
    path('budget-managers/<int:budget_manager_id>/operations/<int:pk>/delete/', OperationDeleteView.as_view(), name='operation-delete'), # DELETE for operations

    path('budget-managers/<int:budget_manager_id>/user-access/', UserAccessListView.as_view(), name='user_access_list'), # GET for user access
    path('budget-managers/<int:budget_manager_id>/user-access/add/', UserAccessCreateView.as_view(), name='user_access_create'), # POST for user access
    path('budget-managers/<int:budget_manager_id>/user-access/<int:pk>/edit/', UserAccessUpdateView.as_view(), name='user-access-update'), # PUT for user access
    path('budget-managers/<int:budget_manager_id>/user-access/<int:pk>/delete/', UserAccessDeleteView.as_view(), name='user-access-delete'), # DELETE for user access

    path('access-requests/send/', AccessRequestCreateView.as_view(), name='access-request-create'), # POST for access requests
    path('budget-managers/<int:budget_manager_id>/access-requests/', AccessRequestListView.as_view(), name='access-request-list'), # GET for access requests
    path('budget-managers/<int:budget_manager_id>/access-requests/<int:pk>/edit/', AccessRequestUpdateView.as_view(), name='access-request-update'), # PUT for access requests 
    # (there's no DELETE for access requests because access requests can have status of "pending", "accepted", "denied")
]