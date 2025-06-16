import os
from django.core.management.base import BaseCommand, CommandError
# from english_words import get_english_words_set # No longer needed
from words.models import EnglishWord
from django.conf import settings

class Command(BaseCommand):
    help = 'Populates the database with English words from a text file and prompts for Vietnamese translations.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='wordlist.txt', # Default file name
            help='Name of the text file containing words (must be in the project root directory, e.g., src/). Each word should be on a new line.',
        )

    def handle(self, *args, **options):
        file_name = options['file']
        # BASE_DIR in settings.py usually points to the `src` directory
        # If your `manage.py` file is at `d:\Python\english-learning\src\`,
        # then settings.BASE_DIR will also be `d:\Python\english-learning\src\`
        file_path = os.path.join(settings.BASE_DIR, file_name)

        words_from_file = []
        processed_lines = 0
        added_count = 0
        skipped_malformed_count = 0
        already_exists_count = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read each line and process
                for line_number, line in enumerate(f, 1):
                    processed_lines += 1
                    line = line.strip()
                    if not line: # Skip empty line
                        continue

                    parts = line.split('__', 1) # Split only at the first "__"
                    if len(parts) == 2:
                        english_word = parts[0].strip().lower()
                        vietnamese_translation = parts[1].strip()
                        if not english_word: # Skip if the English word is empty
                            self.stdout.write(self.style.WARNING(f"Skipped line {line_number}: English word is empty in '{line}'."))
                            skipped_malformed_count +=1
                            continue
                        words_from_file.append({'english': english_word, 'vietnamese': vietnamese_translation, 'line_number': line_number, 'original_line': line})
                    else:
                        self.stdout.write(self.style.WARNING(f"Skipped line {line_number}: Malformed entry '{line}'. Expected format 'english__vietnamese'."))
                        skipped_malformed_count +=1
        except FileNotFoundError:
            raise CommandError(f"File '{file_path}' not found. Please make sure it exists.")
        except Exception as e:
            raise CommandError(f"Error reading file '{file_path}': {e}")

        if not words_from_file:
            self.stdout.write(self.style.WARNING(f"No words found in '{file_path}' or the file is empty."))
            return

        self.stdout.write(self.style.SUCCESS(f"Processed {processed_lines} lines from '{file_name}'. Found {len(words_from_file)} valid entries to attempt to add."))

        for item in words_from_file:
            english_word = item['english']
            vietnamese_translation = item['vietnamese']
            
            if not EnglishWord.objects.filter(english_word=english_word).exists():
                EnglishWord.objects.create(english_word=english_word, vietnamese_translation=vietnamese_translation)
                self.stdout.write(self.style.SUCCESS(f"Added: '{english_word}' - '{vietnamese_translation}'"))
                added_count += 1
            else:
                self.stdout.write(self.style.NOTICE(f"Word '{english_word}' already exists in the database. Skipped from line {item['line_number']}: '{item['original_line']}'."))
                already_exists_count += 1

        self.stdout.write(self.style.SUCCESS(f"Finished populating words. Added: {added_count}. Already existed: {already_exists_count}. Skipped (malformed): {skipped_malformed_count}."))