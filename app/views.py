from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from app.models import *

best_members = Profile.objects.sample_profile(count=20)


def paginate(objects_list, request, limit):
    paginator = Paginator(objects_list, limit)
    return paginator.get_page(request.GET.get('page'))


def new_questions(request):
    curr_questions = paginate(Question.objects.all(), request, 5)
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'index.html', {'questions': curr_questions,
                                          'paginated_elements': curr_questions,
                                          'popular_tags': popular_tags,
                                          'best_members': best_members})


def hot_questions(request):
    curr_questions = paginate(Question.objects.hot(), request, 5)
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'index.html', {'questions': curr_questions,
                                          'paginated_elements': curr_questions,
                                          'popular_tags': popular_tags,
                                          'best_members': best_members})


def questions_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, tag=tag_name)
    curr_questions = paginate(Question.objects.by_tag(tag_name), request, 5)
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'questions_by_tag.html', {'questions': curr_questions,
                                                     'popular_tags': popular_tags,
                                                     'best_members': best_members,
                                                     'tag': tag,
                                                     'paginated_elements': curr_questions
                                                     })


def question(request, question_id):
    curr_question = get_object_or_404(Question, pk=question_id)
    curr_answers = paginate(Answer.objects.by_question(pk=question_id), request, 5)
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'question.html', {'question': curr_question,
                                             'answers': curr_answers,
                                             'popular_tags': popular_tags,
                                             'best_members': best_members,
                                             'paginated_elements': curr_answers
                                             })


def signup(request):
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'signup.html', {'popular_tags': popular_tags,
                                           'best_members': best_members
                                           })


def login(request):
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'login.html', {'popular_tags': popular_tags,
                                          'best_members': best_members
                                          })


def settings(request):
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'settings.html', {'popular_tags': popular_tags,
                                             'best_members': best_members
                                             })


def ask(request):
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'new_question.html', {'popular_tags': popular_tags,
                                                 'best_members': best_members
                                                 })
