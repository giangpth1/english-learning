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

    @action(detail=False, methods=['get'], url_path='medium-quiz-choices')
    def medium_quiz_choices(self, request):
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

    @action(detail=False, methods=['get'], url_path='easy-quiz-choices') # Changed detail to False, removed pk
    def easy_quiz_choices(self, request):
        """
        Provides 3 Vietnamese translation choices for a quiz (easy difficulty).
        The API randomly selects an English word and provides:
        1. The English word itself.
        2. vietnamese_translation_1 of this randomly selected word.
        2. vietnamese_translation_1 of a different random word.
        3. vietnamese_translation_1 of another different random word.
        """
        all_words = list(EnglishWord.objects.all())
        if not all_words:
            return response.Response({"detail": "No words available in the database."}, status=status.HTTP_404_NOT_FOUND)

        current_word = random.choice(all_words)
        if not current_word.vietnamese_translation_1:
             # Or handle this case differently, e.g., pick another word
            return response.Response(
                {"detail": f"Word '{current_word.english_word}' does not have a primary Vietnamese translation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        current_word_translation = current_word.vietnamese_translation_1

        other_words = list(EnglishWord.objects.exclude(pk=current_word.pk))

        if len(other_words) < 2:
            return response.Response(
                {"detail": "Not enough other words available to generate two distinct choices."},
                status=status.HTTP_400_BAD_REQUEST
            )

        random_choices = random.sample(other_words, 2)
        
        return response.Response({
            "english_word": current_word.english_word,
            "correct_translation": current_word_translation, # Renamed for clarity
            "other_random_translations": [
                random_choices[0].vietnamese_translation_1,
                random_choices[1].vietnamese_translation_1
            ]
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='check-easy-translation')
    def check_easy_translation(self, request):
        """
        Checks if the selected Vietnamese translation for a given English word is correct.
        This is for the "easy" quiz type where choices are provided.
        Expects {'english_word': 'word', 'selected_translation': 'translation'} in the request body.
        """
        english_word_str = request.data.get('english_word')
        selected_translation_str = request.data.get('selected_translation')

        if not english_word_str or not selected_translation_str:
            return response.Response(
                {"detail": "Missing 'english_word' or 'selected_translation'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            word_obj = EnglishWord.objects.get(english_word__iexact=english_word_str)
        except EnglishWord.DoesNotExist:
            return response.Response(
                {"detail": f"Word '{english_word_str}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        correct_primary_translation = word_obj.vietnamese_translation_1
        if not correct_primary_translation:
            return response.Response(
                {"detail": f"Word '{english_word_str}' does not have a primary Vietnamese translation defined."},
                status=status.HTTP_400_BAD_REQUEST
            )

        normalized_selected = normalize_text_for_comparison(selected_translation_str.strip())
        normalized_correct = normalize_text_for_comparison(correct_primary_translation.strip())

        is_correct = (normalized_selected == normalized_correct)

        return response.Response({
            "is_correct": is_correct,
            "correct_translation": correct_primary_translation # Trả về bản dịch đúng (chưa chuẩn hóa)
        }, status=status.HTTP_200_OK)