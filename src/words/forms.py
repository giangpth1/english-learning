from django import forms

class TranslationForm(forms.Form):
    translation = forms.CharField(label='Vietnamese', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))