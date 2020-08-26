from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['owner', 'content', 'likes', 'timestamp']
        widgets = {
            'owner': forms.HiddenInput(),
            'likes': forms.HiddenInput(),
            'timestamp': forms.HiddenInput()
        }
