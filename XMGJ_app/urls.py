from django.urls import path
from . import views

app_name = 'xmgj'

urlpatterns = [
    # 仪表盘
    path('', views.DashboardView.as_view(), name='dashboard'),

    # 事项 CRUD
    path('items/', views.ItemListView.as_view(), name='item_list'),
    path('items/create/', views.ItemCreateView.as_view(), name='item_create'),
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('items/<int:pk>/edit/', views.ItemUpdateView.as_view(), name='item_edit'),
    path('items/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),

    # 节点 CRUD
    path('items/<int:item_id>/nodes/create/', views.NodeCreateView.as_view(), name='node_create'),
    path('items/<int:item_id>/nodes/<int:pk>/', views.NodeDetailView.as_view(), name='node_detail'),
    path('items/<int:item_id>/nodes/<int:pk>/edit/', views.NodeUpdateView.as_view(), name='node_edit'),
    path('items/<int:item_id>/nodes/<int:pk>/delete/', views.NodeDeleteView.as_view(), name='node_delete'),

    # 步骤
    path('items/<int:item_id>/nodes/<int:node_id>/steps/create/', views.StepCreateView.as_view(), name='step_create'),
    path('items/<int:item_id>/nodes/<int:node_id>/steps/<int:pk>/edit/', views.StepUpdateView.as_view(), name='step_edit'),
    path('items/<int:item_id>/nodes/<int:node_id>/steps/<int:pk>/delete/', views.StepDeleteView.as_view(), name='step_delete'),
    path('items/<int:item_id>/nodes/<int:node_id>/steps/<int:pk>/update-status/', views.StepStatusUpdateView.as_view(), name='step_status_update'),
    path('items/<int:item_id>/nodes/<int:node_id>/steps/<int:pk>/inline-save/', views.StepInlineSaveView.as_view(), name='step_inline_save'),

    # 文件
    path('steps/<int:step_id>/files/upload/', views.FileUploadView.as_view(), name='file_upload'),
    path('files/<int:pk>/delete/', views.FileDeleteView.as_view(), name='file_delete'),

    # 认证
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
]
