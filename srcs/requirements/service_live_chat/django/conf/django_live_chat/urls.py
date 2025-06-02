"""django_live_chat URL Configuration

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
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import health_check


urlpatterns = [
	path('live_chat/health/', health_check, name='health_check'),
    path('live_chat/admin/', admin.site.urls),
    path('live_chat/', include('core.urls')),
    path('live_chat/api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('live_chat/api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
