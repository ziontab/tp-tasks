from django.urls import path
from app import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from askme.settings import DEBUG

urlpatterns = [
                  path('', views.new_questions, name='index'),
                  path('hot/', views.hot_questions, name='hot_questions'),
                  path('ask/', views.ask, name='ask'),
                  path('question/<int:question_id>/', views.question, name='question'),
                  path('tag/<tag_name>', views.questions_by_tag, name='questions_by_tag'),
                  path('settings/', views.settings, name='settings'),
                  path('login/', views.login, name='login'),
                  path('signup/', views.signup, name='signup'),
                  path('logout/', views.logout, name='logout'),
                  path('question_vote/', views.question_vote, name="question_vote"),
                  path('answer_vote/', views.answer_vote, name="answer_vote"),
                  path('answer_correct/', views.answer_correct, name='answer_correct'),
                  path('admin/', admin.site.urls),
              ]

if DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
