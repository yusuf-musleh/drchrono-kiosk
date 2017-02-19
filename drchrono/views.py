from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


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
	content = {}
	return render(request, 'kiosk.html')
