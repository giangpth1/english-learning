from django.contrib import admin
from .models import EnglishWord

@admin.register(EnglishWord)
class EnglishWordAdmin(admin.ModelAdmin):
    list_display = (
        'english_word', 
        'vietnamese_translation_1', 
        'vietnamese_translation_2', 
        'vietnamese_translation_3', 
        'vietnamese_translation_4', 
        'vietnamese_translation_5'
    )
    search_fields = ('english_word', 'vietnamese_translation_1', 'vietnamese_translation_2', 'vietnamese_translation_3', 'vietnamese_translation_4', 'vietnamese_translation_5')