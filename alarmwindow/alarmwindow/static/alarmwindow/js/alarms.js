function timeToString(dt) {
    if (dt == null)
        return "";
    return dt.replace("-", ".")
        .replace("-", ".")
        .replace("T", " ")
        .replace("Z", " ");
}

function updateAlarms(node_id) {
    $.ajax({
        type: $(this).attr('GET'),
        url: alarm_template,
        data: {id: node_id},
        success: function (response) {
            $("#alarm_table tbody").html("");
            $.each(response["alarms"], function (index, item) {
                // language=HTML
                $("#alarm_table tbody").prepend(
                    `
                        <tr class="clickablerow">
                            <td class="coloredrow">${item["type"]}</td>
                            <td>${item["id"]}</td>
                            <td>${timeToString(item["raising_time"])}</td>
                            <td>${timeToString(item["ceasing_time"])}</td>
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
                    alert(row.find(".coloredrow").text());
                    $(this).css({background: 'green'});
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
$(document).ready(updateAlarms());
$('#alarm_table td').dblclick(function () {
    //var id = $(this).attr('id');
    alert("+1");
    //alert($(this).attr('Name'));
})