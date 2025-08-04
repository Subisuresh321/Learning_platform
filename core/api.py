from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .agents import quiz_agent, translation_agent, learning_agent
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from .models import StudentProfile
# Generate quiz based on topic or document

@api_view(['POST'])
def generate_quiz(request):
    print("hai")
    topic = request.data.get('topic')
    if not topic:
        return Response({"error": "Topic is required"}, status=status.HTTP_400_BAD_REQUEST)

    quiz = quiz_agent(topic)
    return Response({'quiz': quiz})

# Translate text to preferred language
@api_view(['POST'])
def translate_text(request):
    text = request.data.get('text')
    lang = request.data.get('lang')

    if not text or not lang:
        return Response({'error': 'Text and language are required'}, status=status.HTTP_400_BAD_REQUEST)

    translated = translation_agent(text, lang)
    return Response({'translated': translated})

# Get personalized learning plan
# core/api.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import StudentProfile
from .agents import learning_agent


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_learning_plan(request):
    try:
        student = request.user.studentprofile
    except StudentProfile.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

    # Corrected: Get the nested 'progress' dictionary first
    progress_data = request.data.get('progress', {})
    
    # Corrected: Then get 'last_topic' from the 'progress' dictionary
    last_topic = progress_data.get('last_topic', '')

    # Save the user's input to the student profile
    student.last_quiz_topic = last_topic
    
    # Use the student's score and the user-provided topic
    progress = {
        "score": student.score,
        "last_topic": student.last_quiz_topic
    }

    recommendation = learning_agent(progress)
    student.last_quiz_topic = recommendation.get("focus","N/A")
    student.save()
    return Response({
        "level": recommendation.get("level", "N/A"),
        "focus": recommendation.get("focus", "N/A"),
        "translated_message": recommendation.get("translated_message", recommendation.get("message", "")),
        "explanation": recommendation.get("explanation", "No explanation available")
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_progress(request):
    """
    API endpoint to update the logged-in user's score based on a quiz result.
    The score is sent in the POST request body.
    """
    score = request.data.get("score")
    if score is None:
        return Response({'error': 'Score is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Access the logged-in user's StudentProfile
    try:
        student = request.user.studentprofile
    except StudentProfile.DoesNotExist:
        # Handle case where a user exists but a profile doesn't
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Use += to add the new score to the existing score
        student.score += int(score)
        student.save()
    except (ValueError, TypeError):
        return Response({'error': 'Invalid score format. Must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'message': 'Progress updated successfully', 
        'total_score': student.score
    }, status=status.HTTP_200_OK)
