var updates = {}
var unchecked_updates = {}

function process_updates(response) {
    //updates.keys().length;
    $.each(response["updates"], function (index, item) {
        var name = item['name'];
        var value = item['update_id'];
        if (updates.hasOwnProperty(name)){
            if(updates[name] != value){
                if(name == current_controller){
                    updateAlarms(current_controller, get_controller_update_id(name));
                    unchecked_updates[name] = value;
                }
                else {
                    $('#'+name).css({'color': 'red'});
                }
            }
        }
        else {
            updates[name] = value;
            unchecked_updates = value;
            init_controllers([name]);
        }
    });
}

function get_controllers_update_id() {
    $.ajax({
        type: $(this).attr('GET'),
        url: get_updates,
        success: function (response) {
            process_updates(response);
        },
        error: function (response) {
            console.log('update error');
        }
    })
}

function get_controller_update_id(controller) {
    return updates[controller];
}

function refresh_controller_update_id(controller) {
    updates[controller] = unchecked_updates[controller];
}

function start_alarm_updater() {
    get_controllers_update_id();
    setInterval(function () {
        get_controllers_update_id();
    }, 5000);
}

function init_controllers(controllers) {
    $.each(controllers, function (index, item){
        $("#controller_row").prepend(
            `<button class="controller-button" id=${item} role="button"
                onClick="controllerButtonClicked($(this).text()); return false;">${item}</button>`)

    });
    //$("#controller_row").prepend(`<label id="controller_name"></label>`);
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
