from django import forms

from courses.models import Course
from courses.models import PracticalSubmission


class CourseEnrollForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        super(CourseEnrollForm, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.all()


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = PracticalSubmission
        fields = ['file']
