from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse

from .forms import CheckinForm, DemographicsForm
from drchrono.models import Doctor, Patient, Appointment, Arrival

import json, requests, datetime, pytz

from dateutil import parser

from django.db.models import Q

def logout(request):
	auth_logout(request)
	return redirect('/login_page')


def get_datetime_in_doctor_timezone(request):
	user_timezone = request.COOKIES.get('tzname_from_user', 'UTC')
	return datetime.datetime.now(pytz.timezone(user_timezone))


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

def get_all_todays_appointments(headers, today, doctor_id):
	appointments = []
	appointments_url = 'https://drchrono.com/api/appointments?doctor=' + str(doctor_id) + '&date=' + str(today)
	while appointments_url:
		data = requests.get(appointments_url, headers=headers)
		data = data.json()
		for appointment in data['results']:
			# create an appointment to add to db if not found

			appointment_obj, created = Appointment.objects.get_or_create(appointment_id=appointment['id'], patient=Patient.objects.get(patient_id=appointment['patient']), doctor_id=appointment['doctor'])
			if created:
				appointment_obj.time_waited = None
			appointment_obj.status = appointment['status']
			appointment_obj.scheduled_time = appointment['scheduled_time']
			appointment_obj.save()
			appointment_obj.scheduled_time = parser.parse(appointment['scheduled_time'])

			appointments.append(appointment_obj)

		appointments_url = data['next'] # a JSON null on the last page
	return appointments


def get_average_wait_time(doctor_id):
	completed_appointments = Appointment.objects.filter((Q(status='Complete') | Q(status='In Session')) & Q(doctor_id=doctor_id))
	if not completed_appointments:
		return None

	completed_appointments = map(lambda x: x.time_waited, completed_appointments)

	avg = sum(completed_appointments, datetime.timedelta()) / len(completed_appointments)
	avg = str(avg).split('.')[0]
	return avg

def get_doctor_id_from_drchrono(headers):
	users_url = 'https://drchrono.com/api/users/current'
	data = requests.get(users_url, headers=headers).json()
	return data['doctor']


@login_required(login_url='/login_page')
def index(request):

	today = get_datetime_in_doctor_timezone(request)
	headers = build_headers(request)

	# fetch doctors id if not saved to doctor obj
	try:
		doctor = Doctor.objects.get(user=request.user)
		print 'found doctor'
	except:
		print 'calling api'
		doctor = Doctor(user=request.user)
		doctor.doctor_id = get_doctor_id_from_drchrono(headers)
		doctor.save()

	patients = get_doctors_patients(headers)
	todays_appointments = get_all_todays_appointments(headers, today, doctor.doctor_id)
	content = {}
	average_wait_time = get_average_wait_time(doctor.doctor_id)
	if average_wait_time:
		content['average_wait_time'] = average_wait_time

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


def get_patient_info(first_name, last_name, ssn, headers, doctor_id):
	patients_url = 'https://drchrono.com/api/patients?doctor=' + str(doctor_id) + '&first_name=' + first_name + '&last_name=' + last_name
	while patients_url:
		data = requests.get(patients_url, headers=headers)
		# print data.text
		data = data.json()
		print data
		for patient in data['results']: # find patient matching name and ssn
			if patient['first_name'] == first_name and patient['last_name'] == last_name and patient['social_security_number'] == ssn:
				return patient

		patients_url = data['next'] # a JSON null on the last page

	# no patient matched first name, last name and ssn
	return None


def get_patients_appointment_today(patient_id, headers, today):
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
			doctor_id = Doctor.objects.get(user=request.user).doctor_id

			print first_name, last_name, ssn
			today = get_datetime_in_doctor_timezone(request)
			headers = build_headers(request)
			patient_info = get_patient_info(first_name, last_name, ssn, headers, doctor_id)
			if patient_info:
				patients_appointment = get_patients_appointment_today(patient_info['id'], headers, today)
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

def change_appointment_status(appointment_id, headers, status):
	data = {}
	data['status'] = status
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
			if not change_appointment_status(demographics_form.cleaned_data['appointment_id'], headers, "Arrived"):
				demographics_form.add_error('cell_phone', 'Failed to change appointment status, please try again')
				return render(request, 'update_demographics.html', {'demographics_form': demographics_form})

			patients_arrived_before = len(Appointment.objects.filter(Q(status='Arrived') | Q(status='In Session')))

			# change appointment status locally
			appointment_obj = Appointment.objects.get(appointment_id=demographics_form.cleaned_data['appointment_id'])
			appointment_obj.status = "Arrived"
			appointment_obj.arrival_time = get_datetime_in_doctor_timezone(request)
			print 'before being saved', appointment_obj.arrival_time
			appointment_obj.save()

			content = {'patients_arrived_before': patients_arrived_before}

			# inform doctor that patient arrived and checked-in
			# adding appointment to Arrivals to be picked up on polling
			add_to_arrivals(appointment_obj)
			return render(request, 'checkin_complete.html', content)

		return render(request, 'update_demographics.html', {'demographics_form': demographics_form})
	else: # if GET request render checkin page
		checkin_form = CheckinForm()
		return render(request, 'kiosk.html', {'checkin_form': checkin_form})


def call_in_patient(request):
	if request.method == 'POST':

		# try:
		appointment_id = request.POST['appointment_id']
		datetime_patient_saw_doc = request.POST['current_date_time']
		datetime_patient_saw_doc = parser.parse(datetime_patient_saw_doc)

		appointment = Appointment.objects.get(appointment_id=appointment_id)
		appointment.status = "In Session"

		delta = datetime_patient_saw_doc - appointment.arrival_time

		appointment.time_waited = delta
		appointment.save()

		headers = build_headers(request)
		change_appointment_status(appointment_id, headers, "In Session")

		doctor_id = appointment.doctor_id
		avg_wait_time = get_average_wait_time(doctor_id)

		return JsonResponse({'status': 'success', 'avg_wait_time': avg_wait_time})
		# except:
			# return JsonResponse({'status': 'fail', 'message': 'Failed to call in patient and get new average wait time'})


def appointment_completed(request):
	if request.method == 'POST':
		appointment_id = request.POST['appointment_id']
		print appointment_id
		appointment = Appointment.objects.get(appointment_id=appointment_id)
		appointment.status = "Complete"
		appointment.save()

		headers = build_headers(request)
		change_appointment_status(appointment_id, headers, 'Complete')

		return HttpResponse('ok')


def add_to_arrivals(appointment_obj):
	app, created = Arrival.objects.get_or_create(appointment_id=appointment_obj.appointment_id, doctor_id=appointment_obj.doctor_id)


def poll_for_updates(request):
	if request.method == 'POST':
		try:
			print 'polling'
			doctor_id = Doctor.objects.get(user=request.user).doctor_id
			updates = Arrival.objects.filter(doctor_id=doctor_id)
			updates = map(lambda x: x.appointment_id, updates)

			Arrival.objects.all().delete()
			return JsonResponse({'status': 'success', 'updates': updates})
		except:
			return JsonResponse({'status': 'fail', 'message': 'Failed to poll'})
		# return HttpResponse('polled')


