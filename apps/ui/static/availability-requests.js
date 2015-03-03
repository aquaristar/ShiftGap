$(function () {
    "use strict";
    // Initialize all tabs

    $('#requests a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });

    $('#datetimepicker6').datetimepicker({
        viewMode: 'days',
        format: 'YYYY-MM-DD'
    });
    $('#datetimepicker7').datetimepicker({
        viewMode: 'days',
        format: 'YYYY-MM-DD'
    });
    $("#datetimepicker6").on("dp.change",function (e) {
        $('#datetimepicker7').data("DateTimePicker").minDate(e.date);
    });
    $("#datetimepicker7").on("dp.change",function (e) {
        $('#datetimepicker6').data("DateTimePicker").maxDate(e.date);
    });

    // Employee list with current user selected as default
    var sel = $('<select id="request-for-user" class="form-control">').appendTo('#textRequest');
    $(sg_users).each(function () {
        if (this.id == sg_user) {
            sel.append($('<option>').attr('value', this.id).attr('selected', 'selected').text(this.name));
        } else if (sg_admin_or_manager === "True") {
            // If the user is an admin or manager we also include the other employees
            sel.append($('<option>').attr('value', this.id).text(this.name));
        }
    });

    $("#submitRequest").click(function () {
        // post the request
        $.post(
            "submit_time_off_request/",
            {
                start_date: $('#datetime6text').val(),
                end_date: $('#datetime7text').val(),
                user: $('#request-for-user').val()
            },
            function (suc) {
                alert("success!");
            }
        );
        // clear the fields
        //$('#datetimepicker6').val();
        //$('#datetimepicker7').val();

        // show UX feedback
        alert('CLicked!');
    });
});

