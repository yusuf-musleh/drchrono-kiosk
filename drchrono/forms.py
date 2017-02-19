from django import forms

class CheckinForm(forms.Form):
    first_name = forms.CharField(max_length=100, label='First Name', widget=forms.TextInput(attrs={'required': True, 'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, label='Last Name', widget=forms.TextInput(attrs={'required': True, 'class': 'form-control'}))
    SSN = forms.RegexField(regex='\d{3}-?\d{2}-?\d{4}', label='Social Security Number', widget=forms.TextInput(attrs={'required': True, 'class': 'form-control'}))