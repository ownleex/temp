"""django_user_handler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.authtoken.views import obtain_auth_token
from core.views import health_check



urlpatterns = [
	path('users/health/', health_check, name='health_check'),
    path('users/api-auth/', include('rest_framework.urls')),
    path('users/admin/', admin.site.urls),
    path('users/', include('core.urls')),
    path('users/api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/api-token-auth/', obtain_auth_token),
    path('users/social/', include('social_django.urls', namespace='social')),
]

