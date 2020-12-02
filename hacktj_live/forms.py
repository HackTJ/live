from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from django import forms
from judge.models import Annotator


class VolunteerSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(VolunteerSignupForm, self).__init__(*args, **kwargs)

        self.fields["user_type"] = forms.MultipleChoiceField(
            required=True,
            widget=forms.CheckboxSelectMultiple(
                attrs={
                    "class": "rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                }
            ),
            choices=[("user_judge", "Judge"), ("user_mentor", "Mentor")],
        )

        # TODO: full name? https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/autocomplete#Values:~:text=Using%20%22name%22%20rather%20than%20breaking%20the,names%20and%20how%20they%20are%20structured
        # although the default Django User model uses first_name and last_name
        # https://docs.djangoproject.com/en/3.1/ref/contrib/auth/#django.contrib.auth.models.User.first_name:~:text=first_name%C2%B6,Optional%20(blank%3DTrue).%20150%20characters%20or%20fewer.
        self.fields["first_name"] = forms.CharField(max_length=150)
        self.fields["last_name"] = forms.CharField(max_length=150)

    def save(self, request):
        user = super(VolunteerSignupForm, self).save(request)

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if "user_judge" in self.cleaned_data["user_type"]:
            judge_group, _ = Group.objects.get_or_create(name="judge")
            user.groups.add(judge_group)

            annotator = Annotator(judge=user)
            annotator.save()
        if "user_mentor" in self.cleaned_data["user_type"]:
            mentor_group, _ = Group.objects.get_or_create(name="mentor")
            user.groups.add(mentor_group)

        user.save()

        return user
