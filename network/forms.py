from django import forms
from .models import Post, Following

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['owner', 'content', 'likes', 'timestamp']
        widgets = {
            'owner': forms.HiddenInput(),
            'likes': forms.HiddenInput(),
            'timestamp': forms.HiddenInput()
        }

class FollowForm(forms.ModelForm):
    class Meta:
        model = Following
        fields = ['followingUser', 'followedUser']
        widgets = {
            'followingUser': forms.HiddenInput(),
            'followedUser': forms.HiddenInput()
        }
