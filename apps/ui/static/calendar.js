// Generated by CoffeeScript 1.9.0
(function() {
  var deleteShift, engine, newShiftSave, onHidePo, onShowPo, onShownPo, poOpen, root, shiftPublish;

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  (function($) {})(jQuery);

  engine = new Bloodhound({
    name: 'employees',
    local: root.employees,
    datumTokenizer: function(d) {
      return Bloodhound.tokenizers.whitespace(d.name);
    },
    queryTokenizer: Bloodhound.tokenizers.whitespace
  });

  engine.initialize();

  poOpen = false;

  onHidePo = function() {
    return poOpen = false;
  };

  onShowPo = function() {
    if (poOpen) {
      return false;
    } else {
      return true;
    }
  };

  onShownPo = function() {
    var a, employeeSelector;
    a = this.getAttribute("aria-describedby");
    employeeSelector = $("#" + a).children().find("#employeeSelector").typeahead({
      highlight: true
    }, {
      name: 'employees',
      displayKey: 'name',
      source: engine.ttAdapter()
    });
    employeeSelector.on("typeahead:selected typeahead:autocompleted", function(e, datum) {
      return $("#" + a).children().find("#employeeId").val(datum.id);
    });
    if (poOpen === false) {
      poOpen = true;
      return true;
    }
  };

  root.closePopover = function(x) {
    var po;
    po = $(x.parentNode.parentNode.parentNode);
    return po.popover('hide');
  };

  shiftPublish = function(shiftId, publish) {
    var pub;
    pub = publish ? "True" : "False";
    return $.ajax({
      type: 'POST',
      url: root.shift_pubunpub_url,
      data: {
        pk: shiftId,
        pub: pub
      },
      dataType: 'json',
      success: function() {
        return void 0;
      }
    }).fail(function(err) {
      return alert("Unable to change publication status of shift.");
    });
  };

  root.publishShiftButton = function() {
    shiftPublish(root.currentEvent.id, true);
    setTimeout((function() {
      return $('#calendar').fullCalendar('refetchEvents');
    }), 200);
    return $('#shiftDetailModal').modal('hide');
  };

  root.unpublishShiftButton = function() {
    shiftPublish(root.currentEvent.id, false);
    setTimeout((function() {
      return $('#calendar').fullCalendar('refetchEvents');
    }), 200);
    return $('#shiftDetailModal').modal('hide');
  };

  deleteShift = function(shiftId) {
    return $.ajax({
      url: root.shift_delete_calendar_url,
      type: "POST",
      data: {
        pk: shiftId
      },
      dataType: 'json',
      success: function() {
        alert("Shift deleted");
        return $("#calendar").fullCalendar("refetchEvents");
      }
    }).fail(function(err) {
      return alert("Shift deletion failed");
    });
  };

  root.deleteShiftButton = function() {
    deleteShift(root.currentEvent.id);
    return $('#shiftDetailModal').modal('hide');
  };

  newShiftSave = function(schedule, startTime, endTime, user) {
    return $.ajax({
      type: "POST",
      url: root.list_create_api_url,
      data: {
        schedule: schedule,
        start_time: startTime,
        end_time: endTime,
        user: user
      },
      success: function() {
        return $('#calendar').fullCalendar('refetchEvents');
      },
      dataType: 'json'
    }).fail(function(err) {
      alert("Error saving new shift");
      return console.log(err);
    });
  };

  root.newShift = function(x) {
    var end_time, po, schedule, start_time, time_text, times, user;
    po = $(x.parentNode.parentNode.parentNode);
    time_text = po.children().find('#timeText').val();
    times = shorthand_to_datetimes(root.dayCreate, time_text);
    start_time = times[0];
    end_time = times[1];
    user = po.children().find("#employeeId").val();
    schedule = root.default_schedule;
    newShiftSave(schedule, start_time, end_time, user);
    return po.popover('hide');
  };

  $(function() {
    $("#calendar").fullCalendar({
      dayClick: function(date, jsEvent, view) {
        var dateString, offset, po;
        if (root.admin_or_manager) {
          offset = new Date().getTimezoneOffset();
          date = date.zone(-offset);
          dateString = date._d.toString().slice(0, 15);
          po = $(this).popover({
            html: true,
            title: "Add a new shift",
            content: function() {
              return $("#popover-content").html();
            },
            placement: 'bottom',
            container: 'body'
          });
          root.dayCreate = date;
          root.po = po;
          po.on('show.bs.popover', onShowPo);
          po.on('shown.bs.popover', onShownPo);
          return po.on('hidden.bs.popover', onHidePo);
        }
      },
      eventClick: function(calEvent, jsEvent, view) {
        if (root.admin_or_manager) {
          $("#shiftDetailModal").modal('show');
          $('#shiftDetailModalContent').append("<h2 id=\"h2usertitle\">User: " + calEvent.title + "</h2>" + "<br /><br /><h3>" + calEvent.start.format('h:mm a') + " -- " + calEvent.end.format('h:mm a') + "</h3>");
          return root.currentEvent = calEvent;
        }
      },
      eventSources: [root.source, root.source_unpublished],
      displayEventEnd: true,
      header: {
        left: 'title',
        center: '',
        right: 'today agendaWeek month prev, next'
      }
    });
    $('#shiftDetailModalContent').on('click', '#h2usertitle', function() {
      $(this).slideUp();
      $('#shiftDetailModalContent').append("<p><label for=\"employeeSelector\">Employee:</label> " + "<input id=\"employeeSelector\" type=\"text\" name=\"employee\" placeholder=\"Start typing first name\">" + "<input type=\"hidden\" id=\"employeeId\"> " + " </p>" + "<button id=\"saveNewDetails\" class=\"btn btn-lg btn-primary\">Save Changes</button>");
      $('#employeeSelector').typeahead({
        highlight: true
      }, {
        name: 'employees',
        displayKey: 'name',
        source: engine.ttAdapter()
      });
      $("#employeeSelector").on("typeahead:selected typeahead:autocompleted", function(e, datum) {
        return $('#employeeId').val(datum.id);
      });
      return $('#employeeSelector').focus();
    });
    $("#saveShiftDetail").click(function() {
      if (root.admin_or_manager) {
        return $('#saveNewDetails').trigger('click');
      } else {
        return $('#shiftDetailModal').modal('hide');
      }
    });
    $('#shiftDetailModal').on('hide.bs.modal', function(e) {
      $('#employeeSelector').val('');
      $('#employeeId').val('');
      return $('#shiftDetailModalContent').empty();
    });
    $("#employeeSelector").on("typeahead:selected typeahead:autocompleted", function(e, datum) {
      return $('#employeeId').val(datum.id);
    });
    $('#checkMe').change(function() {
      if (this.checked) {
        $('#checkEveryone').attr('checked', false);
        $('#calendar').fullCalendar('addEventSource', root.source_filtered);
        $('#calendar').fullCalendar('removeEventSource', root.source);
        return $('#calendar').fullCalendar('removeEventSource', root.source_unpublished);
      }
    });
    return $('#checkEveryone').change(function() {
      if (this.checked) {
        $('#checkMe').attr('checked', false);
        $('#calendar').fullCalendar('addEventSource', root.source);
        $('#calendar').fullCalendar('addEventSource', root.source_unpublished);
        return $('#calendar').fullCalendar('removeEventSource', root.source_filtered);
      }
    });
  });

}).call(this);

//# sourceMappingURL=calendar.js.map