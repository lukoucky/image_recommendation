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
        formData.append("file_to_upload", files[0]);

        $.ajax({ 
            type:'POST',
            url: '/upload_file',
            data : formData,
            beforeSend: function () { // Before we send the request, remove the .hidden class from the spinner and default to inline-block.
                document.getElementById("overlay").style.display = "block";
            },
            processData: false,
            contentType: false,
            success: function(response) {
                console.log(response);
                window.location.href = '/predict_similar/'+response.image_name;
            },
            complete: function () { // Set our complete callback, adding the .hidden class and hiding the spinner.
                document.getElementById("overlay").style.display = "none";
            },
        });
    };

    var loadSimilarImages = function(data)
    {   

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


$(".random_img_button").on('click', function()
{   
    console.log('Random button clicked');
    $.ajax({ 
        type:'GET',
        url: '/get_random_image',
        success: function(response) {
            console.log(response);
            window.location.href = '/predict_similar/'+response.image_name;
        }
    });
});