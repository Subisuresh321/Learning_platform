from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .agents import quiz_agent, translation_agent, learning_agent
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
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
@api_view(['POST'])
def get_learning_plan(request):
    progress = request.data.get("progress")

    if not progress:
        return Response({'error': 'Progress data is required'}, status=status.HTTP_400_BAD_REQUEST)

    recommendation = learning_agent(progress)

    return Response({
        "level": recommendation.get("level", "N/A"),
        "focus": recommendation.get("focus", "N/A"),
        "translated_message": recommendation.get("translated_message", recommendation.get("message", "")),
        "explanation": recommendation.get("explanation", "No explanation available")
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_progress(request):
    score = request.data.get("score")
    if score is None:
        return Response({'error': 'Score is required'}, status=status.HTTP_400_BAD_REQUEST)

    student = request.user.studentprofile
    student.progress_score += int(score)
    student.save()

    return Response({'message': 'Progress updated', 'total_score': student.progress_score})
