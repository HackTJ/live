from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from django import forms

class VolunteerSignupForm(SignupForm):
    user_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[('user_judge', 'Judge'), ('user_mentor', 'Mentor')]
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class': 'text-black'
            }
        )
    )
    last_name = forms.CharField(
        max_length=149,
        widget=forms.TextInput(
            attrs={
                'class': 'text-black'
            }
        )
    )

    def save(self, request):
        user = super(VolunteerSignupForm, self).save(request)

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if self.cleaned_data["user_type"] == "user_judge":
            judge_group = Group.objects.get(name='judge')
            user.groups.add(judge_group)
        else:
            mentor_group = Group.objects.get(name='mentor')
            user.groups.add(mentor_group)

        user.save()
        
        return user