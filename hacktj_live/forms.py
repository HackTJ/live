from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from django import forms
from judge.models import Annotator

class VolunteerSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(VolunteerSignupForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-black'
            })

        self.fields['user_type'] = forms.ChoiceField(
            widget=forms.RadioSelect,
            choices=[('user_judge', 'Judge'), ('user_mentor', 'Mentor')]
        )

        self.fields['name'] = forms.CharField(
            max_length=150,
            widget=forms.TextInput(
                attrs={
                    'class': 'text-black'
                }
            )
        )

    def save(self, request):
        user = super(VolunteerSignupForm, self).save(request)

        user.name = self.cleaned_data["name"]

        print('r', request.user.groups.values_list('name',flat = True))
        print('g', list(Group.objects.all()))
        if self.cleaned_data["user_type"] == "user_judge":
            judge_group, _ = Group.objects.get_or_create(name='judge')
            user.groups.add(judge_group)

            annotator = Annotator(judge=user)
            annotator.save()
        elif self.cleaned_data["user_type"] == "user_mentor":
            mentor_group, _ = Group.objects.get_or_create(name='mentor')
            user.groups.add(mentor_group)
        else:
            # raise
            pass

        user.save()
        
        return user