from django.test import TestCase, Client
from django.urls import reverse
from .models import EnglishWord
from .forms import TranslationForm
from .viewsets import normalize_text_for_comparison, remove_vietnamese_diacritics
from django.contrib.messages import get_messages

# Create your tests here.

class HelperFunctionTests(TestCase):
    def test_remove_vietnamese_diacritics(self):
        self.assertEqual(remove_vietnamese_diacritics("Tiếng Việt"), "Tieng Viet")
        self.assertEqual(remove_vietnamese_diacritics("Chào bạn"), "Chao ban")
        self.assertEqual(remove_vietnamese_diacritics(""), "")

    def test_normalize_text_for_comparison(self):
        self.assertEqual(normalize_text_for_comparison("Tiếng Việt"), "tieng-viet")
        self.assertEqual(normalize_text_for_comparison("  Chào   bạn  "), "chao-ban")
        self.assertEqual(normalize_text_for_comparison("ĐỒNG BẰNG"), "dong-bang")
        self.assertEqual(normalize_text_for_comparison("Một-Hai Ba"), "mot-hai-ba")


class RandomWordQuizViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('words:random_word_quiz')
        self.word1 = EnglishWord.objects.create(
            english_word="Hello", 
            vietnamese_translation_1="Xin chào",
            vietnamese_translation_2="Chào bạn"
        )
        self.word2 = EnglishWord.objects.create(
            english_word="Goodbye", 
            vietnamese_translation_1="Tạm biệt"
        )

    def test_get_no_words_in_db(self):
        EnglishWord.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'random_word_quiz.html')
        self.assertContains(response, "There are no words in the database yet.")
        # Check message content more robustly
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("There are no words in the database yet." in str(m) for m in messages))
        self.assertIsInstance(response.context['form'], TranslationForm)

    def test_get_with_words_in_db(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'random_word_quiz.html')
        self.assertIn('word', response.context)
        self.assertIsInstance(response.context['word'], EnglishWord)
        self.assertIsInstance(response.context['form'], TranslationForm)
        self.assertIn('current_word_id', self.client.session)

    def test_post_no_current_word_id_in_session(self):
        # Ensure session is clean or current_word_id is not set
        session = self.client.session
        if 'current_word_id' in session:
            del session['current_word_id']
            session.save()

        response = self.client.post(self.url, {'translation': 'some answer'})
        self.assertEqual(response.status_code, 302) # Redirect
        self.assertRedirects(response, self.url)
        storage = get_messages(response.wsgi_request)
        messages = list(storage)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "The current word was not found. Please try again.")

    def test_post_word_does_not_exist(self):
        session = self.client.session
        session['current_word_id'] = 999 # Non-existent ID
        session.save()

        response = self.client.post(self.url, {'translation': 'some answer'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        storage = get_messages(response.wsgi_request)
        messages = list(storage)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "The word does not exist. Please try again.")
        self.assertNotIn('current_word_id', self.client.session)

    def test_post_correct_translation_first_meaning(self):
        session = self.client.session
        session['current_word_id'] = self.word1.id
        session.save()

        response = self.client.post(self.url, {'translation': 'Xin chào'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        storage = get_messages(response.wsgi_request)
        messages = list(storage)
        self.assertEqual(len(messages), 1)
        msg_str = str(messages[0])
        self.assertTrue("Exactly!" in msg_str)
        self.assertIn(self.word1.vietnamese_translation_1, msg_str)
        if self.word1.vietnamese_translation_2:
            self.assertIn(self.word1.vietnamese_translation_2, msg_str)
        self.assertNotIn('current_word_id', self.client.session)

    def test_post_correct_translation_second_meaning(self):
        session = self.client.session
        session['current_word_id'] = self.word1.id
        session.save()

        response = self.client.post(self.url, {'translation': 'Chào bạn'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        storage = get_messages(response.wsgi_request)
        messages = list(storage)
        self.assertEqual(len(messages), 1)
        msg_str = str(messages[0])
        self.assertTrue("Exactly!" in msg_str)
        self.assertIn(self.word1.vietnamese_translation_1, msg_str)
        if self.word1.vietnamese_translation_2:
            self.assertIn(self.word1.vietnamese_translation_2, msg_str)
        self.assertNotIn('current_word_id', self.client.session)

    def test_post_incorrect_translation(self):
        session = self.client.session
        session['current_word_id'] = self.word1.id
        session.save()
        response = self.client.post(self.url, {'translation': 'Sai rồi'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        storage = get_messages(response.wsgi_request)
        messages = list(storage)
        self.assertEqual(len(messages), 1)
        msg_str = str(messages[0])
        self.assertTrue("Incorrect." in msg_str)
        self.assertIn(self.word1.vietnamese_translation_1, msg_str)
        if self.word1.vietnamese_translation_2:
            self.assertIn(self.word1.vietnamese_translation_2, msg_str)
        self.assertIn("You entered: 'Sai rồi'", msg_str)
        self.assertNotIn('current_word_id', self.client.session)

    def test_post_invalid_form(self):
        session = self.client.session
        session['current_word_id'] = self.word1.id
        session.save()

        response = self.client.post(self.url, {'translation': ''}) # Empty translation, should be invalid
        self.assertEqual(response.status_code, 200) # Stays on the same page
        self.assertTemplateUsed(response, 'random_word_quiz.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(response.context['word'], self.word1)
        self.assertEqual(self.client.session['current_word_id'], self.word1.id) # current_word_id should still be in session
