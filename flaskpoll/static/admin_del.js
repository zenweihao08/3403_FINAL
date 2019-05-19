$(document).ready(function(){
	$('#movie_id_submit').on('click',function(event){
		id = $('#movie_id').val()
		consol.log(id);
		$.ajax({
			url:'/movie/del',
			dataType: "json",
			data: JSON.stringify({'id': '1'}),
			contentType:"application/json; charset=utf-8",
			type:'POST',
			success:function(response){
				alert("Success")
			},
			error: function(response){
				alert("Fail")
			}
		});
	});
});
