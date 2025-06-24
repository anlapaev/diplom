from courses.models import Course, Test, Question, Answer, TestSubmission
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView
from django.views import View

from .forms import CourseEnrollForm


class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('student_course_list')

    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(
            username=cd['username'], password=cd['password1']
        )
        login(self.request, user)
        return result


class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'student_course_detail', args=[self.course.id]
        )


class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])


class StudentCourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        if course.modules.exists():
            if 'module_id' in self.kwargs:
                # get current module
                context['module'] = course.modules.get(
                    id=self.kwargs['module_id']
                )
            else:
                # get first module
                context['module'] = course.modules.first()
        else:
            context['module'] = None
        return context

class StudentTestTakeView(LoginRequiredMixin, View):
    template_name = 'students/test/take.html'
    test = None

    def dispatch(self, request, test_id):
        self.test = get_object_or_404(
            Test, id=test_id, module__course__students__in=[request.user]
        )
        return super().dispatch(request, test_id)

    def get(self, request, test_id):
        return render(request, self.template_name, {'test': self.test})

    def post(self, request, test_id):
        answers = {}
        correct = 0
        for question in self.test.questions.all():
            ans_ids = request.POST.getlist(f'question-{question.id}')
            answers[str(question.id)] = ans_ids
            correct_answers = list(
                question.answers.filter(is_correct=True).values_list('id', flat=True)
            )
            if set(map(int, ans_ids)) == set(correct_answers):
                correct += 1
        TestSubmission.objects.create(
            user=request.user, test=self.test, score=correct, data=answers
        )
        return render(
            request,
            self.template_name,
            {
                'test': self.test,
                'score': correct,
                'completed': True,
            },
        )

