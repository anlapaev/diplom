from django.forms.models import inlineformset_factory, BaseInlineFormSet

from .models import (
    Course,
    Module,
    Lesson,
    Test,
    Question,
    Answer,
    PracticalAssignment,
)


class ModuleBaseFormSet(BaseInlineFormSet):
    """Formset for modules with Russian delete label."""

    def add_fields(self, form, index):
        super().add_fields(form, index)
        if self.can_delete and 'DELETE' in form.fields:
            form.fields['DELETE'].label = 'Удалить'

ModuleFormSet = inlineformset_factory(
    Course,
    Module,
    formset=ModuleBaseFormSet,
    fields=['title', 'description'],
    extra=0,
    can_delete=True,
)


class LessonBaseFormSet(BaseInlineFormSet):
    """Formset for lessons with Russian delete label."""

    def add_fields(self, form, index):
        super().add_fields(form, index)
        if self.can_delete and 'DELETE' in form.fields:
            form.fields['DELETE'].label = 'Удалить'


LessonFormSet = inlineformset_factory(
    Module,
    Lesson,
    formset=LessonBaseFormSet,
    fields=['title', 'description'],
    extra=0,
    can_delete=True,
)

class TestBaseFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        if self.can_delete and 'DELETE' in form.fields:
            form.fields['DELETE'].label = 'Удалить'

TestFormSet = inlineformset_factory(
    Module,
    Test,
    formset=TestBaseFormSet,
    fields=['title', 'description'],
    extra=0,
    can_delete=True,
)

QuestionFormSet = inlineformset_factory(
    Test,
    Question,
    fields=['text'],
    extra=0,
    can_delete=True,
)

AnswerFormSet = inlineformset_factory(
    Question,
    Answer,
    fields=['text', 'is_correct'],
    extra=0,
    can_delete=True,
)


class AssignmentBaseFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        if self.can_delete and 'DELETE' in form.fields:
            form.fields['DELETE'].label = 'Удалить'


AssignmentFormSet = inlineformset_factory(
    Module,
    PracticalAssignment,
    formset=AssignmentBaseFormSet,
    fields=['title', 'description', 'file'],
    extra=0,
    can_delete=True,
)

