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
		var firstname = $('#' + clist_id + "-firstname").val();
		var lastname = $('#' + clist_id + "-lastname").val();
		var phonenumber = $('#' + clist_id + "-phonenumber").val();
		var email = $('#' + clist_id + "-email").val();
		//Check to make sure information is valid
		var newrow_html = "<tr><td>" + firstname + "</td><td>" + lastname +
			"</td><td>" + phonenumber + "</td><td>" + email +
			"</td><td><button type='button' class='btn btn-default btn-xs' style='margin-right: -10px;' class='removeContact' id='" +
			clist_id + "-removecontact'><span class='glyphicon glyphicon-remove'></span></button></span></td></tr>";
		$('#' + clist_id + "-table").prepend(newrow_html);
		var tableRef = document.getElementById('#table').getElementsByTagName('tbody')[0];
		alert(tableRef);
		var newRow = tableRef.insertRow(tableRef.rows.length);
		var newCell = newRow.insertCell(0);
		var newText = document.createTextNode('New Row');
		newCell.appendChild(newText);

		//Add table to server database
		$.get('/notify/createcontact', {contactlist_id: clist_id, new_firstname: firstname, new_lastname: lastname, new_phonenumber: phonenumber, newemail: email}, function(data){
			//finish notification
		});
	});
});