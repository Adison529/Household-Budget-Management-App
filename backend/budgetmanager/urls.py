from django.urls import path
from .views import RegisterView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import OperationCategoryListCreateView, OperationTypeListCreateView, BudgetManagerListCreateView, BudgetManagerUpdateView, BudgetManagerDeleteView
from .views import OperationListCreateView, UserAccessListCreateView, UserAccessUpdateView, UserAccessDeleteView, AccessRequestListCreateView, AccessRequestUpdateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('operation-categories/', OperationCategoryListCreateView.as_view(), name='operation_category_list_create'),
    path('operation-types/', OperationTypeListCreateView.as_view(), name='operation_type_list_create'),
    path('budget-managers/', BudgetManagerListCreateView.as_view(), name='budget_manager_list_create'),
    path('budget-managers/<int:pk>/', BudgetManagerUpdateView.as_view(), name='budget-manager-update'),
    path('budget-managers/delete/<int:pk>/', BudgetManagerDeleteView.as_view(), name='budget-manager-delete'),
    path('operations/', OperationListCreateView.as_view(), name='operation_list_create'),
    path('user-access/', UserAccessListCreateView.as_view(), name='user_access_list_create'),
    path('user-access/<int:pk>/', UserAccessUpdateView.as_view(), name='user-access-update'),
    path('user-access/delete/<int:pk>/', UserAccessDeleteView.as_view(), name='user-access-delete'),
    path('access-requests/', AccessRequestListCreateView.as_view(), name='access-request-list-create'),
    path('access-requests/<int:pk>/', AccessRequestUpdateView.as_view(), name='access-request-update'),
]
