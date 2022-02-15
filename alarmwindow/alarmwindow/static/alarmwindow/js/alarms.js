function context_menu() {
    document.body.addEventListener('contextmenu', function (ev) {
        ev.preventDefault();
        refresh_controller_update_id(current_controller);
        updateAlarms(current_controller);
        return false;
    }, false);
}

function timeToString(dt) {
    if (dt == null) return "";
    return dt.replace("-", ".")
        .replace("-", ".")
        .replace("T", " ")
        .replace("Z", " ");
}

function close_footer() {
    $('#alarm_text').html('');
    $('.alarm_footer').hide();
}

function get_alarm_text(alarm_id, controller_name) {
    $.ajax({
        type: $(this).attr('GET'), url: alarm_text_request, data: {
            alarm_id: alarm_id, controller: controller_name
        }, success: function (response) {

            let text = response['text'].toString().replaceAll('\n', '<br>');
            let row_count = text.split('<br>').length;
            let new_height = 30 * row_count + 'px';
            let new_margin = 100 - (4.5 * row_count);
            $('#alarm_text').html(text);
            $('.alarm_footer').css('height', new_height)
                .css('top', new_margin + '%').show();
        }, error: function (response) {
            $('#alarm_text').html('Error');
            $('.alarm_footer').css('height', '30px');
        }
    })
}

function controllerButtonClicked(node_name) {
    if (current_controller) {
        $('#' + current_controller).css({'color': '#79a9fc'});
    }
    current_controller = node_name;
    document.getElementById("controller_name").innerText = node_name;
    $('#' + node_name).css({'color': 'lightgreen'});
    $('.alarm_footer').hide();
    updateAlarms(node_name, get_old_update_id(node_name));
    $('html').animate({
        scrollTop: 0
    }, 30);
}

alarm_colors = {
    "A1/": "#ff7c73",
    "A2/": "#f58c5f",
    "A3/": "#fcd18b",
    "O1/": "#79a9fc",
    "O2/": "#8be8fc"
}

function get_color(td_text, is_active) {
    if (is_active) {
        for (const [identity, color] of Object.entries(alarm_colors)) {
            if (td_text.includes(identity)) {
                return "background-color:" + color;
            }
        }
    }
    return "background-color:darkslategray";
}

function add_row_click_listener() {
    $("tr.clickablerow").each(function (index) {
        let row = $(this).closest("tr");
        row[0].addEventListener("click", function () {
            let id = row.find("#id").text();
            get_alarm_text(id, current_controller);
        });
    });
}

function updateAlarms(node_name, id = -1) {
    $.ajax({
        type: $(this).attr('GET'), url: alarm_template, data: {node: node_name}, success: function (response) {
            $("#alarm_table tbody").html("");
            $.each(response["alarms"], function (index, item) {
                let td_class = "default";
                let is_valid = true;
                let is_active = item['is_active'];
                if (id > -1 && item["node_update_id"] > id) {
                    if (is_active) td_class = "red-td";
                    else td_class = 'gray-td';
                } else if (is_active === false) {
                    is_valid = false;
                }
                // language=HTML
                if (is_valid) {
                    $("#alarm_table tbody").prepend(`
                        <tr class="clickablerow" }>
                            <td class="coloredrow" style=${get_color(item["type"], is_active)}>${item["type"]}</td>
                            <td id="id" class=${td_class}>${item["id"]}</td>
                            <td class=${td_class}>${timeToString(item["raising_time"])}</td>
                            <td class="gray-td">${timeToString(item["ceasing_time"])}</td>
                            <td class=${td_class}>${item["managed_object"]}</td>
                            <td class=${td_class}>${item["object_name"]}</td>
                            <td class=${td_class}>${item["slogan"]}</td>
                            <td class=${td_class}>${item["descr"]}</td>
                        </tr>`)
                }
            });
            add_row_click_listener();
        }, error: function (response) {
            alert("Error");
            console.log(response)
        }
    });
    return false;
}
