$( document ).ready(function() {

	var timezone = jstz.determine();
	var tzname = timezone.name();

	Cookies.set('tzname_from_user', tzname);

	// starting timers with different startimes
	$('.time_diff').each(function () {
		var time_passed = $(this).text();
		console.log(time_passed);
		time_passed = get_time_seconds(time_passed); // in seconds
		var timer_id = $(this).parent("div").find('div[id*="timer_"]').attr('id');
		start_timer(timer_id, time_passed);
	})

});

// get time passed in seconds from text in the format 'xx hours, xx minutes'
function get_time_seconds(time_passed) {
	var seconds_passed = 0;
	var hours_index = time_passed.indexOf("hour");
	var minutes_index = time_passed.indexOf("minute");
	if (hours_index >= 0) {

		var additions = parseInt(time_passed[hours_index-3] + time_passed[hours_index-2]) * 60 * 60;

		if (isNaN(additions)){
			seconds_passed += parseInt(time_passed[hours_index-2]) * 60 * 60;
		}
		else{
			seconds_passed += additions;
		}
	}
	if (minutes_index >= 0) {

		var additions = parseInt(time_passed[minutes_index-3] + time_passed[minutes_index-2]) * 60;

		if (isNaN(additions)){
			seconds_passed += parseInt(time_passed[minutes_index-2]) * 60;
		}
		else {
			seconds_passed += additions
		}

	}
	return seconds_passed;
}


function start_timer(timer_id, time_passed) {
	$('#'+timer_id).timer({action:"start", seconds: time_passed});
}


function call_in_patient(appointment_id, csrf_token) {
	// show 'seeing patient', remove timer, show Done button to complete appointment
	$('#timer_'+appointment_id).remove();
	$('#status_'+appointment_id).removeClass('alert-success').addClass('alert-info');
	$('#status_'+appointment_id).html('<strong>In Progress<strong/>');
	$('#btn_'+appointment_id).html('Done');
	$('#btn_'+appointment_id).removeClass('btn-success').addClass('btn-info');
	$('#btn_'+appointment_id).attr("onclick","appointment_completed(" + appointment_id + ", '"+ csrf_token +"')");

	var current_date_time = new Date($.now());
	current_date_time = current_date_time.toUTCString()
	console.log(current_date_time);
	// add time_waited duration to appointment_obj and save in db

	$.post('/call_in_patient/',
		{
			csrfmiddlewaretoken: csrf_token,
			appointment_id: appointment_id,
			current_date_time: current_date_time

		},
		function(data){
			// data = $.parseJSON(data);
			console.log(data);
		}
	);


}


function appointment_completed(appointment_id, csrf_token) {
	// update status of appointment to 'complete' in db and drchrono api
	console.log('calling completed function');
	console.log(appointment_id);

	$('#status_'+appointment_id).removeClass('alert-info').addClass('alert-warning');
	$('#status_'+appointment_id).html('<strong>Completed<strong/>');
	$('#btn_'+appointment_id).remove();

	$.post('/appointment_completed/',
		{
			csrfmiddlewaretoken: csrf_token,
			appointment_id: appointment_id

		},
		function(data){
			// data = $.parseJSON(data);
			console.log(data);
		}
	);

}
