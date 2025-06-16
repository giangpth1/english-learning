from django.db import models

class EnglishWord(models.Model):
    english_word = models.CharField(max_length=100, unique=True, verbose_name="English")
    vietnamese_translation_1 = models.CharField(max_length=255, verbose_name="Vietnamese Meaning 1")
    vietnamese_translation_2 = models.CharField(max_length=255, verbose_name="Vietnamese Meaning 2", blank=True, null=True)
    vietnamese_translation_3 = models.CharField(max_length=255, verbose_name="Vietnamese Meaning 3", blank=True, null=True)
    vietnamese_translation_4 = models.CharField(max_length=255, verbose_name="Vietnamese Meaning 4", blank=True, null=True)
    vietnamese_translation_5 = models.CharField(max_length=255, verbose_name="Vietnamese Meaning 5", blank=True, null=True)

    def __str__(self):
        return self.english_word

    def get_all_translations(self):
        translations = [self.vietnamese_translation_1]
        for i in range(2, 6):
            translation = getattr(self, f'vietnamese_translation_{i}')
            if translation:
                translations.append(translation)
        return translations

    class Meta:
        verbose_name = "English Word"
        verbose_name_plural = "English Words"