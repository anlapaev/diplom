from django.forms.models import inlineformset_factory, BaseInlineFormSet

from .models import Course, Module


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
    extra=10,
    can_delete=True,
)
