from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .forms import CheckinForm, DemographicsForm
from drchrono.models import Patient, Appointment

import json, requests, datetime


def logout(request):
	auth_logout(request)
	return redirect('/login_page')

def get_doctors_patients(headers):
	patients = []
	patients_url = 'https://drchrono.com/api/patients'
	while patients_url:
	    data = requests.get(patients_url, headers=headers).json()
	    # patients.extend(data['results'])
	    for patient in data['results']:
	    	# create a patient to add to db if not found
	    	patient_obj, created = Patient.objects.get_or_create(patient_id=patient['id'], doctor_id=patient['doctor'])
	    	if created:
	    		patient_obj.gender = patient['gender']
	    		patient_obj.first_name = patient['first_name']
	    		patient_obj.last_name = patient['last_name']
	    		patient_obj.email = patient['email']
	    		patient_obj.save()
	    	patients.append(patient_obj)


	    patients_url = data['next'] # A JSON null on the last page

	return patients

def get_all_todays_appointments(headers):
	appointments = []
	today = datetime.date.today()
	appointments_url = 'https://drchrono.com/api/appointments?date=' + str(today)
	while appointments_url:
		data = requests.get(appointments_url, headers=headers)
		data = data.json()
		for appointment in data['results']:
			# create an appointment to add to db if not found

			appointment_obj, created = Appointment.objects.get_or_create(appointment_id=appointment['id'], patient=Patient.objects.get(patient_id=appointment['patient']), scheduled_time=appointment['scheduled_time'], doctor_id=appointment['doctor'])
			if created:
				appointment_obj.time_waited = None
				appointment_obj.save()

			appointments.append(appointment_obj)

		appointments_url = data['next'] # a JSON null on the last page
	return appointments


@login_required(login_url='/login_page')
def index(request):

	# user_timezone = request.COOKIES.get('tzname_from_user', 'UTC')

	headers = build_headers(request)
	patients = get_doctors_patients(headers)
	todays_appointments = get_all_todays_appointments(headers)


	content = {}
	content['todays_appointments'] = todays_appointments

	return render(request, 'index.html', content)

def login_page(request):
	if request.user.is_authenticated():
		return redirect('/')
	else:
		return render(request, 'login.html')

def build_headers(request):
	# fetching doctor's acccess_token
	access_token = request.user.social_auth.get(provider='drchrono').extra_data['access_token']
	headers = {
		'Authorization': 'Bearer ' + access_token,
	}
	return headers


def get_patient_info(first_name, last_name, ssn, headers):
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


def get_patients_appointment_today(patient_id, headers):
	today = datetime.date.today()
	appointments_url = "https://drchrono.com/api/appointments?date=" + str(today) + "&patient=" + str(patient_id)
	# appointments_url = "https://drchrono.com/api/appointments?date=" + str(today)

	data = requests.get(appointments_url, headers=headers).json()
	results = data.get('results')
	if results != []:
		return results[0]

	# no appointment today for patient found
	return None


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

			headers = build_headers(request)
			patient_info = get_patient_info(first_name, last_name, ssn, headers)
			if patient_info:
				patients_appointment = get_patients_appointment_today(patient_info['id'], headers)
				if patients_appointment:
					# keeping track of initial data to check for any changes
					initial_data = { 'patient_id': patient_info['id'],
									 'appointment_id': patients_appointment['id'],
									 'cell_phone': patient_info['cell_phone'],
									 'email': patient_info['email'],
									 'zip_code': patient_info['zip_code'],
									 'address': patient_info['address'],
									 'emergency_contact_phone': patient_info['emergency_contact_phone'],
									 'emergency_contact_name': patient_info['emergency_contact_name']
					}
					initial_data['initial_form_data'] = json.dumps(initial_data, ensure_ascii=False)
					demographics_form = DemographicsForm(initial=initial_data)
					return render(request, 'update_demographics.html', {'demographics_form': demographics_form})
				else:
					checkin_form.add_error('first_name', 'You have no appointments today')
			else: # no appointments found for given name and ssn
				checkin_form.add_error('first_name', 'No patient found, please double check your name and ssn')
				return render(request, 'kiosk.html', {'checkin_form': checkin_form})

		return render(request, 'kiosk.html', {'checkin_form': checkin_form})

	# if GET request render kiosk page with empty form
	checkin_form = CheckinForm()
	return render(request, 'kiosk.html', {'checkin_form': checkin_form})


def submit_update(demographics_form, headers):
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

def set_appointment_to_arrived(appointment_id, headers):
	data = {}
	data['status'] = "Arrived"
	url = "https://drchrono.com/api/appointments/" + str(appointment_id)
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
		initial_data['initial_form_data'] = json.dumps(initial_data, ensure_ascii=False)
		demographics_form = DemographicsForm(request.POST, initial=initial_data)
		if demographics_form.is_valid():
			headers = build_headers(request)
			if 'initial_form_data' in demographics_form.changed_data:
				demographics_form.changed_data.remove('initial_form_data')
			if demographics_form.has_changed():
				print "The following fields changed: %s" % ", ".join(demographics_form.changed_data)

				if not submit_update(demographics_form, headers): # api update call return False on failure
					demographics_form.add_error('cell_phone', 'Failed to update your data, try again')
					return render(request, 'update_demographics.html', {'demographics_form': demographics_form})

			# change appointment status to arrived both locally and drchrono api
			if not set_appointment_to_arrived(demographics_form.cleaned_data['appointment_id'], headers):
				demographics_form.add_error('cell_phone', 'Failed to change appointment status, please try again')
				return render(request, 'update_demographics.html', {'demographics_form': demographics_form})

			# change appointment status locally
			appointment_obj = Appointment.objects.get(appointment_id=demographics_form.cleaned_data['appointment_id'])
			appointment_obj.status = "Arrived"
			appointment_obj.arrival_time = datetime.datetime.now()
			appointment_obj.save()

			# inform doctor that patient arrived and checked-in
			# ...
			return render(request, 'checkin_complete.html')

		return render(request, 'update_demographics.html', {'demographics_form': demographics_form})
	else: # if GET request render checkin page
		checkin_form = CheckinForm()
		return render(request, 'kiosk.html', {'checkin_form': checkin_form})

