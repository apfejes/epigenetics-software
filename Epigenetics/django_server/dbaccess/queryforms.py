from django import forms

class QueryForm(forms.Form):
    collection = forms.CharField(max_length=15)
    chr = forms.CharField(max_length=2)
    start = forms.CharField(max_length=15,required=False)
    end = forms.CharField(max_length=15,required=False)