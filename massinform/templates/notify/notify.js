$(document).ready(function(){
	//Define variables
	var existing_emails_and_numbers = new Array();
	{% for clist in contactlists %}
		{% for c in clist.contacts%}
			existing_emails_and_numbers.splice(existing_emails_and_numbers.length - 1, 0, '{{ c.phonenumber }}');
			existing_emails_and_numbers.splice(existing_emails_and_numbers.length - 1, 0, '{{ c.email }}');
		{% endfor %}
	{% endfor %}
	//Scripts for processing new contact creations
	$(".createbtn").click(function(event){
		event.preventDefault();
		var clist_id = $(this).attr('id');
		clist_id = clist_id.replace('-createbtn', '');
		//Create table rows

		var firstname = $('#' + clist_id + "-firstname").val();
		var lastname = $('#' + clist_id + "-lastname").val();
		var phonenumber = $('#' + clist_id + "-phonenumber").val();
		var email = $('#' + clist_id + "-email").val();

		if($.inArray(email, existing_emails_and_numbers) > -1){
			alert('A contact with this email address already exists.')
		} else if ($.inArray(phonenumber, existing_emails_and_numbers) > -1) {
			alert('A contact with this phone number already exists.')
		} else if (email == "" && phonenumber == ""){
			alert('A contact must have an email address or phone number.')
		} else {
			//Add table to server database
			$.get("/notify/createcontact/", {contactlist: clist_id, new_firstname: firstname, new_lastname: lastname, new_phonenumber: phonenumber, new_email: email}, function(data){
				//Contact created
				window.location.reload(true);
			});
		}
	});
	
	//Remove a contact
	$(".removecontact").click(function(event){
		//Get row of table and resulting information
		var $row = $(this).closest("tr");
		var phonenumber = $row.find("td:nth-child(3)").text();
		var email = $row.find("td:nth-child(4)").text()

		//Dynamically kill the row and get clist_id
		event.preventDefault();
		var clist_id = $(this).attr('id');
		clist_id = clist_id.replace('-removeContact', '');
		//return window.confirm("Are you sure you want to delete this contact?");
		$.get("/notify/deletecontact", {contactlist: clist_id, email: email, phonenumber: phonenumber}, function(data){
			//Contact deleted
			window.location.reload(true);
		});
	});

	$('#notModal').on('show.bs.modal', function(e) {
    	var clist_id = $(e.relatedTarget).data('clist-id');
    	$(e.currentTarget).find('input[name="clist_id"]').val(clist_id);
	});
});