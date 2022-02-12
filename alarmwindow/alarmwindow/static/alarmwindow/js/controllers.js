function start_alarm_updater(controllers) {
//background-image: linear-gradient(#541a0f 0, #0c0d0d 100%);
}

function init_controllers(controllers) {
    $.each(controllers, function (index, item){
        $("#controller_row").prepend(
            `<button class="controller-button" id=${item} role="button"
                onClick="updateAlarms($(this).text()); return false;">${item}</button>`)

    });
    $("#controller_row").prepend(`<label id="controller_name"></label>`);
}

function get_controller_list() {
    $.ajax({
        type: $(this).attr('GET'),
        url: controller_list_request,
        success: function (response) {
            var controllers = response['controllers'];
            if(controllers.length > 0) {
                init_controllers(controllers);
                current_controller = controllers[controllers.length - 1];
                updateAlarms(current_controller);
                document.getElementById("controller_name").innerText = current_controller;
            }
        },
        error: function (response) {
            alert('Не удалось получить список контроллеров');
        }
    })
}
