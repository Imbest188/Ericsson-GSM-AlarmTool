function get_controller_list() {
    $.ajax({
        type: $(this).attr('GET'),
        url: controller_list_request,
        success: function (response) {
            $.each(response['controllers'], function (index, item){
                $("#controller_row").prepend(
                    `<button className="controller-button" role="button"
                        onClick="updateAlarms($(this).text()); return false;">${item}</button>`)

            });

        },
        error: function (response) {
            alert('err');
        }
    })


}