from django import forms
from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ProfileImage

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["age", "bio"]

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

        def clean_password1(self):
            password =self.cleaned_data.get("password1")

            if len(password) < 8:
                raise forms.ValidationError(
                    "パスワードは8文字以上にしてください"
                )
            return password
