from django import forms



class ReviewForm(forms.Form):
    ratings = forms.IntegerField(max_value=5, min_value=1)
    content = forms.CharField(label='', widget=forms.Textarea)
