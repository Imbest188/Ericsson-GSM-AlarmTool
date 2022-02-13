function timeToString(dt) {
    if (dt == null)
        return "";
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
        type: $(this).attr('GET'),
        url: alarm_text_request,
        data: {
            alarm_id: alarm_id,
            controller: controller_name
        },
        success: function (response) {

            var text = response['text'].toString().replaceAll('\n', '<br>');
            var row_count = text.split('<br>').length;
            var new_height = 30 * row_count + 'px';
            $('#alarm_text').html(text);
            $('.alarm_footer').css('height', new_height).show();
        },
        error: function (response) {
            $('#alarm_text').html('Error');
            $('.alarm_footer').css('height', '30px');
        }
    })


}

function updateAlarms(node_name) {
    if (node_name) {
        current_controller = node_name;
        document.getElementById("controller_name").innerText = node_name;
    }
    $('.alarm_footer').hide();
    $('html').animate({
            scrollTop: 0
        }, 30
    );
    $.ajax({
        type: $(this).attr('GET'),
        url: alarm_template,
        data: {node: node_name},
        success: function (response) {
            $("#alarm_table tbody").html("");
            $.each(response["alarms"], function (index, item) {
                // language=HTML
                $("#alarm_table tbody").prepend(
                    `
                        <tr class="clickablerow">
                            <td class="coloredrow">${item["type"]}</td>
                            <td class="id">${item["id"]}</td>
                            <td>${timeToString(item["raising_time"])}</td>
                            <td>${item["managed_object"]}</td>
                            <td>${item["object_name"]}</td>
                            <td>${item["slogan"]}</td>
                            <td>${item["descr"]}</td>
                        </tr>`
                )
            });
            $('td.coloredrow').each(function () {
                var x = $(this).text();
                if (x.includes("A1/")) $(this).css({background: '#ff7c73'});
                else if (x.includes("A2/")) $(this).css({background: '#f58c5f'});
                else if (x.includes("A3/")) $(this).css({background: '#fcd18b'});
                else if (x.includes("O1/")) $(this).css({background: '#79a9fc'});
                else if (x.includes("O2/")) $(this).css({background: '#8be8fc'});

            });

            $("tr.clickablerow").each(function (index) {
                var row = $(this).closest("tr");
                row[0].addEventListener("click", function () {
                    var id = row.find(".id").text();
                    get_alarm_text(id, current_controller);
                });
            });

        },
        error: function (response) {
            alert("Error");
            console.log(response)
        }
    });
    return false;
};
