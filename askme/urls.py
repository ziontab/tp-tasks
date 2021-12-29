from django.urls import path
from app import views
from django.contrib import admin

urlpatterns = [
    path('', views.new_questions, name='index'),
    path('hot/', views.hot_questions, name='hot_questions'),
    path('ask/', views.ask, name='ask'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('tag/<tag_name>', views.questions_by_tag, name='questions_by_tag'),
    path('settings/', views.settings, name='settings'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('admin/', admin.site.urls),
]
