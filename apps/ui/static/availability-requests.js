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
                user: $('#request-for-user').val(),
                note: $('#requestNote').val()
            },
            function (suc) {
                alert("Your request for time off has been recorded!");
                $('#datetime6text').val('');
                $('#datetime7text').val('');
                $('#requestNote').val('');
            }
        ).fail(function (err) {
                alert("Could not complete request: " + err.responseJSON.result);
            });
        // clear the fields

        //$('#datetimepicker7').val();

        // show UX feedback
        alert('CLicked!');
    });

});

function sg_cancelTimeOffRequest(pk) {
    $.post(
        "cancel_time_off_request/",
        {
            request_pk: pk
        },
        function (suc) {
            alert("Time off request has been cancelled.");
        }
    ).fail(function (err) {
            alert("Could not cancel time off request. Please contact support for assistance.")
        });
}

function sg_rejectTimeOffRequest(pk) {
    $.post(
        "reject_time_off_request/",
        {
            request_pk: pk
        },
        function (suc) {
            alert("Time off request has been rejected.");
        }
    ).fail(function (err) {
            alert("Could not reject time off request. Please contact support for assistance.")
        });
}

function sg_approveTimeOffRequest(pk) {
    $.post(
        "approve_time_off_request/",
        {
            request_pk: pk
        },
        function (suc) {
            alert("Time off request has been approved.");
        }
    ).fail(function (err) {
            alert("Could not approve time off request. Please contact support for assistance.")
        });
}