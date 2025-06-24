from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.apps import apps
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.core.cache import cache
from django.db.models import Count
from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from students.forms import CourseEnrollForm

from .forms import (
    ModuleFormSet,
    LessonFormSet,
    TestFormSet,
    QuestionFormSet,
    AnswerFormSet,
    AssignmentFormSet,
)
from .models import (
    Content,
    Course,
    Module,
    Lesson,
    Step,
    Subject,
    Test,
    Question,
    Answer,
    PracticalAssignment,
    PracticalSubmission,
)


class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(
    OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin
):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(
            Course, id=pk, owner=request.user
        )
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response(
            {'course': self.course, 'formset': formset}
        )

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response(
            {'course': self.course, 'formset': formset}
        )


class ModuleLessonUpdateView(TemplateResponseMixin, View):
    """View to manage lessons within a module."""

    template_name = 'courses/manage/lesson/formset.html'
    module = None

    def get_formset(self, data=None):
        return LessonFormSet(instance=self.module, data=data)

    def dispatch(self, request, module_id):
        self.module = get_object_or_404(
            Module, id=module_id, course__owner=request.user
        )
        return super().dispatch(request, module_id)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response(
            {'module': self.module, 'formset': formset}
        )

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('module_content_list', self.module.id)
        return self.render_to_response(
            {'module': self.module, 'formset': formset}
        )


class ModuleTestUpdateView(TemplateResponseMixin, View):
    """Manage tests within a module."""

    template_name = 'courses/manage/test/formset.html'
    module = None

    def get_formset(self, data=None):
        return TestFormSet(instance=self.module, data=data)

    def dispatch(self, request, module_id):
        self.module = get_object_or_404(
            Module, id=module_id, course__owner=request.user
        )
        return super().dispatch(request, module_id)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response(
            {'module': self.module, 'formset': formset}
        )


class ModuleAssignmentUpdateView(TemplateResponseMixin, View):
    """Manage practical assignments within a module."""

    template_name = 'courses/manage/assignment/formset.html'
    module = None

    def get_formset(self, data=None, files=None):
        return AssignmentFormSet(
            instance=self.module, data=data, files=files
        )

    def dispatch(self, request, module_id):
        self.module = get_object_or_404(
            Module, id=module_id, course__owner=request.user
        )
        return super().dispatch(request, module_id)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response(
            {'module': self.module, 'formset': formset}
        )

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(
            data=request.POST, files=request.FILES
        )
        if formset.is_valid():
            formset.save()
            return redirect('module_content_list', self.module.id)
        return self.render_to_response(
            {'module': self.module, 'formset': formset}
        )

class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(
                app_label='courses', model_name=model_name
            )
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(
            model, exclude=['owner', 'order', 'created', 'updated']
        )
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(
            Module, id=module_id, course__owner=request.user
        )
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(
                self.model, id=id, owner=request.user
            )
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response(
            {'form': form, 'object': self.obj}
        )


class StepCreateUpdateView(TemplateResponseMixin, View):
    """Create or update content within a lesson step."""

    lesson = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(
            model, exclude=['owner', 'order', 'created', 'updated']
        )
        return Form(*args, **kwargs)

    def dispatch(self, request, lesson_id, model_name, id=None):
        self.lesson = get_object_or_404(
            Lesson, id=lesson_id, module__course__owner=request.user
        )
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super().dispatch(request, lesson_id, model_name, id)

    def get(self, request, lesson_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, lesson_id, model_name, id=None):
        form = self.get_form(
            self.model,
            instance=self.obj,
            data=request.POST,
            files=request.FILES,
        )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form, 'object': self.obj})


class StepCreateUpdateView(TemplateResponseMixin, View):
    """Create or update content within a lesson step."""

    lesson = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(
            model, exclude=['owner', 'order', 'created', 'updated']
        )
        return Form(*args, **kwargs)

    def dispatch(self, request, lesson_id, model_name, id=None):
        self.lesson = get_object_or_404(
            Lesson, id=lesson_id, module__course__owner=request.user
        )
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super().dispatch(request, lesson_id, model_name, id)

    def get(self, request, lesson_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, lesson_id, model_name, id=None):
        form = self.get_form(
            self.model,
            instance=self.obj,
            data=request.POST,
            files=request.FILES,
        )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                Step.objects.create(lesson=self.lesson, item=obj)
            return redirect('lesson_step_list', self.lesson.id)
        return self.render_to_response({'form': form, 'object': self.obj})



class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(
            Content, id=id, module__course__owner=request.user
        )
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class StepDeleteView(View):
    """Delete a step and its associated content."""

    def post(self, request, id):
        step = get_object_or_404(
            Step, id=id, lesson__module__course__owner=request.user
        )
        lesson = step.lesson
        step.item.delete()
        step.delete()
        return redirect('lesson_step_list', lesson.id)


class TestQuestionUpdateView(TemplateResponseMixin, View):
    """Manage questions within a test."""

    template_name = 'courses/manage/question/formset.html'
    test = None

    def get_formset(self, data=None):
        return QuestionFormSet(instance=self.test, data=data)

    def dispatch(self, request, test_id):
        self.test = get_object_or_404(
            Test, id=test_id, module__course__owner=request.user
        )
        return super().dispatch(request, test_id)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'test': self.test, 'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('test_question_update', self.test.id)
        return self.render_to_response({'test': self.test, 'formset': formset})


class QuestionAnswerUpdateView(TemplateResponseMixin, View):
    """Manage answers for a question."""

    template_name = 'courses/manage/answer/formset.html'
    question = None

    def get_formset(self, data=None):
        return AnswerFormSet(instance=self.question, data=data)

    def dispatch(self, request, question_id):
        self.question = get_object_or_404(
            Question, id=question_id, test__module__course__owner=request.user
        )
        return super().dispatch(request, question_id)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response(
            {'question': self.question, 'formset': formset}
        )

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('test_question_update', self.question.test.id)
        return self.render_to_response(
            {'question': self.question, 'formset': formset}
        )


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(
            Module, id=module_id, course__owner=request.user
        )
        return self.render_to_response({'module': module})


class LessonStepListView(TemplateResponseMixin, View):
    """Display steps for a lesson."""

    template_name = 'courses/manage/lesson/step_list.html'

    def get(self, request, lesson_id):
        lesson = get_object_or_404(
            Lesson, id=lesson_id, module__course__owner=request.user
        )
        return self.render_to_response({'lesson': lesson})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(
                id=id, course__owner=request.user
            ).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(
                id=id, module__course__owner=request.user
            ).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class LessonOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Lesson.objects.filter(
                id=id, module__course__owner=request.user
            ).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class StepOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Step.objects.filter(
                id=id, lesson__module__course__owner=request.user
            ).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class PracticalSubmissionUpdateView(OwnerMixin, UpdateView):
    model = PracticalSubmission
    fields = ['status']
    template_name = 'courses/manage/assignment/submission_form.html'
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(assignment__module__course__owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy(
            'module_assignment_update',
            args=[self.object.assignment.module.id],
        )


class AssignmentSubmissionListView(OwnerMixin, TemplateResponseMixin, View):
    template_name = 'courses/manage/assignment/submission_list.html'

    def get(self, request, assignment_id):
        assignment = get_object_or_404(
            PracticalAssignment,
            id=assignment_id,
            module__course__owner=request.user,
        )
        submissions = assignment.submissions.select_related('student')
        return self.render_to_response(
            {'assignment': assignment, 'submissions': submissions}
        )


class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = Subject.objects.annotate(
                total_courses=Count('courses')
            )
            cache.set('all_subjects', subjects)
        all_courses = Course.objects.annotate(
            total_modules=Count('modules')
        )
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            key = f'subject_{subject.id}_courses'
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject)
                cache.set(key, courses)
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses', courses)
        return self.render_to_response(
            {
                'subjects': subjects,
                'subject': subject,
                'courses': courses,
            }
        )


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(
            initial={'course': self.object}
        )
        if self.request.user.is_authenticated:
            context['is_enrolled'] = self.object.students.filter(
                id=self.request.user.id
            ).exists()
        else:
            context['is_enrolled'] = False
        return context
