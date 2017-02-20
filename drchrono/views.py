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
		data = requests.get(patients_url, headers=headers).json()
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
				demographics_form = DemographicsForm(initial={'cell_phone': patient_info['cell_phone'], 'email': patient_info['email'], 'zip_code': patient_info['zip_code'], 'address': patient_info['address'], 'emg_contact_phone': patient_info['emergency_contact_phone'], 'emg_contact_name': patient_info['emergency_contact_name']})
				return render(request, 'update_demographics.html', {'demographics_form': demographics_form})
			else: # no appointments found for given name and ssn
				checkin_form.add_error('first_name', 'You have no appointments today, please double check your name and ssn')
				return render(request, 'kiosk.html', {'checkin_form': checkin_form})

		return render(request, 'kiosk.html', {'checkin_form': checkin_form})

	# if GET request render kiosk page with empty form
	checkin_form = CheckinForm()
	return render(request, 'kiosk.html', {'checkin_form': checkin_form})


@login_required(login_url='/login_page')
def update_demographics(request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		demographics_form = DemographicsForm(request.POST)
		if demographics_form.is_valid():
			return HttpResponse('ok')
		return render(request, 'update_demographics.html', {'demographics_form': demographics_form})
	else: # if GET request render checkin page
		checkin_form = CheckinForm()
		return render(request, 'kiosk.html', {'checkin_form': checkin_form})