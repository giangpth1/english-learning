from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .viewsets import RandomWordQuizView, EnglishWordViewSet

app_name = 'words'

# Create a router and register our viewsets with it.
# This router will be imported and included in the project's main urls.py under the /api/ prefix
words_api_router = DefaultRouter() # Rename router
words_api_router.register(r'words', EnglishWordViewSet, basename='word') # Register at 'words'

urlpatterns = [
    path('', RandomWordQuizView.as_view(), name='random_word_quiz'),
    # The API URLs are now determined automatically by the router.
    # Remove the inclusion of the router here:
]