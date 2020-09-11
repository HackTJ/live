from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from django import forms
from judge.models import Annotator

class VolunteerSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(VolunteerSignupForm, self).__init__(*args, **kwargs)

        for fieldname, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'text-black'
            })

        self.fields['user_type'] = forms.ChoiceField(
            widget=forms.RadioSelect,
            choices=[('user_judge', 'Judge'), ('user_mentor', 'Mentor')]
        )

        self.fields['first_name'] = forms.CharField(
            max_length=150,
            widget=forms.TextInput(
                attrs={
                    'class': 'text-black'
                }
            )
        )

        self.fields['last_name'] = forms.CharField(
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

            annotator = Annotator(judge=user)
            annotator.save()
        else:
            mentor_group = Group.objects.get(name='mentor')
            user.groups.add(mentor_group)

        user.save()
        
        return user