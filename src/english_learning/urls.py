"""
URL configuration for english_learning project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from words.urls import words_api_router # Import API router từ app words

urlpatterns = [
    path('admin/', admin.site.urls),
    # URL cho các trang web (ví dụ: trang quiz)
    path('random-english-word/', include('words.urls', namespace='words-web')), # Thêm namespace để phân biệt
    # URL cho API
    path('api/', include(words_api_router.urls)), # Bao gồm các API của app words, ví dụ: /api/words/
    path('api/users/', include('users.urls', namespace='users_api')),     # Bao gồm API đăng ký, đăng nhập
]
