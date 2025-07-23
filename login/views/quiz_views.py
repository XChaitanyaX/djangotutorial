from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from login.forms import QuestionForm
from login.models import Answer, Choice, Question


@method_decorator([login_required], name="dispatch")
class Questions(View):
    def _get_paginated_questions(self, request, page_number):
        """Helper method to set up paginator and return page object"""
        # Get IDs of questions the user has already answered
        answered = Answer.objects.filter(user=request.user).values_list(
            "question_id", flat=True
        )
        # Exclude answered questions
        questions = Question.objects.exclude(id__in=answered)
        self.paginator = Paginator(questions, 2)
        return self.paginator.get_page(page_number)

    def _render_questions(self, request, page_obj, form=None):
        """Helper method to render the questions template"""
        if form is None:
            form = QuestionForm(questions=page_obj.object_list)

        return render(
            request,
            "login/questions.html",
            {
                "page_obj": page_obj,
                "form": form,
            },
        )

    def get(self, request):
        page_number = request.GET.get("page", 1)
        page_obj = self._get_paginated_questions(request, page_number)
        if not page_obj.object_list:
            messages.info(
                request,
                "No questions available \
                or you have already answered all questions.",
            )
            return redirect("login:dashboard")
        request.session["answers"] = {}
        return self._render_questions(request, page_obj)

    def post(self, request):
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
            print(f"{request.session['answers']}")
            Answer.objects.bulk_create(
                Answer(
                    user=request.user,
                    question=Question.objects.get(
                        id=int(q_id.replace("question_", ""))
                    ),
                    answer_choice=Choice.objects.get(
                        id=int(choice_id.replace("question_", ""))
                    ),
                )
                for q_id, choice_id in request.session["answers"].items()
            )
            print(f"All questions answered: {request.session['answers']}")
            return redirect("login:dashboard")

        # Initialize paginator for POST requests
        page_number = request.POST.get("page", 1)
        page_obj = self._get_paginated_questions(request, page_number)

        # Initialize form with the current page's questions
        form = QuestionForm(questions=page_obj.object_list)
        return self._render_questions(request, page_obj, form)


@login_required(login_url="login:login")
@never_cache
def result(request):
    if request.method != "POST":
        return redirect("login:questions")

    total = 0
    correct_count = 0
    results = []

    correct_answers = {
        a.question_id: a.answer_choice_id
        for a in Answer.objects.filter(user=None)
    }

    already_answered = Answer.objects.filter(user=request.user).values_list(
        "question_id", flat=True
    )
    unanswered_questions = Question.objects.exclude(id__in=already_answered)

    for question in unanswered_questions:
        selected_choice_id = request.POST.get(f"question{question.id}")
        if not selected_choice_id:
            messages.error(request, "Please answer all questions.")
            return redirect("login:questions")

        try:
            selected_choice = Choice.objects.get(id=selected_choice_id)
            correct_choice_id = correct_answers.get(question.id)

            # Save the user's answer
            Answer.objects.create(
                user=request.user,
                question=question,
                answer_choice=selected_choice,
            )

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
