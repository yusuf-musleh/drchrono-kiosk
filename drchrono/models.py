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
	patient_id = models.IntegerField(unique=True)
	doctor_id = models.IntegerField()
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	email = models.EmailField()

	def __str__(self):
		return '%s %s %s' % (self.first_name, self.last_name, str(self.patient_id))



class Appointment(models.Model):
	appointment_id = models.CharField(unique=True, max_length=100)
	patient = models.ForeignKey('Patient')
	scheduled_time = models.DateTimeField(auto_now=False, auto_now_add=False)
	doctor_id = models.IntegerField()
	time_waited = models.DurationField(null=True)
	status = models.CharField(max_length=100, default='')
	arrival_time = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, default=None)

	def __str__(self):
		return '%s %s at %s' % (self.patient.first_name, self.patient.last_name, str(self.scheduled_time))



