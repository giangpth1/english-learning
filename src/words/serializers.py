from rest_framework import serializers
from .models import EnglishWord

class EnglishWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnglishWord
        fields = [
            'id', 
            'english_word', 
            'vietnamese_translation_1', 
            'vietnamese_translation_2', 
            'vietnamese_translation_3', 
            'vietnamese_translation_4', 
            'vietnamese_translation_5'
        ]