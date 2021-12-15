from django.db import models
from django.contrib.auth.models import User

from random import sample

# TODO: поменять на английский
#TODO: удалить рейтинг тега
class ProfileManager(models.Manager):
    def sample_profile(self, count):
        profile_ids = list(
            Profile.objects.values_list(
                'id', flat=True
            )
        )
        return self.filter(id__in=sample(profile_ids, k=count))


class Profile(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, null=True, verbose_name='Профиль')
    avatar = models.ImageField(default='img/no_avatar.jpg', upload_to='static/avatar/%y/%m/%d', verbose_name='Аватар')

    objects = ProfileManager()

    def __str__(self):
        return self.user_id.get_username()

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


# class TagManager(models.Manager):
#     def create_question(self, tags_list):
#         tags = self.filter(tag__in=tags_list)
#         for tag in tags:
#             tag.rating += 1
#             tag.save()
#         return tags
#
#     def popular_tags(self):
#         return self.all().order_by('-rating')[:9]


class Tag(models.Model):
    tag = models.CharField(unique=True, max_length=32, verbose_name='Тег')
    # TODO: delete
    # rating = models.IntegerField(default=0, verbose_name='Рейтинг')

    # objects = TagManager()

    def __str__(self):
        return self.tag

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class QuestionManager(models.Manager):
    def all(self):
        return self.order_by('-date_create')

    def by_tag(self, tag):
        return self.filter(tags__tag=tag).order_by('-rating', '-date_create')

    def hot(self):
        return self.order_by('-rating', '-date_create')


class Question(models.Model):
    # TODO: тут были кавычки 
    profile_id = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='Автор')
    title = models.CharField(max_length=1024, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст вопроса')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    number_of_answers = models.IntegerField(default=0, verbose_name='Количество ответов')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    likes_count = models.IntegerField(default=0, verbose_name='Лайки')
    dislikes_count = models.IntegerField(default=0, verbose_name='Дизлайки')

    objects = QuestionManager()

    def __str__(self):
        return self.title

    def get_tags(self):
        return self.tags

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class AnswerManager(models.Manager):
    def by_question(self, pk):
        return self.filter(question_id=pk).order_by('-rating', 'date_create')


class Answer(models.Model):
    profile_id = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='Автор')
    question_id = models.ForeignKey('Question', on_delete=models.CASCADE, verbose_name='Вопрос')
    text = models.TextField(verbose_name='Текст ответа')
    is_correct = models.BooleanField(default=False, verbose_name='Корректность ответа')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    likes_count = models.IntegerField(default=0, verbose_name='Лайки')
    dislikes_count = models.IntegerField(default=0, verbose_name='Дизлайки')

    objects = AnswerManager()

    #TODO: ??? поч self.question_id.title
    def __str__(self):
        return self.question_id.title

    def save(self, *args, **kwargs):
        if not self.pk:
            self.question_id.number_of_answers += 1
            self.question_id.save()
        super(Answer, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.question_id.number_of_answers -= 1
        self.question_id.save()
        super(Answer, self).delete(*args, **kwargs)

    # TODO: rename: bad naming
    def change_mind_correct(self):
        self.is_correct = not self.is_correct
        self.save()

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'


class LikeQuestion(models.Model):
    question_id = models.ForeignKey('Question', on_delete=models.CASCADE, verbose_name='Вопрос')
    profile_id = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='Профиль')
    is_like = models.BooleanField(default=True, verbose_name='Лайк или дизлайк')

    def __str__(self):
        action = 'дизлайкнул'
        if self.is_like:
            action = 'лайкнул'
        return self.profile_id.user_id.get_username() + ' ' + action + ' "' + self.question_id.title + '"'

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.is_like:
                self.question_id.likes_count += 1
                self.question_id.rating += 1
            else:
                self.question_id.dislikes_count += 1
                self.question_id.rating -= 1
            self.question_id.save()
        super(LikeQuestion, self).save(*args, **kwargs)
        return self.question_id.rating

    def delete(self, *args, **kwargs):
        if self.is_like:
            self.question_id.likes_count -= 1
            self.question_id.rating -= 1
        else:
            self.question_id.dislike_count -= 1
            self.question_id.rating += 1
        self.question_id.save()
        super(LikeQuestion, self).delete(*args, **kwargs)
        return self.question_id.rating

    def change_mind(self):
        if self.is_like:
            self.question_id.like_count -= 1
            self.question_id.dislike_count += 1
            self.question_id.rating -= 2
        else:
            self.question_id.like_count += 1
            self.question_id.dislike_count -= 1
            self.question_id.rating += 2
        self.is_like = not self.is_like
        self.save()
        self.question_id.save()
        return self.question_id.rating

    class Meta:
        unique_together = ('question_id', 'profile_id')
        verbose_name = 'Лайк вопроса'
        verbose_name_plural = 'Лайки вопросов'


class LikeAnswer(models.Model):
    answer_id = models.ForeignKey('Answer', on_delete=models.CASCADE, verbose_name='Ответ')
    profile_id = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='Профиль')
    is_like = models.BooleanField(default=True, verbose_name='Лайк или дизлайк')

    def __str__(self):
        action = 'дизлайкнул'
        if self.is_like:
            action = 'лайкнул'
        return self.profile_id.user_id.get_username() + ' ' + action + ' "' + self.answer_id.text + '"'

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.is_like:
                self.answer_id.likes_count += 1
                self.answer_id.rating += 1
            else:
                self.answer_id.dislikes_count += 1
                self.answer_id.rating -= 1
            self.answer_id.save()
        super(LikeAnswer, self).save(*args, **kwargs)
        return self.answer_id.rating

    def delete(self, *args, **kwargs):
        if self.is_like:
            self.answer_id.likes_count -= 1
            self.answer_id.rating -= 1
        else:
            self.answer_id.dislikes_count -= 1
            self.answer_id.rating += 1
        self.answer_id.save()
        super(LikeAnswer, self).delete(*args, **kwargs)
        return self.answer_id.rating

    def change_mind(self):
        if self.is_like:
            self.answer_id.likes_count -= 1
            self.answer_id.dislikes_count += 1
            self.answer_id.rating -= 2
        else:
            self.answer_id.likes_count += 1
            self.answer_id.dislikes_count -= 1
            self.answer_id.rating += 2
        self.is_like = not self.is_like
        self.save()
        self.answer_id.save()
        return self.answer_id.rating

    class Meta:
        unique_together = ('answer_id', 'profile_id')
        verbose_name = 'Лайк ответа'
        verbose_name_plural = 'Лайки ответов'
