from django.contrib.auth.views import LogoutView
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

class LogoutViewAllowGet(LogoutView):
    """Allow logout via GET requests for convenience."""

    def get(self, request, *args, **kwargs):
        """Redirect GET requests to POST to avoid CSRF issues with stale pages."""
        return self.post(request, *args, **kwargs)


class UserRegistrationView(CreateView):
    """Register a new user and log them in."""

    template_name = "registration/register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("student_course_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(
            username=cd["username"], password=cd["password1"]
        )
        login(self.request, user)
        return response
