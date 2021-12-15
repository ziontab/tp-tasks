from django.core.paginator import Paginator
from django.shortcuts import render
from app.models import *

def paginate(objects_list, request, limit):
    paginator = Paginator(objects_list, limit)
    return paginator.get_page(request.GET.get('page'))

class User:
    def __init__(self, id, nick, login, email, avatar_src):
        self.id = id
        self.nick = nick
        self.login = login
        self.email = email
        self.avatar_src = avatar_src
        return


popular_tags = [f"tag_{i}" for i in range(20)]
best_members = [f"member_{i}" for i in range(20)]
user = User(1, 'my_nick', 'my_login', 'my_email@mail.com', 'avatar.png')


def signup(request):
    return render(request, 'signup.html', {'is_auth': False,
                                           'popular_tags': popular_tags,
                                           'best_members': best_members
                                           })


def login(request):
    return render(request, 'login.html', {'is_auth': False,
                                          'popular_tags': popular_tags,
                                          'best_members': best_members
                                          })


def settings(request):
    return render(request, 'settings.html', {'is_auth': True,
                                             'user': user,
                                             'popular_tags': popular_tags,
                                             'best_members': best_members
                                             })


def ask(request):
    return render(request, 'new_question.html', {'is_auth': True,
                                                 'user': user,
                                                 'popular_tags': popular_tags,
                                                 'best_members': best_members
                                                 })


questions = [
    {
        "title": f"Title for question? {i}",
        "id": i,
        "author": f'writer_{i}',
        "avatar_source_img": "avatar",
        "answers_count": i,
        "text": f'Text for question {i} Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
        "tags_count": 4,
        "tags": ["tag1", "tag2", "tag3", "tag4"],
        "references": ["#", "#", "#", "#"],
        "like_count": i,
        "dislike_count": i,
    } for i in range(100)
]


def questions_by_tag(request, tag_name):
    paginator = Paginator(questions, 5)
    page = request.GET.get('page')
    curr_questions = paginator.get_page(page)
    return render(request, 'questions_by_tag.html', {'is_auth': True,
                                                     'user': user,
                                                     'questions': curr_questions,
                                                     'popular_tags': popular_tags,
                                                     'best_members': best_members,
                                                     'tag_name': tag_name,
                                                     'paginated_elements': curr_questions
                                                     })


def hot_questions(request):
    paginator = Paginator(questions, 5)
    page = request.GET.get('page')
    curr_questions = paginator.get_page(page)
    return render(request, 'index.html', {'is_auth': True,
                                          'user': user,
                                          'questions': curr_questions,
                                          'popular_tags': popular_tags,
                                          'best_members': best_members,
                                          'paginated_elements': curr_questions
                                          })


answers = [
    {
        "id": i,
        "author": f'writer_{i}',
        "avatar_source_img": "avatar",
        "text": f'Text for question {i} Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod '
                f'tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud '
                f'occaecat cupidatat non president, sunt in culpa qui officia deserunt mollit anim id est laborum.',
        "like_count": i,
        "dislike_count": i,
        "correct": (True and (i % 2 == 0))
    } for i in range(100)
]


def question(request, question_id):
    curr_question = questions[0]
    paginator = Paginator(answers, 7)
    page = request.GET.get('page')
    curr_answers = paginator.get_page(page)
    return render(request, 'question.html', {'is_auth': True,
                                             'user': user,
                                             'question': curr_question,
                                             'answers': curr_answers,
                                             'popular_tags': popular_tags,
                                             'best_members': best_members,
                                             'paginated_elements': curr_answers
                                             })
