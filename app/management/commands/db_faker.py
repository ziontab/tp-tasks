from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from app.models import Profile, Question, Answer, Tag, LikeQuestion, LikeAnswer
from random import choice, sample, randint
from faker import Faker

faker = Faker()


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('--auto', nargs='+', type=int)
        parser.add_argument('--users', nargs='+', type=int)
        parser.add_argument('--questions', nargs='+', type=int)
        parser.add_argument('--answers', nargs='+', type=int)
        parser.add_argument('--tags', nargs='+', type=int)
        parser.add_argument('--likes', nargs='+', type=int)

        parser.add_argument('--db_size', nargs='+', type=str)

    def handle(self, *args, **options):
        if options['auto']:
            self.fill_db(options['auto'][0])

        if options['users']:
            self.fill_profiles(options['users'][0])

        if options['tags']:
            self.fill_tags(options['tags'][0])

        if options['questions']:
            self.fill_questions(options['questions'][0])

        if options['answers']:
            self.fill_answers(options['answers'][0])

        if options['likes']:
            self.fill_likes_dislikes_questions(options['likes'][0])
            self.fill_likes_dislikes_answers(options['likes'][0])

        self.stdout.write(self.style.SUCCESS('Data creation was successful'))

    @staticmethod
    def fill_profiles(profile_count, avatar_count=5):
        profile_counter = 0
        while profile_counter < profile_count:
            try:
                Profile.objects.create(
                    user_id=User.objects.create_user(
                        username=faker.user_name(),
                        email=faker.email(),
                        password="1"
                    ),
                    avatar="img/avatar_" + str(profile_counter % avatar_count) + ".jpg",
                )
                profile_counter += 1
            except Exception:
                pass

    @staticmethod
    def fill_tags(tag_count):
        tags_counter = 0
        while tags_counter < tag_count:
            try:
                tag = faker.word() + '_' + faker.word()
                Tag.objects.create(tag=tag)
                tags_counter += 1
            except Exception:
                pass

    @staticmethod
    def fill_questions(question_count, question_tags_max=25):
        profile_ids = list(
            Profile.objects.values_list(
                'id', flat=True
            )
        )
        tag_ids = list(Tag.objects.values_list('tag', flat=True))

        for i in range(question_count):
            tags_list = sample(tag_ids, randint(1, question_tags_max))
            Question.objects.create(
                profile_id=Profile.objects.get(pk=choice(profile_ids)),
                title=faker.sentence()[:-1] + '?',
                text=faker.text()
            ).tags.set(Tag.objects.create_question(tags_list))

    @staticmethod
    def fill_answers(answer_count):
        profile_ids = list(
            Profile.objects.values_list(
                'id', flat=True
            )
        )
        question_ids = list(
            Question.objects.values_list(
                'id', flat=True
            )
        )
        for i in range(answer_count):
            Answer.objects.create(
                profile_id=Profile.objects.get(pk=choice(profile_ids)),
                question_id=Question.objects.get(pk=choice(question_ids)),
                text=faker.text(),
                is_correct=faker.random_int(min=0, max=1),
            )

    @staticmethod
    def fill_likes_dislikes_questions(like_and_dislike_count):
        profile_ids = list(
            Profile.objects.values_list(
                'id', flat=True
            )
        )
        question_ids = list(
            Question.objects.values_list(
                'id', flat=True
            )
        )
        i = 0
        while i < like_and_dislike_count:
            try:
                LikeQuestion.objects.create(
                    profile_id=Profile.objects.get(pk=choice(profile_ids)),
                    question_id=Question.objects.get(pk=choice(question_ids)),
                    is_like=faker.random.choice([True, False])
                )
                i += 1
            except Exception:
                pass

    @staticmethod
    def fill_likes_dislikes_answers(like_and_dislike_count):
        profile_ids = list(
            Profile.objects.values_list(
                'id', flat=True
            )
        )
        answer_ids = list(
            Answer.objects.values_list(
                'id', flat=True
            )
        )
        i = 0
        while i < like_and_dislike_count:
            try:
                LikeAnswer.objects.create(
                    profile_id=Profile.objects.get(pk=choice(profile_ids)),
                    answer_id=Answer.objects.get(pk=choice(answer_ids)),
                    is_like=faker.random.choice([True, False])
                )
                i += 1
            except Exception:
                pass

    def fill_db(self, cnt):
        self.fill_profiles(cnt)
        self.fill_tags(cnt // 2)
        self.fill_questions(3 * cnt)
        self.fill_answers(10 * cnt)
        self.fill_likes_dislikes_questions(5 * cnt)
        self.fill_likes_dislikes_answers(20 * cnt)
