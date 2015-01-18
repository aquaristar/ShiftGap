// Custom javascript here
function human_to_computer_time(date, timeString) {
    // takes user input and returns a list of moment objects representing start and end

    //input 9-17 -> output [date + "09:00:00", date + "17:00:00"]
    //input 9a-5p -> output [date + "09:00:00", date + "17:00:00"]
    //input 11am-1pm -> output [date + "11:00:00, date + "13:00:00"]
    //input 9:45-13:45 -> output [date + "09:45:00, date + "13:45:00"]
    //input 9:45a-2p -> outout [date + "09:45:00, date + "14:00:00"]
    //input 1215-235 -> output [date + "12:15:00, date + "14:35:00"]
    //input 1030am-4pm -> output [date + "10:30:00, date + "16:00:00]


    // first strip any spaces and make it lowercase
    var time = timeString.replace(' ', '');
    time = time.toLowerCase();
    var times = time.split(('-'));
    console.log(times);
    if (times.length > 2 || times.length < 2) {
        return -1;
    }
    // FIXME code the rest here
    var dateString = date.toJSON();
    var dateOnly = dateString.split('T')[0];
    console.log('dateOnly', dateOnly);
    var createRange = [];
    createRange.push();

    return createRange;
}