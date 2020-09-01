$(function(){
    var reloadPage = function(data){
        // window.location.reload(false); 
        // window.location.href = '/show_similar/'+data;  
    };

    var fileUploadFail = function(data){};

    var dragHandler = function(evt){
        evt.preventDefault();
    };

    var dropHandler = function(evt){
        evt.preventDefault();
        var files = evt.originalEvent.dataTransfer.files;

        var formData = new FormData();
        formData.append("file2upload", files[0]);

        $.ajax({ 
            type:'POST',
            url: '/sendfile',
            data : formData,
            processData: false,
            contentType: false,
            success: function(response) {
                console.log(response);
                window.location.href = '/show_similar/'+response.image_name;
            }
        });
    };

    var dropHandlerSet = {
        dragover: dragHandler,
        drop: dropHandler
    };

    $(".droparea").on(dropHandlerSet);
});

$('input[type="checkbox"]').on('change', function() {
   $('input[type="checkbox"]').not(this).prop('checked', false);
});