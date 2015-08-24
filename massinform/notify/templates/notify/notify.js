$(document).ready(function(){
	//Define variables
	var existing_emails_and_numbers = new Array();
	{% for clist in contactlists %}
		{% for c in clist.contacts%}
			projects_loaded.splice(projects_loaded.length - 1, 0, '{{ c.phonenumber }}');
			projects_loaded.splice(projects_loaded.length - 1, 0, '{{ c.email }}');
		{% endfor %}
	{% endfor %}
	//Scripts for processing new contact creations
	$(".createbtn").click(function(event){
		var clist_id = $(this).attr('id');
		clist_id.replace('-createbtn', '');

		//Create table rows
		var firstname = "";
		var lastname = "";
		var phonenumber = "";
		var email = "";
		//Check to make sure information is valid
		if firstname.length < 3 && firstname.length > 50{
			
		}

		var newrow_html = "<tr><td>" + firstname + "</td><td>" + lastname +
			"</td><td>" + phonenumber + "</td><td>" + email +
			"</td><td><button type='button' class='btn btn-default btn-xs' style='margin-right: -10px;' class='removeContact' id='" +
			clist_id + "-removecontact'><span class='glyphicon glyphicon-remove'></span></button></span></td></tr>";
		$("#" + clist_id + "-table").prepend(newrow_html);

		//Add table to server database
		$.get('/notify/createcontact', {contactlist_id: clist_id, new_firstname: firstname, new_lastname: lastname, new_phonenumber: phonenumber, newemail: email}, function(data){
			//finish notification
		});
	});
});