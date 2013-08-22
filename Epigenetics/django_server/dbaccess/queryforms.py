from django import forms

class QueryForm(forms.Form):
    database = forms.CharField(max_length = 15)
    collection = forms.CharField(max_length = 15)
    chromosome = forms.CharField(max_length = 2)
    start = forms.CharField(max_length = 15, required = False)
    end = forms.CharField(max_length = 15, required = False)
