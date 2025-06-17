from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import HighScore
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        label="Mật khẩu"
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label="Xác nhận mật khẩu"
    )
    email = serializers.EmailField(
        required=True,
        label="Địa chỉ Email"
    )

    class Meta:
        model = User
        # Các trường sẽ được sử dụng để tạo user và trả về (trừ password, password2)
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False, 'label': "Tên"},
            'last_name': {'required': False, 'label': "Họ"}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Mật khẩu xác nhận không khớp."})

        # Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Địa chỉ email này đã được sử dụng."})

        # Kiểm tra username đã tồn tại chưa
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "Tên đăng nhập này đã tồn tại."})
        return attrs

    def create(self, validated_data):
        # Tạo user mới với password đã được hash
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'], # create_user sẽ hash mật khẩu
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        # Không cần gọi user.set_password() nữa vì create_user đã làm
        # user.save() cũng không cần vì create_user đã lưu
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Bạn có thể thêm custom claims vào token ở đây nếu muốn
        # token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Thêm thông tin người dùng vào response data
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name
        }
        return data

class UserForHighScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class HighScoreSerializer(serializers.ModelSerializer):
    """
    Serializer để hiển thị HighScore.
    """
    user = UserForHighScoreSerializer(read_only=True)

    class Meta:
        model = HighScore
        fields = ['id', 'user', 'difficulty', 'score', 'updated_at']

class HighScoreUpdateSerializer(serializers.Serializer):
    """
    Serializer để xác thực dữ liệu đầu vào khi cập nhật score.
    """
    score = serializers.IntegerField(min_value=0, help_text="Điểm số mới, phải là số nguyên không âm.")
