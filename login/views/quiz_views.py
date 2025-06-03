from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from login.models import Answer, Choice, Question


@login_required(login_url="login:login")
@never_cache
def questions(request):
    answered = Answer.objects.filter(user=request.user).values_list(
        "question_id", flat=True
    )
    questions = Question.objects.exclude(id__in=answered)
    return render(request, "login/questions.html", {"questions": questions})


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
