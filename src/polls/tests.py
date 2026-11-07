import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Choice, Question

class QuestionDetailViewTests(TestCase):
    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and a publication date
    the given number of days before now.
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class PollCreationTests(TestCase):
    def test_create_poll_sets_owner_and_choices(self):
        user = get_user_model().objects.create_user(
            username="poll-author",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("polls:create"),
            {
                "question_text": "Favorite color?",
                "choices": "Blue\nGreen",
            },
        )

        self.assertRedirects(response, reverse("polls:index"))
        question = Question.objects.get(question_text="Favorite color?")
        self.assertEqual(question.owner, user)
        self.assertQuerySetEqual(
            question.choice_set.order_by("choice_text"),
            ["Blue", "Green"],
            transform=lambda choice: choice.choice_text,
        )


class LoginPageTests(TestCase):
    def test_login_page_uses_polls_template(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "polls/login.html")

    def test_successful_login_redirects_to_polls_index(self):
        password = "Strong-test-pass-934!"
        get_user_model().objects.create_user(
            username="login-user",
            password=password,
        )

        response = self.client.post(
            reverse("login"),
            {"username": "login-user", "password": password},
        )

        self.assertRedirects(response, reverse("polls:index"))


class PollDeletionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="poll-owner",
            password="test-password",
        )
        self.question = Question.objects.create(
            question_text="Favorite color?",
            pub_date=timezone.now(),
            owner=self.user,
        )

    def test_owner_can_view_delete_confirmation(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("polls:delete", args=(self.question.pk,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.question.question_text)

    def test_owner_can_delete_poll(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("polls:delete", args=(self.question.pk,))
        )

        self.assertRedirects(response, reverse("polls:index"))
        self.assertFalse(Question.objects.filter(pk=self.question.pk).exists())

    def test_another_user_cannot_delete_poll(self):
        other_user = get_user_model().objects.create_user(
            username="another-user",
            password="test-password",
        )
        self.client.force_login(other_user)

        response = self.client.post(
            reverse("polls:delete", args=(self.question.pk,))
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Question.objects.filter(pk=self.question.pk).exists())


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])



    def test_search_matches_question_text_case_insensitively(self):
        matching_question = create_question(question_text="Favorite color?", days=-1)
        create_question(question_text="Favorite food?", days=-2)

        response = self.client.get(reverse("polls:index"), {"q": "COLOR"})

        self.assertEqual(
            list(response.context["latest_question_list"]),
            [matching_question],
        )
        self.assertContains(response, "value=\"COLOR\"")


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)


    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)