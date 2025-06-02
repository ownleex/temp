from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views


from django.conf import settings
from django.conf.urls.static import static

# ===========================
# DEFINITION DES URLS
# ===========================

urlpatterns = [
    # CRUD PLAYER
    path('api/register/', views.PlayerRegisterView.as_view(), name='registerView'),
    path('api/player/', views.PlayerListView.as_view(), name='player-list'),
    path('api/player/<int:pk>/', views.PlayerDetailView.as_view(), name='player-detail'),
    path('api/player/update-name/', views.PlayerUpdateNameView.as_view(), name='player-update-name'),
    path('api/player/update-PWD/', views.PlayerUpdatePWDView.as_view(), name='player-update-pwd'),
    path('api/player/update-info/', views.PlayerUpdateInfoView.as_view(), name='player-update-info'),
    path('api/player/delete/', views.PlayerDeleteView.as_view(), name='player-delete'),

    # Authentification API
    path('api/login/', views.PlayerLoginView.as_view(), name='loginView'),
    path('api/logout/', views.PlayerLogoutView.as_view(), name='logoutView'),

    # CRUD FRIENDSHIP
    path('api/friend-request/send/', views.SendFriendRequestView.as_view(), name='send-friend-request'),
    path('api/friend-request/accept/', views.FriendRequestAcceptView.as_view(), name='friend-request-accept'),
    path('api/friend-request/reject/', views.FriendRequestRejectView.as_view(), name='friend-request-reject'),
    path('api/friend-request/cancel/', views.FriendRequestCancelView.as_view(), name='cancel-friend-request'),
    path('api/friend/remove/', views.FriendRemoveView.as_view(), name='remove-friend'),
    path('api/friend/list/', views.FriendshipListView.as_view(), name='friendship-list'),

    # CRUD BLOCK
    path('api/block/add', views.BlockPlayerView.as_view(), name='block-player'),
    path('api/block/list/', views.BlockListView.as_view(), name='block-list'),
    path('api/block/remove/', views.UnblockPlayerView.as_view(), name='unblock-player'),

    # 2FA
    path('api/2fa-enable/', views.Enable2FAView.as_view(), name='enable_2fa'),  # PUT
    path('api/2fa-disable/', views.Disable2FAView.as_view(), name='disable_2fa'),  # DELETE

    #OAUTH
    path('api/auth-42/register/', views.Auth42RegisterView.as_view(), name='auth_42_register'),
    path('api/auth-42/callback/', views.Auth42CallbackView.as_view(), name='auth_42_callback'),
    path('api/auth-42/complete/', views.Auth42CompleteView.as_view(), name='auth_42_complete'),

    path('api/status/', views.StatusApi.as_view(), name='status'),
]
