from django.urls import path
from .views import RegisterView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
#from .views import OperationCategoryListCreateView
from .views import OperationCategoryListView, OperationTypeListView
#from .views OperationTypeListCreateView
from .views import BudgetManagerListCreateView, BudgetManagerUpdateView, BudgetManagerDeleteView, BudgetManagerMembersView
# from .views import OperationListCreateView
from .views import OperationListView, OperationCreateView, OperationUpdateView, OperationDeleteView
#from .views import UserAccessListCreateView
from .views import UserAccessListView, UserAccessCreateView, UserAccessUpdateView, UserAccessDeleteView
#from .views import AccessRequestListCreateView
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

    path('budget-managers/<int:budget_manager_id>/access-requests/', AccessRequestListView.as_view(), name='access-request-list'), # GET for access requests
    path('access-requests/send/', AccessRequestCreateView.as_view(), name='access-request-create'), # POST for access requests
    path('budget-managers/<int:budget_manager_id>/access-requests/<int:pk>/edit/', AccessRequestUpdateView.as_view(), name='access-request-update'), # PUT for access requests 
    # (there's no DELETE for access requests because access requests can have status of "pending", "accepted", "denied")
]

# ############# APP LORE #############
# Unauthorized user should have access to register/ and login/ endpoints only
# I'm unsure of what is token/refresh/ for yet and if it's even necessary
#
# Authenticated user shall be able to retrieve a list of budget managers for household that they're a part of or create a new household budget manager (budget-managers/)
# Each budget manager can have it's name modified (budget-managers/<int:pk>/edit/ where pk is the id of a budget manager that's meant to be modified)
#       the user trying to send the request must either have an "edit" or "admin" role assigned in UserAccess for the household they're trying to modify
# Each budget manager can be deleted only by the administrator of the manager themselves (budget-managers/<int:pk>/delete/ where pk is the id of a budget manager that's meant to be deleted)
#
# Authentiacted user shall be able to retrieve a list of operations within a household budget that they're viewing (budget-managers/<int:budget_manager_id>/operations/)
# Authenticated user shall be able to add an operation to a household budget (budget-managers/<int:budget_manager_id>/operations/) as long as they have an "edit" or "admin" role
#   in that budget (they need to have "edit" or "admin" role in UserAccess entry that has their UID and the ID of the household they're trying to add an operation to)
# Authenticated user should be able to modify operations as long as they have "edit" or "admin" role in the household which the operation they're trying to alter is associated with
#   not all fields are required, they can modify only one field if they want to; the fields that can be modified are "type", "date", "title", "category", "value"
#   (budget-managers/<int:budget_manager_id>/operations/<int:pk>/edit/ where pk is the id of the operation they're trying to edit)
# Authenticated user should be able to delete operations in a budget manager if they have an editor or admin role in that household
#   budget-managers/<int:budget_manager_id>/operations/<int:pk>/delete/
# 
# Authenticated user can retrieve the list of households they have an access to (user-access/)
#   POST request to the user-access/ endpoint should not be performed manually, it is meant to be done automatically when an access request is accepted
# Admin (ofc authenticated) of a household budget manager should be able to edit the access level for an user that is a part of the household they administer
#   (user-access/<int:pk>/ where pk is the id of the UserAccess entry)
# Admin (ofc authenticated) of a household should be able to revoke access (delete user's entry for their household from UserAccess table)
#   (user-access/delete/<int:pk>/ where pk is the id of the UserAccess entry)
#
# Admin (ofc authenticated) of a household should be able to retrieve access requests to the household they own (access-requests/)
# Authenticated user shall be able to request an access to a household they don't have an access to nor they have a pending access request already (access-requests/)
# Admin (ofc authenticated) of a household should be able to accept or deny access requests (access-requests/<int:pk>/ where pk is the ID of AccessRequest entry that's meant to be modified)