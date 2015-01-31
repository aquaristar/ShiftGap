
n.n.n / 2015-01-30
==================

  * change user from shift detail modal
  * newrelic version
  * update djangorestframework and django-rest-auth
  * need to filter by user for myshifts
  * custom Shifts manager base implementation
  * request.user is a simplelazyobject until used
  * bump to django 1.7.4
  * show upcoming shifts on welcome screen
  * greet user by first name not username
  * updated templates for end user use
  * removed bad import
  * reply with next shift to 'next' and next two shifts to 'next2'
  * next should only give us shifts in the future
  * return next shift when user txts 'next' to sms endpoint
  * basic shift view tests, need to add more
  * handle dates across days with min and max set by variable
  * publish unpublish single shifts fixes #23 SG-19
  * publish and unpublish by range
  * how to enter shift information
  * only manager or admin can add shifts
  * updated date parsing js
  * comment out incorrect view
  * updated security settings
  * nope
  * some test code for heroku
  * basic shift publish functionality
  * enable worker in procfile
  * basic phone number validation per E.164 international standards
  * load font over ssl if required
  * respond appropriate to START, YES, STOP and UNSUBSCRIBE messages from our twilio endpoint
  * confirm users phone number and edit profile from user list page
  * update arrow, placeholder tasks for shift saving
  * additional test cases for shift input to allow for shifts that span more than a day
  * autocomplete shift add uses user firstname + last initial unless no first name set then we default to username
  * support for whitespace and 'to' instead of '-' in user shift input
  * more exact datetimes in text reminders
  * reminders 24 hours and 90 minutes before the start of shifts if user has a confirmed phone #
