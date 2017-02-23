from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.contrib import admin


import views


urlpatterns = [

	url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
    url(r'^login_page/', views.login_page, name='login_page'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),

    url(r'^checkin_patient/', views.checkin_patient, name='checkin_patient'),
    url(r'^update_demographics/', views.update_demographics, name='update_demographics'),

    url(r'^call_in_patient/', views.call_in_patient, name='call_in_patient'),
    url(r'^appointment_completed/', views.appointment_completed, name='appointment_completed'),
]
