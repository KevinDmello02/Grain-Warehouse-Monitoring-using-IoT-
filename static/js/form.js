$(document).ready(function(){
    $('form').on('submit',function(event) {

        $.ajax({
            data : {
                block : $('#block').val(),
                grain : $('#grain').val(),
                type : $('#type').val(),
                weight : $('#weight').val()
            },
            type : 'POST',
            url : '/process'
        })

        event.preventDefault();

    });
});