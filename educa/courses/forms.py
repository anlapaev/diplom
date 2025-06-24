from django.forms.models import inlineformset_factory, BaseInlineFormSet

from .models import Course, Module, Lesson


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
