import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from .forms import CustomRegisterForm, LoginForm
from .models import StudentProfile
from .agents import learning_agent, translation_agent, quiz_agent


def home(request):
    if request.method == "POST":
        name = request.POST.get("name")
        lang = request.POST.get("language")
        score = int(request.POST.get("score", 0))
        last_topic = request.POST.get("last_topic")

        # Create User
        user = User.objects.create_user(username=name)

        # Create Student Profile
        student = StudentProfile.objects.create(
            user=user,
            preferred_language=lang,
            score=score,
            last_quiz_topic=last_topic,
            progress={"score": score, "last_topic": last_topic}
        )

        # Run AI agents
        recommendation = learning_agent(student.progress)
        translation = translation_agent("Welcome to your learning journey!", lang)
        quiz = quiz_agent(last_topic)

        context = {
            "student": student,
            "level": recommendation.get("level", ""),
            "focus": recommendation.get("focus", ""),
            "message": translation,
            "quiz": quiz,
        }
        return render(request, "core/home.html", context)

    return render(request, "core/home.html")


@csrf_exempt
def quiz_page(request):
    questions = None
    if request.method == "POST":
        topic = request.POST.get("topic")
        if topic:
            questions = quiz_agent(topic)
    return render(request, 'core/quiz.html', {'questions': questions})


def translate_page(request):
    return render(request, 'core/translate.html')


def recommend_page(request):
    return render(request, "core/recommend.html")


@csrf_exempt
def api_quiz(request):
    if request.method == "POST":
        data = json.loads(request.body)
        topic = data.get("topic", "")
        quiz_data = quiz_agent(topic)

        # If it's wrapped inside "quiz", unwrap it
        if isinstance(quiz_data, dict) and "quiz" in quiz_data:
            return JsonResponse({"questions": quiz_data["quiz"]})
        else:
            return JsonResponse({"questions": quiz_data})  # fallback

    return JsonResponse({"error": "POST request required"}, status=400)


@csrf_exempt
def api_translate(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            text = data.get("text", "")
            lang = data.get("lang", "")
            translated = translation_agent(text, lang)
            return JsonResponse({"translation": translated})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "POST request required"}, status=400)


@csrf_exempt
def api_recommend(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            progress = data.get("progress", {})
            recommendation = learning_agent(progress)
            return JsonResponse({
                "level": recommendation.get("level", "N/A"),
                "focus": recommendation.get("focus", "N/A"),
                "translated_message": recommendation.get("translated_message", ""),
                "quiz": recommendation.get("quiz", [])
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "POST request required"}, status=400)


def register_view(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('mypage')
    else:
        form = CustomRegisterForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('mypage')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def mypage_view(request):
    student, created = StudentProfile.objects.get_or_create(user=request.user)
    return render(request, 'core/mypage.html', {'student': student})


@csrf_exempt
def submit_quiz_score(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('name')
            score = int(data.get('score', 0))
            topic = data.get('topic')

            user = User.objects.get(username=username)
            student = StudentProfile.objects.get(user=user)
            student.score += score
            student.last_quiz_topic = topic
            student.save()

            return JsonResponse({'status': 'success', 'message': 'Score updated'})
        except (User.DoesNotExist, StudentProfile.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Student not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'error': 'POST request required'}, status=400)


def leaderboard_view(request):
    students = StudentProfile.objects.order_by('-score')[:10]
    return render(request, 'core/leaderboard.html', {'students': students})
