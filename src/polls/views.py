from django.db.models import F
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.urls import reverse_lazy
from .models import Choice, Question
import logging
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

security_logger = logging.getLogger("security")

# FLAW 5 (A09:2021 Security Logging and Monitoring Failures): login attempts
# (successful and failed) are not logged, so there's no record of who
# logged in, when, or from where, nor any trace of attacks in progress.
#
# FIX 2/2: uncomment these two receivers to log login activity with IP address.
@receiver(user_logged_in)
def log_successful_login(sender, request, user, **kwargs):
    security_logger.info(
        "Successful login: user=%s ip=%s", user.username, request.META.get("REMOTE_ADDR"),
    )

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    security_logger.warning(
        "Failed login: username=%s ip=%s",
        credentials.get("username"), request.META.get("REMOTE_ADDR"),
    )

@login_required
def delete_poll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # FLAW 1 (A01:2021 Broken Access Control): site does not check if the user owns the poll:
    # any logged-in user can delete any poll via /<id>/delete/
    # FIX: uncomment the lines below
    #if question.owner != request.user:
        #raise PermissionDenied  
    if request.method == "POST":
        question.delete()
        return HttpResponseRedirect(reverse("polls:index"))
    return render(request, "polls/delete_poll.html", {"question": question})

@login_required
def create_poll(request):
    error_message = None
    if request.method == "POST":
        text = request.POST.get("question_text", "").strip()
        choices = [
            line.strip()[:200]
            for line in request.POST.get("choices", "").splitlines()
            if line.strip()
        ]
        if not text:
            error_message = "Please enter a question."
        elif len(choices) < 2:
            error_message = "Please enter at least two choices."
        else:
            question = Question.objects.create(
                question_text=text,
                pub_date=timezone.now(),
                owner=request.user,
            )
            for choice_text in choices:
                Choice.objects.create(question=question, choice_text=choice_text)
            return HttpResponseRedirect(reverse("polls:index"))
    return render(request, "polls/create_poll.html", {"error_message": error_message})

def account_locked(request, credentials=None, *args, **kwargs):
    return render(request, "polls/account_locked.html")

def register(request):
    if request.method == "GET":
        return render(request, "polls/register.html")

    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    password_confirmation = request.POST.get("password_confirmation", "")

    if not username or not password:
        return render(request, "polls/register.html", {
            "error_message": "Username and password are required",
            "previous_username_input": username,
        })

    if User.objects.filter(username=username).exists():
        return render(request, "polls/register.html", {
            "error_message": "Username already exists",
            "previous_username_input": username,
        })

    if password != password_confirmation:
        return render(request, "polls/register.html", {
            "error_message": "Passwords do not match",
            "previous_username_input": username,
        })

    try:
        validate_password(password)
        User.objects.create_user(username=username, password=password)
    except ValidationError as e:
        return render(request, "polls/register.html", {
            "validation_error_messages": e.messages,
            "previous_username_input": username,
        })

    return render(request, "polls/register.html", {
        "success_message": f"Account '{username}' created successfully!"
    })

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        self.search_query = self.request.GET.get("q", "").strip()

        # Flaw 3 (A03:2021 Injection): user input from search is pasted
        # directly into a raw SQL string instead of being sent as a
        # parameter.
        sql = (
            "SELECT * FROM polls_question "
            f"WHERE question_text LIKE '%{self.search_query}%' "
            "ORDER BY pub_date DESC"
        )
        questions = list(Question.objects.raw(sql))
        return questions if self.search_query else questions[:5]

        # Fix: use the ORM, which sends user input to the database as a
        # parameter instead of concatenating it into the SQL string.
        # questions = Question.objects.order_by("-pub_date")
        # if self.search_query:
        #     return questions.filter(question_text__icontains=self.search_query)
        # return questions[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.search_query
        return context

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))