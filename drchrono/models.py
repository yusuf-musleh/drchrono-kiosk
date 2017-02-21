from django.db import models


class Patient(models.Model):
	MALE = 'M'
	FEMALE = 'F'
	OTHER = 'O'
	GENDER_CHOICES = (
		(MALE, 'Male'),
		(FEMALE, 'Female'),
		(OTHER, 'Other'),
	)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=OTHER)
	patient_id = models.IntegerField()
	doctor_id = models.IntegerField()
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	email = models.EmailField()



class Appointment(models.Model):
	patient = models.ForeignKey('Patient')
	scheduled_time = models.DateTimeField(auto_now=False, auto_now_add=False)
	doctor_id = models.IntegerField()
	time_waited = models.DurationField()



