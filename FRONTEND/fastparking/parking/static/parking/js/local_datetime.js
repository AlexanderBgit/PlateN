const regexPattern_datetime = /^(.*)(\d{4}-\d{2}-\d{2} \d{2}:\d{2}(?::\d{2})?)(.*)$/;

function parse_utc_string(datetimeString) {
  // Example datetime string in "yyyy-mm-dd hh:mm:ss" format
  const parts = datetimeString.split(/[- :]/);
  const year = parseInt(parts[0]);
  const month = parseInt(parts[1]) - 1; // Month is zero-indexed
  const day = parseInt(parts[2]);
  const hour = parseInt(parts[3]);
  const minute = parseInt(parts[4]);
  const second = parts[5] ? parseInt(parts[5]) : 0;
  return Date.UTC(year, month, day, hour, minute, second);
}

function get_client_tz_offset() {
  const date = new Date();
  const offset = date.getTimezoneOffset(); // * 60 * 1000; // Convert minutes offset to milliseconds
  return offset;
}

function format_datetime_to_local(datetime, show_seconds = false) {
  if (datetime) {
    const options = {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    };
    if (show_seconds) {
      options.second = "2-digit";
    }
    const formatter = new Intl.DateTimeFormat([], options);
    return formatter.format(datetime);
  }
  return datetime;
}

function formatDateInString(originalString) {
  const match = originalString.match(regexPattern_datetime);
  if (match) {
    const text_start_Part = match ? match[1] : null;
    const dateTimePart = match ? match[2] : null;
    const text_end_Part = match ? match[3] : null;

    const parsedDateTime = dateTimePart ? new Date(dateTimePart + "Z") : null;
    const formattedDateTime = format_datetime_to_local(parsedDateTime);
    const newString = formattedDateTime ? text_start_Part + formattedDateTime + text_end_Part : originalString;
    return newString;
  }
  return originalString;
}

function parse_datetime_utc() {
  const cells = document.querySelectorAll(".datetime_utc");
  cells.forEach((cell) => {
    const datetimeString = cell.innerText;
    if (datetimeString) {
      cell.innerText = formatDateInString(datetimeString);
    }
  });
}

function parse_datetime_utc_title() {
  const cells = document.querySelectorAll(".datetime_utc_title");
  cells.forEach((cell) => {
    const datetimeString = cell.title;
    if (datetimeString) {
      cell.title = formatDateInString(datetimeString);
    }
  });
}


//document.addEventListener("DOMContentLoaded", parse_datetime_utc);
