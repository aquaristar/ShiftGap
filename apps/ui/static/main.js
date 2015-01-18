// output helper function:
function out(s) { /*$("#output").append(s);*/ /* console.log(s); */ }

// Helper function, generating a time String of formar "HH:mm"
// from an input array `time` of two int elements: [hours, minutes]:
function hoursminsToString(time) {
    var h = time[0] + '';
    var m = time[1] + '';

    if (h.length == 1) { h = '0' + h; }
    if (m.length == 1) { m = '0' + m; }

    return h + ":" + m;
}

function isValidRangeFormat(t) {
    // Max parsable string length is 15 (example: "07:33am-10:27pm").
    // For longer strings, or those not starting with a digit
    // we return `undefined`:
    return ((typeof t == 'string' || t instanceof String) &&
            (t.length <= 15) &&
            t.match(/^[0-9]/) &&
            true
           );
}

/*
Parsing time from multiple input formats, such as:
"9",      "17",
"9a",     "5p",
"11am",   "1pm",
"9:45",   "13:45",
"9:45a",  "2p",
"1215",   "235",
"1030am", "4pm"

Strategy:
We want to convert every of those inputs into one specific format: "HHmm"

Step 1: ensure a colon (if present) is followed by two digits
Step 2: removing the colon
Step 3: Remove am/pm (but remember which it was) if possible
Step 4: We have now time strings such as:
        "9", "17", "1215", "235" or "1030"
        Two cases:
        a) string length is 1 or 2. In this case time means hours
        b) string length is 3 or 4.
           In this case we split by interpreting the two ending digits
           as minutes, and the one or two leading digit(s) as hour(s).
Step 5: convert 12:mm AM to 00:mm
*/
function parseTime(t) {
    var tmp;
    var hours;
    var minutes;
    var add12Hours = 0;  // 0 for am, 12 for pm
    var containsAMorPM = false;

    // Step 1:
    // if a colon is followed by just one digit we replace it with a zero
    // Example: "14:6" becomes => "1406"
    if (t.match(/:[0-9]([^0-9]|$)/)) t = t.replace(':', '0');

    // Step 2: removing the colon if possible:
    tmp = t.replace(':', '');

    // Step 3: remove am / pm if possible
    if (tmp.match(/am?$/i)) {
        add12Hours = 0;
        containsAMorPM = true;
        tmp = tmp.replace(/am?$/i, "");  // remove am from end
    }
    if (tmp.match(/pm?$/i)) {
        add12Hours = 12;
        containsAMorPM = true;
        tmp = tmp.replace(/pm?$/i, "");  // remove pm from end
    }

    // Step 4: split into hours and minutes
    if (tmp.length <= 2) {
        minutes = 0;
        hours = parseInt(tmp);
    } else {
        minutes = parseInt(tmp.slice(-2));
        if (tmp.length == 3) { hours = parseInt(tmp[0]); }
        if (tmp.length == 4) { hours = parseInt(tmp[0] + tmp[1]); }
    }

    // Step 5:
    // According to http://en.wikipedia.org/wiki/12-hour_clock
    // 12:xy AM means 00:xy in 24h format.
    // So hours needs to be resetted to zero before adding add12Hours:
    if ( containsAMorPM && (hours == 12) ) hours = 0;
    hours += add12Hours;

    return [hours, minutes];
}

// Splits time inputs at hyphen '-' into an array of parsed times.
function parseRange(r) {
    var tmp = r.split('-');
    var s = tmp[0];
    var e = tmp[1];

    return [parseTime(s), parseTime(e)];
}

function shorthand_to_datetimes(date, timeString) {
    if (!isValidRangeFormat(timeString)) {
        console.log("Format of »" + timeString + "« is not valid!");
        return;
    }
    var day = date.format('YYYY-MM-DD');
    var range = parseRange(timeString);

    try {
        var h1 = range[0][0]; // hours of start time
        var m1 = range[0][1]; // minutes of start time
        var s = moment(day + " " + hoursminsToString(range[0])).format();
    }
    catch(err) {
        console.log(err);
        return;
    }
    try {
        var h2 = range[1][0]; // hours of end time
        var m2 = range[1][1]; // minutes of end time

        // in case we have: 1215-235 we want to interpret
        // the `2` in `235` as 14 (12 hours later):
        if (h2 < h1) {
            h2 += 12;
            range[1][0] += 12;
        }

        if (h2 < h1) throw("end time must be AFTER start AND on same day");

        // Checking if any hour is >23 or minute >59:
        if ((h1 > 23) || (h2 > 23) || (m1 > 59) || (m2 > 59))
            throw("Invalid time: »" +
                  range[0] + "« or " +
                  range[1] + "«");

        if ((h1 == h2) && (m2 < m1)) throw("end time BEFORE start time");
        var e = moment(day + " " + hoursminsToString(range[1])).format();
    }
    catch(err) {
        console.log(err);
        return;
    }

    return [s, e];
}

function test(timeString) {
    var times = shorthand_to_datetimes(moment('2004-03-27'), timeString);

    if (typeof times == 'undefined') {
        out("<span style='color:red;'>Bad input: »" + timeString + "«</span>");
    } else {
        out("" + timeString + ' => ');
        out("from: <span style='color:green;'>" + times[0] + '</span> ');
        out("to: <span style='color:green;'>" + times[1] + '</span>');
    }

    out("<br /><br />");
}

// provided test cases:
// /*
test("9-17");       // -> output [date + "09:00:00", date + "17:00:00"]
test("9a-5p");      // -> output [date + "09:00:00", date + "17:00:00"]
test("11am-1pm");   // -> output [date + "11:00:00, date + "13:00:00"]
test("9:45-13:45"); // -> output [date + "09:45:00, date + "13:45:00"]
test("9:45a-2p");   // -> outout [date + "09:45:00, date + "14:00:00"]
test("1215-235");   // -> output [date + "12:15:00, date + "14:35:00"]
test("1030am-4pm"); // -> output [date + "10:30:00, date + "16:00:00]
test("hello");      // -> output -1
test("1030am-4");   // -> output -1  => Why? We can parse this! :-)
// */