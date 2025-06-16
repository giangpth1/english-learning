import random
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .models import EnglishWord
from .forms import TranslationForm
from rest_framework import viewsets, status, response
from unidecode import unidecode
from rest_framework import viewsets
from .serializers import EnglishWordSerializer
from rest_framework.decorators import action

def remove_vietnamese_diacritics(text):
    """
    Loại bỏ dấu tiếng Việt khỏi một chuỗi.
    """
    return unidecode(text)

def normalize_text_for_comparison(text):
    """
    Chuẩn hóa văn bản để so sánh:
    1. Chuyển thành chữ thường.
    2. Loại bỏ dấu tiếng Việt.
    3. Thay thế khoảng trắng bằng dấu gạch nối.
    """
    text = text.lower()
    text = remove_vietnamese_diacritics(text)
    text = text.replace(" ", "-")
    return text

class RandomWordQuizView(View):
    def get(self, request):
        all_words = list(EnglishWord.objects.all())
        if not all_words:
            messages.warning(request, "There are no words in the database yet. Please add some words.")
            return render(request, 'random_word_quiz.html', {'form': TranslationForm()})

        random_word = random.choice(all_words)
        request.session['current_word_id'] = random_word.id
        form = TranslationForm()
        return render(request, 'random_word_quiz.html', {'word': random_word, 'form': form})

    def post(self, request):
        form = TranslationForm(request.POST)
        current_word_id = request.session.get('current_word_id')

        if not current_word_id:
            messages.error(request, "The current word was not found. Please try again.")
            return redirect('words:random_word_quiz')

        try:
            current_word = EnglishWord.objects.get(id=current_word_id)
        except EnglishWord.DoesNotExist:
            messages.error(request, "The word does not exist. Please try again.")
            if 'current_word_id' in request.session:
                del request.session['current_word_id']
            return redirect('words:random_word_quiz')

        if form.is_valid():
            user_input_raw = form.cleaned_data['translation'].strip()
            user_translation_normalized = normalize_text_for_comparison(user_input_raw)
            
            correct_translations_raw = current_word.get_all_translations()
            correct_translations_normalized = [normalize_text_for_comparison(t.strip()) for t in correct_translations_raw if t]

            is_correct = user_translation_normalized in correct_translations_normalized

            if is_correct:
                all_meanings_str = ", ".join(filter(None, correct_translations_raw))
                messages.success(request, f"Exactly! '{current_word.english_word}' can mean '{user_input_raw}'. All correct meanings: {all_meanings_str}.")
            else:
                all_meanings_str = ", ".join(filter(None, correct_translations_raw))
                messages.error(request, f"Incorrect. The correct meanings of '{current_word.english_word}' are: '{all_meanings_str}'. You entered: '{user_input_raw}'.")
            
            if 'current_word_id' in request.session:
                del request.session['current_word_id'] 
            return redirect('words:random_word_quiz') 
        
        return render(request, 'random_word_quiz.html', {'word': current_word, 'form': form})

class EnglishWordViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows words to be viewed or edited.
    """
    queryset = EnglishWord.objects.all().order_by('-id')
    serializer_class = EnglishWordSerializer

    @action(detail=False, methods=['get'])
    def random(self, request):
        """
        Get a random English word.
        """
        words = self.get_queryset()
        if not words.exists():
            return response.Response({"detail": "No words available."}, status=status.HTTP_404_NOT_FOUND)
        random_word = random.choice(list(words)) # Convert queryset to list for random.choice
        serializer = self.get_serializer(random_word)
        return response.Response(serializer.data)

    @action(detail=True, methods=['post'])
    def check_translation(self, request, pk=None):
        """
        Check the user's translation for a specific word.
        Expects {'translation': 'user_input'} in the request body.
        """
        word = self.get_object() # Get the specific word instance based on pk

        user_input_raw = request.data.get('translation', '').strip()

        user_translation_normalized = normalize_text_for_comparison(user_input_raw)
        
        correct_translations_raw = word.get_all_translations()
        correct_translations_normalized = [normalize_text_for_comparison(t.strip()) for t in correct_translations_raw if t]

        is_correct = user_translation_normalized in correct_translations_normalized
        
        valid_raw_translations = [t for t in correct_translations_raw if t]

        return response.Response({"is_correct": is_correct, "correct_translations": valid_raw_translations})