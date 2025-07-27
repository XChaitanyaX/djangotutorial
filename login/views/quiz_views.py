from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from login.forms import QuestionForm
from login.models import Answer, Choice, Question, Quiz, QuizSubmission


@method_decorator([login_required], name="dispatch")
class Questions(View):
    def _get_paginated_questions(self, page_number, quiz_id):
        """Helper method to set up paginator and return page object"""
        questions = Quiz.objects.get(id=quiz_id).questions.all()
        self.paginator = Paginator(questions, 2)
        return self.paginator.get_page(page_number)

    def _render_questions(self, request, page_obj, quiz_id, form=None):
        """Helper method to render the questions template"""
        if form is None:
            form = QuestionForm(questions=page_obj.object_list)

        return render(
            request,
            "login/questions.html",
            {
                "page_obj": page_obj,
                "form": form,
                "quiz_id": quiz_id,
            },
        )

    def get(self, request, quiz_id):
        page_number = request.GET.get("page", 1)
        page_obj = self._get_paginated_questions(page_number, quiz_id)
        if not page_obj.object_list:
            messages.info(
                request,
                "No questions available \
                or you have already answered all questions.",
            )
            return redirect("login:dashboard")
        request.session["answers"] = {}
        return self._render_questions(request, page_obj, quiz_id)

    def post(self, request, quiz_id):
        # Store current page answers in session
        if "answers" not in request.session:
            request.session["answers"] = {}

        # Update session with current page answers
        current_answers = {
            k: v for k, v in request.POST.items() if k.startswith("question")
        }
        request.session["answers"].update(current_answers)
        request.session.modified = True

        if len(request.session["answers"]) == len(Question.objects.all()):
            submission = QuizSubmission.objects.create(
                user=request.user,
                quiz_id=quiz_id,
            )
            Answer.objects.bulk_create(
                Answer(
                    submission=submission,
                    question=Question.objects.get(
                        id=int(q_id.replace("question_", ""))
                    ),
                    answer_choice=Choice.objects.get(
                        id=int(choice_id.replace("question_", ""))
                    ),
                )
                for q_id, choice_id in request.session["answers"].items()
            )
            request.session.pop("answers", None)
            return redirect("login:dashboard")

        # Initialize paginator for POST requests
        page_number = request.POST.get("page", 1)
        page_obj = self._get_paginated_questions(page_number, quiz_id)

        # Initialize form with the current page's questions
        form = QuestionForm(questions=page_obj.object_list)
        return self._render_questions(request, page_obj, quiz_id, form)


@login_required(login_url="login:login")
@never_cache
def result(request, quiz_id):
    if request.method != "GET":
        return redirect("login:dashboard")

    total = 0
    correct_count = 0
    results = []

    correct_answers = {
        choice.question.id: choice.id
        for choice in Choice.objects.filter(is_correct=True)
    }

    quiz = Quiz.objects.get(id=quiz_id)
    questions = quiz.questions.all()

    submission = QuizSubmission.objects.get(user=request.user, quiz=quiz)
    for question in questions:
        selected_choice_id = (
            submission.answers.filter(question=question)
            .values_list("answer_choice", flat=True)
            .first()
        )
        try:
            selected_choice = Choice.objects.get(id=selected_choice_id)
            correct_choice_id = correct_answers.get(question.id)

            is_correct = selected_choice.id == correct_choice_id
            if is_correct:
                correct_count += 1

            total += 1
            results.append(
                {
                    "question": question.text,
                    "selected_choice": selected_choice.text,
                    "correct_answer": Choice.objects.get(
                        id=correct_choice_id
                    ).text,
                    "is_correct": is_correct,
                }
            )

        except (Choice.DoesNotExist, KeyError):
            messages.error(request, "Invalid or missing answer data.")
            return redirect("login:questions")

    score = (correct_count / total) * 100 if total > 0 else 0

    return render(
        request,
        "login/result.html",
        {
            "score": round(score, 2),
            "total": total,
            "correct_count": correct_count,
            "results": results,
        },
    )


@login_required(login_url="login:login")
def quiz_list(request):
    """View to list all quizzes"""
    quizzes = Quiz.objects.all().order_by("-created_at")
    return render(request, "login/quiz_list.html", {"quizzes": quizzes})
