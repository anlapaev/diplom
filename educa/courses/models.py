from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.template.loader import render_to_string

from .fields import OrderField


class Subject(models.Model):
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Адрес', max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(
        User, related_name='courses_created', on_delete=models.CASCADE
    )
    subject = models.ForeignKey(
        Subject, related_name='courses', on_delete=models.CASCADE
    )
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Адрес', max_length=200, unique=True)
    overview = models.TextField('Описание')
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(
        User, related_name='courses_joined', blank=True
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(
        Course, related_name='modules', on_delete=models.CASCADE,
        verbose_name='Курс'
    )
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    order = OrderField(verbose_name='Порядок', blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.order}. {self.title}'


class Lesson(models.Model):
    module = models.ForeignKey(
        Module,
        related_name='lessons',
        on_delete=models.CASCADE,
        verbose_name='Модуль',
    )
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    order = OrderField(verbose_name='Порядок', blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.order}. {self.title}'


class Content(models.Model):
    module = models.ForeignKey(
        Module, related_name='contents', on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={
            'model__in': ('text', 'video', 'image', 'file')
        },
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']


class Step(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        related_name='steps',
        on_delete=models.CASCADE,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={
            'model__in': ('text', 'video', 'image', 'file')
        },
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['lesson'])

    class Meta:
        ordering = ['order']

    def clean(self):
        if self.pk is None and self.lesson.steps.count() >= 16:
            raise ValidationError('Урок не может содержать более 16 шагов.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class ItemBase(models.Model):
    owner = models.ForeignKey(
        User, related_name='%(class)s_related', on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    title = models.CharField('Название', max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def render(self):
        return render_to_string(
            f'courses/content/{self._meta.model_name}.html',
            {'item': self},
        )


class Text(ItemBase):
    content = models.TextField('Содержание')


class File(ItemBase):
    file = models.FileField('Файл', upload_to='files')


class Image(ItemBase):
    file = models.FileField('Изображение', upload_to='images')


class Video(ItemBase):
    url = models.URLField('URL видео')
class Test(models.Model):
    module = models.ForeignKey(
        Module, related_name='tests', on_delete=models.CASCADE,
        verbose_name='Модуль'
    )
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    order = OrderField(verbose_name='Порядок', blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.order}. {self.title}'


class Question(models.Model):
    test = models.ForeignKey(
        Test, related_name='questions', on_delete=models.CASCADE,
        verbose_name='Тест'
    )
    text = models.CharField('Вопрос', max_length=300)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(
        Question, related_name='answers', on_delete=models.CASCADE,
        verbose_name='Вопрос'
    )
    text = models.CharField('Ответ', max_length=300)
    is_correct = models.BooleanField('Правильный', default=False)

    def __str__(self):
        return self.text


class TestSubmission(models.Model):
    user = models.ForeignKey(
        User, related_name='test_submissions', on_delete=models.CASCADE
    )
    test = models.ForeignKey(
        Test, related_name='submissions', on_delete=models.CASCADE
    )
    data = models.JSONField('Ответы')
    score = models.PositiveIntegerField('Результат')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']


class PracticalAssignment(models.Model):
    module = models.ForeignKey(
        Module,
        related_name='assignments',
        on_delete=models.CASCADE,
        verbose_name='Модуль',
    )
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    file = models.FileField(
        'Файл', upload_to='assignments', blank=True, null=True
    )
    order = OrderField(verbose_name='Порядок', blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.order}. {self.title}'


class PracticalSubmission(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REDO = 'redo'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'В проверке'),
        (STATUS_ACCEPTED, 'Принято'),
        (STATUS_REDO, 'Переделать'),
    ]

    assignment = models.ForeignKey(
        PracticalAssignment,
        related_name='submissions',
        on_delete=models.CASCADE,
    )
    student = models.ForeignKey(
        User,
        related_name='practical_submissions',
        on_delete=models.CASCADE,
    )
    file = models.FileField('Файл', upload_to='submissions')
    status = models.CharField(
        'Статус',
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f'{self.assignment} - {self.student}'

