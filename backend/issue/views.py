from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from issue.forms import IssuesForm


def report_issues(request):
    form: IssuesForm
    if request.method == "POST":
        form = IssuesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully reported issue!")
            return redirect("")
    else:
        form = IssuesForm()

    return render(request, "issue/report_issues.html", {"form": form})
