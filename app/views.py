from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from app.forms import *
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
                                          'user': request.user,
                                          'best_members': best_members,
                                          'redirect_after_logout': reverse('index'),
                                          })


def hot_questions(request):
    curr_questions = paginate(Question.objects.hot(), request, 5)
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'hot_questions.html', {'questions': curr_questions,
                                                  'paginated_elements': curr_questions,
                                                  'popular_tags': popular_tags,
                                                  'best_members': best_members,
                                                  'redirect_after_logout': reverse('hot_questions'),
                                                  })


def questions_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, tag=tag_name)
    curr_questions = paginate(Question.objects.by_tag(tag_name), request, 5)
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'questions_by_tag.html', {'questions': curr_questions,
                                                     'popular_tags': popular_tags,
                                                     'best_members': best_members,
                                                     'tag': tag,
                                                     'paginated_elements': curr_questions,
                                                     'redirect_after_logout': reverse('questions_by_tag',
                                                                                      kwargs={'tag_name': tag}),
                                                     })


def question(request, question_id):
    answer_count_on_page = 5
    print(request.GET)
    print(request.POST)
    curr_question = get_object_or_404(Question, pk=question_id)
    if request.method == 'GET':
        curr_answers = paginate(Answer.objects.by_question(pk=question_id), request, answer_count_on_page)
        popular_tags = Tag.objects.popular_tags()
        return render(request, 'question.html', {'question': curr_question,
                                                 'answers': curr_answers,
                                                 'popular_tags': popular_tags,
                                                 'best_members': best_members,
                                                 'paginated_elements': curr_answers,
                                                 'ask_form': AskForm(),
                                                 'redirect_after_logout': reverse('question',
                                                                                  kwargs={'question_id': question_id}),
                                                 })

    if request.method == 'POST' and request.user.is_authenticated:
        answer_form = AnswerForm(data=request.POST)
        curr_answer = Answer.objects.create(
            text=answer_form.data['text'],
            profile_id=Profile.objects.get(user_id=request.user),
            question_id=curr_question
        )
        curr_question.number_of_answers += 1
        curr_question.save()
        print(curr_answer)
        curr_answer_index = Answer.objects.all().filter(question_id=question_id).filter(rating__gte=0,
                                                                                        date_create__lt=curr_answer.date_create).count()
        return redirect(reverse('question', kwargs={
            'question_id': curr_question.pk}) + '?page=' + str(
            curr_answer_index // answer_count_on_page + 1) + '#is-right-checkbox-' + str(curr_answer.pk))


def signup(request):
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
    if request.method == 'GET':
        form = LoginForm()
    elif request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = auth.authenticate(**form.cleaned_data)
            if not user:
                form.add_error(None, 'User not found')
            else:
                auth.login(request, user)
                return redirect(request.POST.get('next', '/'))
    return render(request, 'login.html', {'form': form,
                                          'best_members': best_members,
                                          'user': request.user,
                                          'popular_tags': popular_tags})


@login_required(login_url='login')
def logout(request):
    print(request)
    print(request.GET)
    auth.logout(request)
    if request.method == 'GET':
        return_page = request.GET.get('next')
        if return_page:
            return redirect(return_page)
    return redirect(reverse('index'))


@login_required(login_url='login')
def settings(request):
    print(request.GET)
    print(request.POST)
    popular_tags = Tag.objects.popular_tags()
    if request.method == 'GET':
        form = SettingsForm(
            initial={'username': request.user.username, 'email': request.user.email, 'password': request.user.password})
    else:
        form = SettingsForm(user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
    return render(request, 'settings.html', {
        'form': form,
        'popular_tags': popular_tags,
        'best_members': best_members,
        'user': request.user,
    })


@login_required(login_url='login')
def ask(request):
    print(request.GET)
    print(request.POST)
    popular_tags = Tag.objects.popular_tags()
    if request.method == 'GET':
        form = AskForm()
    elif request.method == 'POST':
        form = AskForm(request.user.profile, data=request.POST)
        if form.is_valid():
            published_question = form.save()
            return redirect(reverse('question', kwargs={'question_id': published_question.pk}))
    return render(request, 'new_question.html', {
        'form': form,
        'popular_tags': popular_tags,
        'best_members': best_members,
    })
