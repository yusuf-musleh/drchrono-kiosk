$( document ).ready(function() {

	// starting timers with different startimes
	$('.time_diff').each(function () {
		var time_passed = $(this).text();
		time_passed = parseInt(time_passed.split(' ')[0]) * 60; // in seconds
		console.log(time_passed);
		var timer_id = $(this).parent("div").find('div[id*="timer_"]').attr('id');
		console.log(timer_id);
		start_timer(timer_id, time_passed);
	})

});



function start_timer(timer_id, time_passed) {
	$('#'+timer_id).timer({action:"start", seconds: time_passed});
}

