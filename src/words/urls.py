from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .viewsets import RandomWordQuizView, EnglishWordViewSet

app_name = 'words'

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'api/words', EnglishWordViewSet, basename='word-api')

urlpatterns = [
    path('', RandomWordQuizView.as_view(), name='random_word_quiz'),
    # The API URLs are now determined automatically by the router.
    path('', include(router.urls)),
]