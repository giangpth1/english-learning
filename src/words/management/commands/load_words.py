from django.core.management.base import BaseCommand
from words.models import EnglishWord # Ensure you import the correct model
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Loads words from wordlist.txt into the EnglishWord model, handling multiple translations.'

    def handle(self, *args, **options):
        # Assume wordlist.txt is in the same directory as manage.py or in the project root
        # Adjust this path if your file is in a different location
        file_path = os.path.join(settings.BASE_DIR, 'wordlist.txt')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Wordlist file not found at {file_path}'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line or '__' not in line:
                    self.stdout.write(self.style.WARNING(f'Skipping malformed line {line_number}: "{line}"'))
                    continue

                english_part, vietnamese_part = line.split('__', 1)
                english_word_str = english_part.strip()
                
                # Split Vietnamese meanings by '--'
                vietnamese_translations_list = [trans.strip() for trans in vietnamese_part.split('--') if trans.strip()]

                if not english_word_str or not vietnamese_translations_list:
                    self.stdout.write(self.style.WARNING(f'Skipping line {line_number} due to empty English word or translations: "{line}"'))
                    continue

                # Prepare data for the model, up to 5 meanings
                word_data = {
                    'vietnamese_translation_1': vietnamese_translations_list[0] if len(vietnamese_translations_list) > 0 else None,
                    'vietnamese_translation_2': vietnamese_translations_list[1] if len(vietnamese_translations_list) > 1 else None,
                    'vietnamese_translation_3': vietnamese_translations_list[2] if len(vietnamese_translations_list) > 2 else None,
                    'vietnamese_translation_4': vietnamese_translations_list[3] if len(vietnamese_translations_list) > 3 else None,
                    'vietnamese_translation_5': vietnamese_translations_list[4] if len(vietnamese_translations_list) > 4 else None,
                }

                try:
                    obj, created = EnglishWord.objects.update_or_create(
                        english_word=english_word_str,
                        defaults=word_data
                    )
                    action = "Created" if created else "Updated"
                    self.stdout.write(self.style.SUCCESS(f'{action} word: {english_word_str}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing line {line_number} ({english_word_str}): {e}'))
        self.stdout.write(self.style.SUCCESS('Finished loading words from wordlist.txt.'))