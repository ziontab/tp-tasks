from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from app.forms import *
from app.models import *
from django.contrib.auth import logout


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
                                          'user': request.user,
                                          'best_members': best_members})


def hot_questions(request):
    curr_questions = paginate(Question.objects.hot(), request, 5)
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'index.html', {'questions': curr_questions,
                                          'paginated_elements': curr_questions,
                                          'popular_tags': popular_tags,
                                          'user': request.user,
                                          'best_members': best_members})


def questions_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, tag=tag_name)
    curr_questions = paginate(Question.objects.by_tag(tag_name), request, 5)
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'questions_by_tag.html', {'questions': curr_questions,
                                                     'popular_tags': popular_tags,
                                                     'best_members': best_members,
                                                     'tag': tag,
                                                     'paginated_elements': curr_questions,
                                                     'user': request.user,
                                                     })


def question(request, question_id):
    curr_question = get_object_or_404(Question, pk=question_id)
    curr_answers = paginate(Answer.objects.by_question(pk=question_id), request, 5)
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'question.html', {'question': curr_question,
                                             'answers': curr_answers,
                                             'popular_tags': popular_tags,
                                             'best_members': best_members,
                                             'paginated_elements': curr_answers,
                                             'user': request.user,
                                             })


def signup(request):
    print('________________________________________')
    print(request.GET)
    print(request.POST)
    popular_tags = Tag.objects.popular_tags()
    if request.method == 'GET':
        form = SignupForm()
    else:
        form = SignupForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return redirect(request.POST.get('next', '/'))
    return render(request, 'signup.html', {
        'form': form,
        'popular_tags': popular_tags,
        'best_members': best_members,
        'user': request.user,
    })


def login(request):
    print(request.GET)
    print(request.POST)
    popular_tags = Tag.objects.popular_tags()
    print('82')
    if request.method == 'GET':
        print('84')
        form = LoginForm()
        print('86')
    elif request.method == 'POST':
        print('88')
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = auth.authenticate(**form.cleaned_data)
            print('92')
            if not user:
                print('94')
                form.add_error(None, 'User not found')
            else:
                print('97')
                auth.login(request, user)
                return redirect(request.POST.get('next', '/'))
    print('100')
    return render(request, 'login.html', {'form': form,
                                          'best_members': best_members,
                                          'user': request.user,
                                          'popular_tags': popular_tags})


@login_required
def logout(request):
    auth.logout(request)
    return redirect(reverse('index'))


def settings(request):
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'settings.html', {'popular_tags': popular_tags,
                                             'user': request.user,
                                             'best_members': best_members
                                             })


def ask(request):
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'new_question.html', {'popular_tags': popular_tags,
                                                 'user': request.user,
                                                 'best_members': best_members
                                                 })
