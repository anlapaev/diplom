from django.contrib import admin

from .models import (
    Course,
    Module,
    Subject,
    Lesson,
    Step,
    Test,
    Question,
    Answer,
)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}


class ModuleInline(admin.StackedInline):
    model = Module


class LessonInline(admin.StackedInline):
    model = Lesson


class StepInline(admin.StackedInline):
    model = Step


class QuestionInline(admin.StackedInline):
    model = Question


class AnswerInline(admin.StackedInline):
    model = Answer


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'created']
    list_filter = ['created', 'subject']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order']
    inlines = [StepInline]


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ['id', 'lesson', 'order', 'content_type']

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'test']
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['text', 'question', 'is_correct']

