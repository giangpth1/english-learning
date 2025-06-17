from django.db import models
from django.contrib.auth.models import User

class DifficultyLevel(models.TextChoices):
    EASY = 'easy', 'Easy'
    MEDIUM = 'medium', 'Medium'
    # Thêm các cấp độ khác nếu cần
    # HARD = 'hard', 'Hard'

class HighScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='highscores') # Thay OneToOneField thành ForeignKey
    difficulty = models.CharField(
        max_length=10,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.EASY
    )
    score = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "High Score"
        verbose_name_plural = "High Scores"
        unique_together = ('user', 'difficulty') # Đảm bảo mỗi user chỉ có 1 high score cho mỗi difficulty

    def __str__(self):
        return f"{self.user.username} - {self.get_difficulty_display()}: {self.score}"