from django import forms

class CheckinForm(forms.Form):
	first_name = forms.CharField(max_length=100, label='First Name', widget=forms.TextInput(attrs={'required': True, 'class': 'form-control'}))
	last_name = forms.CharField(max_length=100, label='Last Name', widget=forms.TextInput(attrs={'required': True, 'class': 'form-control'}))
	SSN = forms.RegexField(regex='^\d{3}-?\d{2}-?\d{4}$', label='Social Security Number', error_messages={'invalid': 'Must enter valid US Social Security Number XXX-XX-XXXX'}, widget=forms.TextInput(attrs={'required': True, 'class': 'form-control'}))

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


class DemographicsForm(forms.Form):
	patient_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
	cell_phone = forms.RegexField(required=False, regex='^((\(\d{3}\) ?)|(\d{3}-))?\d{3}-\d{4}$', label='Cell Phone', error_messages={'invalid': 'Must enter valid US phone number in the format (999) 999-9999'}, widget=forms.TextInput(attrs={'class': 'form-control'}))
	email = forms.EmailField(required=False, label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
	zip_code = forms.RegexField(required=False, regex='^\d{5}$', label='Zip Code', error_messages={'invalid': 'Enter a valid zip-code in the format 00000'}, widget=forms.TextInput(attrs={'class': 'form-control'}))
	address = forms.CharField(required=False, label='Address', widget=forms.TextInput(attrs={'class': 'form-control'}))
	emergency_contact_phone = forms.RegexField(required=False, regex='^((\(\d{3}\) ?)|(\d{3}-))?\d{3}-\d{4}$', label='Emergency Cell Phone', error_messages={'invalid': 'Must enter valid US phone number in the format (999) 999-9999'}, widget=forms.TextInput(attrs={'class': 'form-control'}))
	emergency_contact_name = forms.CharField(required=False, max_length=100, label='Emergency Contact Name', widget=forms.TextInput(attrs={'class': 'form-control'}))
	initial_form_data = forms.CharField(required=False, widget=forms.HiddenInput())
