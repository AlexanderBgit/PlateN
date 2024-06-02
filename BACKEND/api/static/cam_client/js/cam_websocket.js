const IMAGE_INTERVAL_MS = 90;
let isStreaming = false; // Flag to track streaming state

function getWebSocketUrl(path = '') {
  const currentUrl = new URL(window.location.href);

  // Ensure protocol is 'ws:' (unencrypted)
  if (currentUrl.protocol == "https:"){
     currentUrl.protocol = 'wss:';
  }else{
     currentUrl.protocol = 'ws:';
  }
  // Append the path if provided
  if (path) {
    currentUrl.pathname = path.trim(); // Trim leading/trailing slashes
  }

  return currentUrl.toString();
}

function debug(msg, level="danger"){
  const debug_div = document.getElementById('debug');
  if (debug_div) {
    debug_div.className = "";
    debug_div.classList.add("alert");
    debug_div.classList.add("alert-"+level);
    debug_div.innerText = msg;
  }
}

function info(msg, level="info"){
  const info_div = document.getElementById('info');
  if (info_div) {
//    info_div.className = "";
//    info_div.classList.add("alert");
//    info_div.classList.add("alert-"+level);
    info_div.innerText = msg;
  }
}

function info_toggle(){
  const info_div = document.getElementById('info');
  info_div.classList.toggle("d-none");
  info_div.innerText = "";
}


const startFaceDetection = (video, canvas, deviceId) => {
  if (!WS_URL) {
     console.error("WS_URL:", WS_URL)
     return;
  }
  const ws_connect=getWebSocketUrl(WS_URL)
  console.log("ws_connect:", ws_connect)
  try {
    info_toggle();
    const socket = new WebSocket(ws_connect);
    socket.onopen = () => {
      msg = 'WebSocket connection opened!'
      console.log(msg);
      debug(msg, "info")
    };
    socket.onerror = (error) => {
      const msg = "WebSocket connection error. "+ws_connect;
      debug(msg)
    };
    let intervalId;
    let interval_measure;
    let is_answered = true;
    let skipped_frames = 0;
    let sent_frames = 0;
    let adaptive_interval_ms = 0;
    let average_duration = 0;
    let average_duration_calc = 0;
    let avg_duration_calc = 0;
    let max_queue=0;
    // Connection opened
    socket.addEventListener('open', function () {
      // Start reading video from device
      navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
          deviceId,
          width: { max: 640 },
          height: { max: 480 },
        },
      }).then(function (stream) {
        video.srcObject = stream;
        video.play().then(() => {
          // Adapt overlay canvas size to the video size
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          isStreaming = true;

          // Send an image in the WebSocket every 42 ms
          intervalId = setInterval(() => {
            if (!is_answered) {
              skipped_frames += 1;
              const sk_perc = (skipped_frames/sent_frames*100).toFixed(2);
              const currentTime = new Date().toLocaleTimeString();
              debug(`At ${currentTime}: skipped for the sending frame, not received in time. Total frames was skipped: ${skipped_frames} (${sk_perc}%)`, "info");
              return;
            }
            // On canvas to draw current video image
            if (!canvas) {
               console.error("No Canvas...")
               return;
            }
            const canvas_video_snap = document.createElement('canvas');
            const ctx = canvas_video_snap.getContext('2d');
            canvas_video_snap.width = video.videoWidth;
            canvas_video_snap.height = video.videoHeight;
            ctx.drawImage(video, 0, 0);
            // Convert it to JPEG and send it to the WebSocket
            interval_measure = performance.now();
            is_answered = false;
            canvas_video_snap.toBlob((blob) => socket.send(blob), 'image/jpeg');
            sent_frames += 1;
          }, IMAGE_INTERVAL_MS);
        });
      });
    });
    // Listen for messages
    socket.addEventListener('message', function (event) {
      is_answered = true;
      const duration = Math.round(performance.now() - interval_measure);
      average_duration += duration;
      message_data = JSON.parse(event.data)
      average_duration_calc += message_data?.duration_ms;
      if (sent_frames % 50 == 0){
         if (average_duration > 0) {
            adaptive_interval_ms = Math.round(average_duration/50.0);
            average_duration = 0;
         }
         if (average_duration_calc > 0) {
            avg_duration_calc = Math.round(average_duration_calc/50.0);
            average_duration_calc = 0;
         }
      }
      if (draw_detected) draw_detected(video, canvas, message_data);
      max_queue = Math.max(message_data.queue_id, max_queue);
      info(`Queue: ${message_data?.queue_id}(max:${max_queue}). Sending interval: ${IMAGE_INTERVAL_MS} ms, Answer time: ${duration} (avr: ${adaptive_interval_ms}) ms. Calculate duration: ${message_data?.duration_ms} (avg:${avg_duration_calc}) ms.`)
    });
    // Stop the interval and video reading on close
    socket.addEventListener('close', function () {
      window.clearInterval(intervalId);
      video.pause();
    });
    return socket;
  } catch (error) {
      if (error instanceof SyntaxError) {
        debug('Invalid WebSocket URL format:' + error.message);
        console.error('Invalid WebSocket URL format:', error.message);
      } else {
        debug('WebSocket connection error:' + error.message);
        console.error('WebSocket connection error:', error);
      }
  }
};

// Function to stop the video stream and turn off the LED (if possible)
const stopFaceDetection = (video, canvas) => {
  if (1) {
    if (canvas){
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    const mediaStream = video.srcObject;
    if (mediaStream) {
      const tracks = mediaStream.getTracks();
      tracks.forEach(function (track) {
        track.stop(); // Stop individual media track
      });
      video.srcObject = null; // Clear video source
      isStreaming = false;
//      console.log("Video stream stopped");
      setTimeout(() => {debug("Video stream stopped","info")},2000);
    }
    info_toggle();
  } else {
    console.log("Video stream already stopped");
  }
}

const cam_detect = (cameraSelect) => {
   navigator.mediaDevices.getUserMedia({ audio: false, video: true })
    .then((stream) => {
      // stop LED use.
      stream.getTracks().forEach(track => track.stop());
      navigator.mediaDevices.enumerateDevices()
      .then((devices) => {
        // Check for available cameras
        // console.log('Check for available cameras',devices);
        if (!devices.some((device) => device.kind === 'videoinput')) {
          const noCameraOption = document.createElement('option');
          noCameraOption.value = ''; // Set an empty value to avoid potential selection issues
          noCameraOption.innerText = 'No cameras detected';
          console.log('No cameras detected', noCameraOption.innerText)
          cameraSelect.appendChild(noCameraOption);
          return; // Exit if no cameras are found
        }

        // Filter and populate options
        for (const device of devices) {
          if (device.kind === 'videoinput') {
            const deviceOption = document.createElement('option');
            if (device.deviceId) {
              deviceOption.value = device.deviceId;
              deviceOption.innerText = device.label || `Camera ${devices.indexOf(device) + 1}`; // Use label or fallback
              console.log('cameras detected');
              cameraSelect.appendChild(deviceOption);
            } else {
              console.log('cameras detected but empty')
              deviceOption.value = "";
              deviceOption.innerText = 'WARNING: Cameras detected but with empty names';
              cameraSelect.appendChild(deviceOption);
            }
          }
        }
      })
      .catch((error) => {
        console.error('Error listing cameras:', error);
        // Handle errors gracefully (e.g., display an error message to the user)
      });
    })
    .catch((err) => {
          const noCameraOption = document.createElement('option');
          noCameraOption.value = ''; // Set an empty value to avoid potential selection issues
          noCameraOption.innerText = 'No cameras detected. Permission required.';
          console.error('No cameras detected', err)
          cameraSelect.appendChild(noCameraOption);
    });
  };



// DOMContentLoaded
window.addEventListener('DOMContentLoaded', (event) => {
  const video = document.getElementById('video');
  const canvas = document.getElementById('canvas');
  const cameraSelect = document.getElementById('camera-select');
  let socket;
  cam_detect(cameraSelect);
  const button_start = document.getElementById("button-start");
  const button_stop = document.getElementById("button-stop");
  if (button_stop){
    button_stop.addEventListener('click', (event) => {
      event.preventDefault();
      // Close the WebSocket connection (if it exists)
      if (socket) {
        stopFaceDetection(video, canvas);
        socket.close();
        setTimeout(() => {debug("WebSocket connection closed","info")},600);
        socket = null; // Clear the socket reference
      } else {
        console.log("No WebSocket connection to close");
      }
      if (button_stop){
        button_start.classList.toggle("d-none");
      }
      if (button_stop){
        button_stop.classList.toggle("d-none");
      }
    });
   };

  // Start face detection on the selected camera on submit
  document.getElementById('form-connect')?.addEventListener('submit', (event) => {
    event.preventDefault();

    // Close previous socket is there is one
    if (socket) {
      socket.close();
    }

    const deviceId = cameraSelect.selectedOptions[0]?.value;
    if (deviceId){
      socket = startFaceDetection(video, canvas, deviceId);
      if (socket) {
        if (button_start){
         button_start.classList.toggle("d-none");
        }
        if (button_stop){
          button_stop.classList.toggle("d-none");
        }
      }
    }else{
      debug("Not detected device ID");
    }
  });

});
// DOMContentLoaded