from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import UserViewSet # Import UserViewSet từ viewsets.py
from rest_framework_simplejwt.views import (
    TokenObtainPairView, # Dùng cho API đăng nhập
    TokenRefreshView,    # Dùng để làm mới access token
    TokenVerifyView,     # Dùng để xác thực token (tùy chọn)
)
# from .views import UserHighScoreAPIView # Không dùng APIView nữa

app_name = 'users_api' # Đổi tên app_name để rõ ràng hơn cho API

router = DefaultRouter()
# Đăng ký UserViewSet với prefix 'auth'. Các actions như 'register', 'get_highscore', 'update_highscore'
# sẽ được truy cập qua /api/users/auth/register/, /api/users/auth/highscore/.
# Lưu ý: 'highscore' actions sẽ được router tự động tạo ra dựa trên @action decorators.
# Thử khởi tạo router và register trong một khối lệnh riêng biệt
# để đảm bảo không có xung đột.
router = DefaultRouter()
router.register(r'auth', UserViewSet, basename='user-auth')  # Đảm bảo dòng này nằm sau khi khởi tạo router

urlpatterns = [
    # Bao gồm các URL được tạo tự động bởi router (ví dụ: action 'register')
    path('', include(router.urls)),

    # Các API của simplejwt cho đăng nhập, làm mới và xác thực token
    # Chúng được đặt cùng prefix 'auth/' để đồng bộ với action 'register'
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
