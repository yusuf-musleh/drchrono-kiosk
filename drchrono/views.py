from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .forms import CheckinForm

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


@login_required(login_url='/login_page')
def kiosk(request):
	checkin_form = CheckinForm()
	content = {}
	content['checkin_form'] = checkin_form
	return render(request, 'kiosk.html', content)



def checkin_patient(request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		checkin_form = CheckinForm(request.POST)
		# check whether it's valid:
		if checkin_form.is_valid():
			# process the data in form.cleaned_data as required
			# ...
			# redirect to a new URL:
			return HttpResponse('ok')

		# should return jsonresponse
		print 'right here'
		return render(request, 'kiosk.html', {'checkin_form': checkin_form})
	checkin_form = CheckinForm()
	return render(request, 'kiosk.html', {'checkin_form': checkin_form})