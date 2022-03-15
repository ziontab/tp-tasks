from django.db import models
from django.contrib.auth.models import User
from random import sample

from django.urls import reverse


class ProfileManager(models.Manager):
    def sample_profile(self, count):
        profile_ids = list(
            Profile.objects.values_list('id', flat=True)
        )
        return self.filter(id__in=sample(profile_ids, k=count))


class Profile(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, null=True, verbose_name='Profile')
    avatar = models.ImageField(default='img/no_avatar.jpg', upload_to='avatar/%y/%m/%d', verbose_name='Avatar')

    objects = ProfileManager()

    def __str__(self):
        return self.user_id.get_username()

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'


class TagManager(models.Manager):
    def create_question(self, tags_list):
        tags = self.filter(tag__in=tags_list)
        for tag in tags:
            tag.rating += 1
            tag.save()
        return tags

    def popular_tags(self):
        return self.all().order_by('-rating')[:9]


class Tag(models.Model):
    tag = models.CharField(unique=True, max_length=32, verbose_name='Tag')
    rating = models.IntegerField(default=0, verbose_name='Rating')

    objects = TagManager()

    def get_url(self):
        return reverse('questions_by_tag', kwargs={'tag_name': self.tag})

    def __str__(self):
        return self.tag

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class QuestionManager(models.Manager):
    def all(self):
        return self.order_by('-date_create')

    def by_tag(self, tag):
        return self.filter(tags__tag=tag).order_by('-rating', '-date_create')

    def hot(self):
        return self.order_by('-rating', '-date_create')


class Question(models.Model):
    profile_id = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='Author')
    title = models.CharField(max_length=1024, verbose_name='Title')
    text = models.TextField(verbose_name='Text')
    tags = models.ManyToManyField(Tag, verbose_name='Tags')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Creation time')
    number_of_answers = models.IntegerField(default=0, verbose_name='Answer count')
    rating = models.IntegerField(default=0, verbose_name='Rating')
    likes_count = models.IntegerField(default=0, verbose_name='Likes')
    dislikes_count = models.IntegerField(default=0, verbose_name='Dislikes')

    objects = QuestionManager()

    def __str__(self):
        return self.title

    def get_url(self):
        return reverse('question', kwargs={'question_id': self.id})

    def get_tags(self):
        return self.tags

    # def get_user_mind(self): получить мнение пользователя по вопросу: лайк/дизлайк/ничего

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'


class AnswerManager(models.Manager):
    def by_question(self, pk):
        return self.filter(question_id=pk).order_by('-rating', 'date_create')


class Answer(models.Model):
    profile_id = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='Author')
    question_id = models.ForeignKey('Question', on_delete=models.CASCADE, verbose_name='Question')
    text = models.TextField(verbose_name='Text')
    is_correct = models.BooleanField(default=False, verbose_name='Is correct')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Creation time')
    rating = models.IntegerField(default=0, verbose_name='Rating')
    likes_count = models.IntegerField(default=0, verbose_name='Likes')
    dislikes_count = models.IntegerField(default=0, verbose_name='Dislikes')

    objects = AnswerManager()

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

    def change_mind_correct(self):
        self.is_correct = not self.is_correct
        self.save()

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'


class LikeQuestion(models.Model):
    question_id = models.ForeignKey('Question', on_delete=models.CASCADE, verbose_name='Question')
    profile_id = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='Profile')
    is_like = models.BooleanField(default=True, verbose_name='Like or dislike')

    def __str__(self):
        action = 'Disliked'
        if self.is_like:
            action = 'Liked'
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
            self.question_id.dislikes_count -= 1
            self.question_id.rating += 1
        self.question_id.save()
        super(LikeQuestion, self).delete(*args, **kwargs)
        return self.question_id.rating

    def change_mind(self):
        if self.is_like:
            self.question_id.likes_count -= 1
            self.question_id.dislikes_count += 1
            self.question_id.rating -= 2
        else:
            self.question_id.likes_count += 1
            self.question_id.dislikes_count -= 1
            self.question_id.rating += 2
        self.is_like = not self.is_like
        self.save()
        self.question_id.save()
        return self.question_id.rating

    class Meta:
        unique_together = ('question_id', 'profile_id')
        verbose_name = 'Question like'
        verbose_name_plural = 'Questions likes'


class LikeAnswer(models.Model):
    answer_id = models.ForeignKey('Answer', on_delete=models.CASCADE, verbose_name='Answer')
    profile_id = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='Profile')
    is_like = models.BooleanField(default=False, verbose_name='Like or dislike')

    def __str__(self):
        action = 'Disliked'
        if self.is_like:
            action = 'Liked'
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
        verbose_name = 'Answer like'
        verbose_name_plural = 'Answers likes'
