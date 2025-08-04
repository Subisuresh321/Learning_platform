from django.urls import path
from . import views, api


urlpatterns = [
    path('', views.home, name='home'),

    # Agent Pages
    path('quiz/', views.quiz_page, name='quiz'),
    path('translate/', views.translate_page, name='translate'),
    path('recommend/', views.recommend_page, name='recommend'),
    path('learning_plan/', api.get_learning_plan, name='learning_plan'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('mypage/', views.mypage_view, name='mypage'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('submit-score/', views.submit_quiz_score, name='submit_score'),

    # APIs
    path('api/quiz/', api.generate_quiz, name='api_quiz'),
    path('api/translate/', api.translate_text, name='api_translate'),
    path('api/recommend/', api.get_learning_plan, name='api_recommend'),
    path('api/update_progress/', api.update_progress, name='update_progress'),
]
