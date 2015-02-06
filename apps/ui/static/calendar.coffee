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
#    $("#"+a).children().find("#timeText").keypress((e) ->
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

$ ->

  $("#calendar").fullCalendar
    dayClick: (date, jsEvent, view) ->
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

