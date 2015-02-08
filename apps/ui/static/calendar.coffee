root = exports ? this

(($) ->
) jQuery

engine = new Bloodhound
    name: 'employees'
    local: root.employees
    datumTokenizer: (d) ->
      return Bloodhound.tokenizers.whitespace(d.name)
    queryTokenizer: Bloodhound.tokenizers.whitespace

engine.initialize()

######################

poOpen = false

onHidePo = ->
  poOpen = false


onShowPo = ->
  if poOpen then return false else return true


onShownPo = ->
    # Popover HTML
    a = this.getAttribute("aria-describedby")
    employeeSelector = $("#"+a).children().find("#employeeSelector").typeahead
        highlight: true
        {
          name: 'employees'
          displayKey: 'name'
          source: engine.ttAdapter()
        }
    employeeSelector.on("typeahead:selected typeahead:autocompleted",
      (e, datum) ->
        $("#"+a).children().find("#employeeId").val(datum.id)
    )
    # FIXME: this gets called multiple times
#    $("#"+a).children().find("#timeText").on('keydown', (e) ->
#      if e.which == 13
#        e.preventDefault()
#        $("#"+a).children().find("#popover-save").trigger('click')
#    )
#      $("#saveQuickShift").trigger('click')
    if poOpen == false
      poOpen = true
      return true

root.closePopover = (x) ->
  po = $(x.parentNode.parentNode.parentNode)
  po.popover('hide')


shiftPublish = (shiftId, publish) ->
  pub = if publish then "True" else "False"
  $.ajax
    type: 'POST'
    url: root.shift_pubunpub_url
    data: {
      pk: shiftId
      pub: pub
    }
    dataType: 'json'
    success: ->
      undefined
  .fail (err) ->
    alert("Unable to change publication status of shift.")

root.publishShiftButton = ->
  shiftPublish(root.currentEvent.id, true)
  setTimeout ( ->
    $('#calendar').fullCalendar('refetchEvents')
  ), 200
  $('#shiftDetailModal').modal('hide')

root.unpublishShiftButton = ->
  shiftPublish(root.currentEvent.id, false)
  setTimeout ( ->
    $('#calendar').fullCalendar('refetchEvents')
  ), 200
  $('#shiftDetailModal').modal('hide')


deleteShift = (shiftId) ->
  $.ajax
    url: root.shift_delete_calendar_url
    type: "POST"
    data: {
      pk: shiftId
    }
    dataType: 'json'
    success: ->
      alert("Shift deleted")
      $("#calendar").fullCalendar("refetchEvents")
  .fail (err) ->
    alert("Shift deletion failed")

root.deleteShiftButton = ->
  deleteShift(root.currentEvent.id)
  $('#shiftDetailModal').modal('hide')


newShiftSave = (schedule, startTime, endTime, user) ->
  # POST request to create new shift
  $.ajax
    type: "POST"
    url: root.list_create_api_url
    data: {
      schedule: schedule
      start_time: startTime
      end_time: endTime
      user: user
    }
    success: ->
      $('#calendar').fullCalendar('refetchEvents')
    dataType: 'json'
  .fail (err) ->
    alert("Error saving new shift")
    console.log(err)

root.newShift = (x) ->
  po = $(x.parentNode.parentNode.parentNode)
  time_text = po.children().find('#timeText').val()
  times = shorthand_to_datetimes(root.dayCreate, time_text)
  start_time = times[0]
  end_time = times[1]
  user = po.children().find("#employeeId").val()
  schedule = root.default_schedule
  newShiftSave(schedule, start_time, end_time, user)
  po.popover('hide')


# READY ----------------------------------------------
$ ->

  $("#calendar").fullCalendar
    dayClick: (date, jsEvent, view) ->
      if root.admin_or_manager
        offset = new Date().getTimezoneOffset();
        date = date.zone(-offset);
        dateString = date._d.toString().slice(0,15);
        #
        po = $(this).popover
          html: true
          title: "Add a new shift"
          content: -> $("#popover-content").html()
          placement: 'bottom'
          container: 'body'
        root.dayCreate = date
        root.po = po

        po.on('show.bs.popover', onShowPo)
        po.on('shown.bs.popover', onShownPo)
        po.on('hidden.bs.popover', onHidePo)
    eventClick: (calEvent, jsEvent, view) ->
      if root.admin_or_manager
        $("#shiftDetailModal").modal('show')
        $('#shiftDetailModalContent').append("<h2 id=\"h2usertitle\">User: " + calEvent.title + "</h2>" +
                      "<br /><br /><h3>" + calEvent.start.format('h:mm a') + " -- " + calEvent.end.format('h:mm a') + "</h3>")
        root.currentEvent = calEvent
    eventSources: [ root.source, root.source_unpublished ]
    displayEventEnd: true
    header:
      left: 'title'
      center: ''
      right: 'today agendaWeek month prev, next'


  $('#shiftDetailModalContent').on('click', '#h2usertitle',
    ->
      $(this).slideUp()
      $('#shiftDetailModalContent').append("<p><label for=\"employeeSelector\">Employee:</label> " +
                    "<input id=\"employeeSelector\" type=\"text\" name=\"employee\" placeholder=\"Start typing first name\">" +
                    "<input type=\"hidden\" id=\"employeeId\"> " +
                    " </p>" +
                    "<button id=\"saveNewDetails\" class=\"btn btn-lg btn-primary\">Save Changes</button>");
      $('#employeeSelector').typeahead({
                                highlight: true
                            },
                            {
                                name: 'employees',
                                displayKey: 'name',
                                source: engine.ttAdapter()
                            })
      $("#employeeSelector").on("typeahead:selected typeahead:autocompleted",
                            (e,datum) ->
                                $('#employeeId').val(datum.id)
                            )
      $('#employeeSelector').focus()
  )

  # Pressing Save at the Shift Detail Modal
  $("#saveShiftDetail").click ->
    if root.admin_or_manager then $('#saveNewDetails').trigger('click') else $('#shiftDetailModal').modal('hide')

  $('#shiftDetailModal').on('hide.bs.modal', (e) ->
            $('#employeeSelector').val('')
            $('#employeeId').val('')
            $('#shiftDetailModalContent').empty()
        )
  $("#employeeSelector").on("typeahead:selected typeahead:autocompleted",
                (e,datum) ->
                    $('#employeeId').val(datum.id)
                )

  ############################################ Toggle between 'just me' and everyone options
  $('#checkMe').change ->
    if this.checked
      # uncheck everyone
      $('#checkEveryone').attr('checked', false)
      # add source for just me
      $('#calendar').fullCalendar('addEventSource', root.source_filtered)
      $('#calendar').fullCalendar('removeEventSource', root.source)
      $('#calendar').fullCalendar('removeEventSource', root.source_unpublished)

  $('#checkEveryone').change ->
    if this.checked
      # uncheck me
      $('#checkMe').attr('checked', false)
      # add regular source back
      $('#calendar').fullCalendar('addEventSource', root.source)
      $('#calendar').fullCalendar('addEventSource', root.source_unpublished)
      $('#calendar').fullCalendar('removeEventSource', root.source_filtered)

  # end of ready