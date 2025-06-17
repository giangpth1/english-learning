from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from .serializers import UserRegisterSerializer, HighScoreSerializer, HighScoreUpdateSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User # User model đã được import
from .models import HighScore, DifficultyLevel # Import DifficultyLevel

class UserViewSet(viewsets.GenericViewSet):
    """
    ViewSet for user registration and high score management.
    """
    # Explicitly define allowed HTTP methods, ensuring 'post' is included.
    http_method_names = ['get', 'post', 'head', 'options'] # Bạn có thể thêm các phương thức khác nếu cần
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer # Default serializer

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request, *args, **kwargs):
        """
        Handles user registration.
        """
        serializer = self.get_serializer(data=request.data) # Use get_serializer
        if serializer.is_valid():
            user = serializer.save()

            # Generate tokens for the new user
            refresh = RefreshToken.for_user(user)

            user_data = { "id": user.id, "username": user.username, "email": user.email, "first_name": user.first_name, "last_name": user.last_name }

            return Response({ "user": user_data, "refresh_token": str(refresh), "access_token": str(refresh.access_token), "message": "Đăng ký tài khoản thành công!" }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_or_create_highscore(self, user, difficulty_level):
        # Validate difficulty_level (mặc dù regex trong URL đã làm một phần)
        valid_difficulties = [choice[0] for choice in DifficultyLevel.choices]
        if difficulty_level not in valid_difficulties:
            # Điều này không nên xảy ra nếu regex URL đúng, nhưng để an toàn
            raise ValueError(f"Invalid difficulty level: {difficulty_level}")

        highscore, created = HighScore.objects.get_or_create(
            user=user,
            difficulty=difficulty_level,
            defaults={'score': 0}
        )
        return highscore, created

    @action(detail=False, methods=['get', 'post'], url_path=r'highscore/(?P<difficulty_level>(easy|medium))',
            permission_classes=[IsAuthenticated], url_name='user_highscore_level') # Đặt tên cụ thể cho URL
    def highscore_level_manager(self, request, difficulty_level=None):
        """
        Lấy (GET) hoặc cập nhật (POST) high score của user cho một cấp độ cụ thể.
        """
        if request.method == 'GET':
            try:
                highscore, _ = self._get_or_create_highscore(request.user, difficulty_level)
            except ValueError as e: # Bắt lỗi từ _get_or_create_highscore nếu difficulty không hợp lệ
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            serializer = HighScoreSerializer(highscore)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            try:
                highscore, hs_just_created = self._get_or_create_highscore(request.user, difficulty_level)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            input_serializer = HighScoreUpdateSerializer(data=request.data)
            if not input_serializer.is_valid():
                return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            new_score = input_serializer.validated_data['score']

            if new_score > highscore.score:
                highscore.score = new_score
                highscore.save()
                output_serializer = HighScoreSerializer(highscore)
                return Response(output_serializer.data, status=status.HTTP_200_OK)
            else: # Điểm mới không cao hơn
                output_serializer = HighScoreSerializer(highscore)
                # Nếu record vừa được tạo và điểm mới bằng điểm mặc định (ví dụ: post score 0)
                if hs_just_created and new_score == highscore.score:
                     return Response(output_serializer.data, status=status.HTTP_201_CREATED)
                
                return Response({
                    "message": "Điểm mới không cao hơn điểm hiện tại.",
                    "current_highscore": output_serializer.data
                }, status=status.HTTP_200_OK)
        
        # Fallback, though should not be reached if methods are correctly specified in @action
        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)