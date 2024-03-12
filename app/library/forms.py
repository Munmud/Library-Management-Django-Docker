# forms.py
from django import forms
from .models import Rating, Notebook, Note


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'review']


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'notebook']

    def __init__(self, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)
        # Make the notebook field read-only
        self.fields['notebook'].widget.attrs['readonly'] = True


class NotebookForm(forms.ModelForm):
    class Meta:
        model = Notebook
        fields = ['title', 'user']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(NotebookForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['user'].initial = user
            self.fields['user'].widget = forms.HiddenInput()
            self.fields['user'].required = False
