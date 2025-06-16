from django.core.management.base import BaseCommand
from words.models import EnglishWord

class Command(BaseCommand):
    help = 'Deletes all EnglishWord objects from the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Deletes all words without prompting for confirmation.',
        )

    def handle(self, *args, **options):
        if not options['no_input']:
            confirm = input("Are you sure you want to delete ALL words from the database? This action cannot be undone. (yes/N): ")
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING("Operation cancelled by user."))
                return

        count, _ = EnglishWord.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} words from the database."))