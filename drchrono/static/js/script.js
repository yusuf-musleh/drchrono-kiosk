$( document ).ready(function() {
	var timezone = jstz.determine();
	var tzname = timezone.name();

	Cookies.set('tzname_from_user', tzname);

	$('#myModal').on('show.bs.modal', function (event) {
		  var button = $(event.relatedTarget); // Button that triggered the modal
		  var patient_name = button.data('patient'); // Extract info from button pressed
		  var patient_email = button.data('email');
		  var dr_sender = button.data('doctor');
		  var subject = "Birthday Wishes!"

		  var modal = $(this);
		  modal.find('.modal-title').text("Wish " + patient_name + " a Happy Birthday!");
		  $('#recipient-email').val(patient_email);
		  $('#subject-name').val(subject);
		  modal.find('.modal-body textarea').val("Happy Birthday " + patient_name + "!\n\nDr. " + dr_sender);
	})

});


function submit_wish_birthday(url, csrf_token){

	var subject = $('#subject-name').val().trim();
	var recipient = $('#recipient-email').val().trim();
	var message = $('#message-text').val().trim();


	$.post(url,
			{
				csrfmiddlewaretoken: csrf_token,
				subject: subject,
				recipient: recipient,
				message: message

			},
			function(data){
				data = $.parseJSON(data);
				if (data['status'] == 'success'){

				   $('#myModal').modal('toggle');
				   $('#message_success').html("<div class=\"alert alert-success alert-dismissable fade in\">\
    				  <a href=\"#\" class=\"close\" data-dismiss=\"alert\" aria-label=\"close\">&times;</a>\
					  <strong>Success! </strong>" + data['message'] + "\
					</div>");

				}
				else {
				   $('#message_failed').html("<div class=\"alert alert-danger alert-dismissable fade in\">\
				   	  <a href=\"#\" class=\"close\" data-dismiss=\"alert\" aria-label=\"close\">&times;</a>\
					  <strong>Error! </strong>" + data['message'] + "\
					</div>");
				}
			}
		);

	return false;

}