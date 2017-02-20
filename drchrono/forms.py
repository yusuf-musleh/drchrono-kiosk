from django import forms

class CheckinForm(forms.Form):
	first_name = forms.CharField(max_length=100, label='First Name', widget=forms.TextInput(attrs={'required': True, 'class': 'form-control'}))
	last_name = forms.CharField(max_length=100, label='Last Name', widget=forms.TextInput(attrs={'required': True, 'class': 'form-control'}))
	SSN = forms.RegexField(regex='\d{3}-?\d{2}-?\d{4}', label='Social Security Number', error_messages={'invalid': 'Must enter valid US Social Security Number XXX-XX-XXXX'}, widget=forms.TextInput(attrs={'required': True, 'class': 'form-control'}))

	# Handeling form filled with only white spaces
	def clean(self):
		cleaned_data = super(CheckinForm, self).clean()
		first_name = cleaned_data.get("first_name")
		last_name = cleaned_data.get("last_name")
		SSN = cleaned_data.get("SSN")

		msg = "Must not be only white spaces."

		if first_name and first_name.strip() == "":
			self.add_error('first_name', msg)
		if last_name and last_name.strip() == "":
			self.add_error('last_name', msg)
		if SSN and SSN.strip() == "":
			self.add_error('SSN', msg)