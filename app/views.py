from django.core.paginator import Paginator
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.urls import resolve
from django.views.decorators.http import require_GET

from app.forms import *
from app.models import *

best_members = Profile.objects.sample_profile(count=20)
default_obj_page_limit = 5
max_obj_page_limit = 100


def paginate(objects_list, request):
    try:
        limit = int(request.GET.get('limit', default_obj_page_limit))
    except ValueError:
        limit = default_obj_page_limit
    if limit > max_obj_page_limit:
        limit = max_obj_page_limit
    if limit < 1:
        limit = default_obj_page_limit

    try:
        page_num = int(request.GET.get('page', 1))
    except ValueError:
        raise Http404

    if page_num < 1:
        page_num = 1
    paginator = Paginator(objects_list, limit)
    return paginator.get_page(page_num)


@require_GET
def new_questions(request):
    curr_questions = paginate(Question.objects.all(), request)
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'index.html', {'questions': curr_questions,
                                          'paginated_elements': curr_questions,
                                          'popular_tags': popular_tags,
                                          'user': request.user,
                                          'best_members': best_members,
                                          'redirect_after_logout': reverse('index'),
                                          })


@require_GET
def hot_questions(request):
    curr_questions = paginate(Question.objects.hot(), request)
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'hot_questions.html', {'questions': curr_questions,
                                                  'paginated_elements': curr_questions,
                                                  'popular_tags': popular_tags,
                                                  'best_members': best_members,
                                                  'redirect_after_logout': reverse('hot_questions'),
                                                  })


@require_GET
def questions_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, tag=tag_name)
    curr_questions = paginate(Question.objects.by_tag(tag_name), request)
    popular_tags = Tag.objects.popular_tags()
    return render(request, 'questions_by_tag.html', {'questions': curr_questions,
                                                     'popular_tags': popular_tags,
                                                     'best_members': best_members,
                                                     'tag': tag,
                                                     'paginated_elements': curr_questions,
                                                     'redirect_after_logout': tag.get_url(),
                                                     })


def question(request, question_id):
    print(request.GET)
    print(request.POST)
    curr_question = get_object_or_404(Question, pk=question_id)

    if request.method == 'POST' and request.user.is_authenticated:
        answer_form = AnswerForm(data=request.POST)
        curr_answer = Answer.objects.create(
            text=answer_form.data['text'],
            profile_id=Profile.objects.get(user_id=request.user),
            question_id=curr_question
        )
        curr_question.save()
        curr_answer_index = Answer.objects.all().filter(question_id=question_id).filter(rating__gte=0,
                                                                                        date_create__lt=curr_answer.date_create).count()
        try:
            limit = int(request.GET.get('limit', default_obj_page_limit))
        except ValueError:
            limit = default_obj_page_limit
        if limit > max_obj_page_limit:
            limit = max_obj_page_limit
        if limit < 1:
            limit = default_obj_page_limit

        return redirect(curr_question.get_url() + '?page=' + str(
            curr_answer_index // limit + 1) + '#is-right-checkbox-' + str(curr_answer.pk))
    else:
        curr_answers = paginate(Answer.objects.by_question(pk=question_id), request)
        popular_tags = Tag.objects.popular_tags()
        return render(request, 'question.html', {'question': curr_question,
                                                 'answers': curr_answers,
                                                 'popular_tags': popular_tags,
                                                 'best_members': best_members,
                                                 'paginated_elements': curr_answers,
                                                 'ask_form': AskForm(),
                                                 'redirect_after_logout': curr_question.get_url(),
                                                 })


def signup(request):
    print(request.GET)
    print(request.POST)
    popular_tags = Tag.objects.popular_tags()

    if request.method == 'POST':
        form = SignupForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return redirect(request.POST.get('next', '/'))
    else:
        form = SignupForm()

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

    redirect_page = request.GET.get('next', 'index')
    try:
        resolve(redirect_page)
    except Http404:
        redirect_page = 'index'

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = auth.authenticate(**form.cleaned_data)
            if not user:
                form.add_error(None, 'User not found')
            else:
                auth.login(request, user)
                return redirect(redirect_page)
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form,
                                          'best_members': best_members,
                                          'user': request.user,
                                          'redirect_after_logout': redirect_page,
                                          'popular_tags': popular_tags})


@login_required(login_url='login')
@require_GET
def logout(request):
    print(request.GET)
    print(request.POST)
    auth.logout(request)

    redirect_page = request.GET.get('next', 'index')
    try:
        resolve(redirect_page)
    except Http404:
        redirect_page = 'index'

    if redirect_page:
        return redirect(redirect_page)
    return redirect(reverse('index'))


@login_required(login_url='login')
def settings(request):
    print(request.GET)
    print(request.POST)
    popular_tags = Tag.objects.popular_tags()
    is_change_saved = request.GET.get('saved', '')
    if request.method == 'POST':
        form = SettingsForm(user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return HttpResponseRedirect(reverse('settings') + '?saved=True')
    else:
        form = SettingsForm(
            initial={'username': request.user.username, 'email': request.user.email, 'password': request.user.password})

    return render(request, 'settings.html', {
        'form': form,
        'popular_tags': popular_tags,
        'best_members': best_members,
        'user': request.user,
        'is_change_saved': is_change_saved,
    })


@login_required(login_url='login')
def ask(request):
    print(request.GET)
    print(request.POST)
    popular_tags = Tag.objects.popular_tags()

    if request.method == 'POST':
        form = AskForm(request.user.profile, data=request.POST)
        if form.is_valid():
            published_question = form.save()
            return HttpResponseRedirect(published_question.get_url())
    else:
        form = AskForm()
        
    return render(request, 'new_question.html', {
        'form': form,
        'popular_tags': popular_tags,
        'best_members': best_members,
    })
