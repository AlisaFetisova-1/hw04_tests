
from django import forms
from django import forms

from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': "Текст поста",
            'group': "Группа",
        }
        help_text = {
            'text': "текст нового поста",
            'group': "группа, к которой будет относится пост",
        }
