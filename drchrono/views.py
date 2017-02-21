from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .forms import CheckinForm, DemographicsForm

import json, requests, datetime


def logout(request):
	auth_logout(request)
	return redirect('/login_page')


@login_required(login_url='/login_page')
def index(request):

	# user_timezone = request.COOKIES.get('tzname_from_user', 'UTC')

	# getting access token for user
	access_token = request.user.social_auth.get(provider='drchrono').extra_data['access_token']

	# fetching all user's patients information
	# before, today, after, no_birthdays = get_patients_data(access_token, user_timezone)
	content = {}
	# content['birthdays_before'] = before
	# content['birthdays_today'] = today
	# content['birthdays_after'] = after
	# content['no_birthdays'] = no_birthdays

	return render(request, 'index.html', content)

def login_page(request):
	if request.user.is_authenticated():
		return redirect('/')
	else:
		return render(request, 'login.html')


def get_patient_info(first_name, last_name, ssn, access_token):
	headers = {
		'Authorization': 'Bearer ' + access_token,
	}
	patients_url = 'https://drchrono.com/api/patients?first_name=' + first_name + '&last_name=' + last_name
	while patients_url:
		data = requests.get(patients_url, headers=headers)
		# print data.text
		data = data.json()
		for patient in data['results']: # find patient matching name and ssn
			if patient['first_name'] == first_name and patient['last_name'] == last_name and patient['social_security_number'] == ssn:
				return patient

		patients_url = data['next'] # a JSON null on the last page

	# no patient matched first name, last name and ssn
	return None


def get_todays_appointments(access_token):
	headers = {
		'Authorization': 'Bearer ' + access_token,
	}
	today = datetime.date.today()
	appointments_url = "https://drchrono.com/api/appointments?date=" + str(today)
	while appointments_url:
		data = requests.get(appointments_url, headers=headers).json()
		appointments_url = data['next'] # a JSON null on last page


@login_required(login_url='/login_page')
def checkin_patient(request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request
		checkin_form = CheckinForm(request.POST)
		# check whether it's valid:
		if checkin_form.is_valid():
			# processing the data in checkin form
			first_name = checkin_form.cleaned_data['first_name'].strip()
			last_name = checkin_form.cleaned_data['last_name'].strip()
			ssn = checkin_form.cleaned_data['SSN'].strip()

			print first_name, last_name, ssn

			# fetching doctor's acccess_token
			access_token = request.user.social_auth.get(provider='drchrono').extra_data['access_token']

			patient_info = get_patient_info(first_name, last_name, ssn, access_token)
			if patient_info:
				get_todays_appointments(access_token)
				initial_data = {'patient_id': patient_info['id'], 'cell_phone': patient_info['cell_phone'], 'email': patient_info['email'], 'zip_code': patient_info['zip_code'], 'address': patient_info['address'], 'emergency_contact_phone': patient_info['emergency_contact_phone'], 'emergency_contact_name': patient_info['emergency_contact_name']}
				initial_data['initial_form_data'] = json.dumps(initial_data)
				demographics_form = DemographicsForm(initial=initial_data)
				return render(request, 'update_demographics.html', {'demographics_form': demographics_form})
			else: # no appointments found for given name and ssn
				checkin_form.add_error('first_name', 'You have no appointments today, please double check your name and ssn')
				return render(request, 'kiosk.html', {'checkin_form': checkin_form})

		return render(request, 'kiosk.html', {'checkin_form': checkin_form})

	# if GET request render kiosk page with empty form
	checkin_form = CheckinForm()
	return render(request, 'kiosk.html', {'checkin_form': checkin_form})


def submit_update(demographics_form, access_token):

	headers = {
		'Authorization': 'Bearer ' + access_token,
	}
	data = {}
	changed_fields = demographics_form.changed_data
	for field in changed_fields:
		data[field] = demographics_form.cleaned_data[field]

	url = 'https://drchrono.com/api/patients/' + str(demographics_form.cleaned_data['patient_id'])

	r = requests.patch(url, data=data, headers=headers)

	print r.status_code, r.text

	if r.status_code == 204: # HTTP 204 patch successful
		return True

 	# patch failed
	return False


@login_required(login_url='/login_page')
def update_demographics(request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		initial_data = json.loads(request.POST['initial_form_data'])
		initial_data['initial_form_data'] = json.dumps(initial_data)
		demographics_form = DemographicsForm(request.POST, initial=initial_data)
		if demographics_form.is_valid():
			if demographics_form.has_changed():
				print "The following fields changed: %s" % ", ".join(demographics_form.changed_data)
				# fetching doctor's acccess_token
				access_token = request.user.social_auth.get(provider='drchrono').extra_data['access_token']
				if submit_update(demographics_form, access_token): # api update call successful

					# inform doctor patient arrived and checked-in

					return render(request, 'checkin_complete.html')

				demographics_form.add_error('cell_phone', 'Failed to update your data, try again')
				return render(request, 'update_demographics.html', {'demographics_form': demographics_form})
			else:
				print 'nothing changed'
				return render(request, 'checkin_complete.html')
			return HttpResponse('ok')
		return render(request, 'update_demographics.html', {'demographics_form': demographics_form})
	else: # if GET request render checkin page
		checkin_form = CheckinForm()
		return render(request, 'kiosk.html', {'checkin_form': checkin_form})

