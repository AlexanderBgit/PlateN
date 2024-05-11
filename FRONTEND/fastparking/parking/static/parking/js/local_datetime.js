function parse_utc_string(datetimeString){
    // Example datetime string in "yyyy-mm-dd hh:mm:ss" format
    const parts = datetimeString.split(/[- :]/);
    const year = parseInt(parts[0]);
    const month = parseInt(parts[1]) - 1; // Month is zero-indexed
    const day = parseInt(parts[2]);
    const hour = parseInt(parts[3]);
    const minute = parseInt(parts[4]);
    const second = parseInt(parts[5]);
    return Date.UTC(year, month, day, hour, minute, second);
}

function get_client_tz_offset(){
    const date = new Date();
    const offset = date.getTimezoneOffset();// * 60 * 1000; // Convert minutes offset to milliseconds
    return offset
}

function parse_datetime_utc(){
    // Get all table cells with class name "dateutc"
    const cells = document.querySelectorAll('.datetime_utc');

    // Loop through each cell and convert the datetime to the client's timezone
    cells.forEach(function(cell) {
        // Parse the datetime string from the cell
        const datetimeString = cell.innerText;
        if (datetimeString) {
            const datetime = new Date(datetimeString+"Z");
            // Convert the datetime to the client's timezone
//            const clientTimeZoneDatetime = datetime.toLocaleString(undefined, {
//                year: 'numeric',
//                month: '2-digit',
//                day: '2-digit',
//                hour: 'numeric',
//                minute: 'numeric',
//                timeZoneName: 'short'
//            });

            const formatter = new Intl.DateTimeFormat([], {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
    //            timeZoneName: 'short'
            });

            const formattedDate = formatter.format(datetime);
            // Update the cell with the datetime in the client's timezone
    //        cell.innerText = clientTimeZoneDatetime;
            cell.innerText = formattedDate;
        }
    });
}
document.addEventListener("DOMContentLoaded", parse_datetime_utc)
