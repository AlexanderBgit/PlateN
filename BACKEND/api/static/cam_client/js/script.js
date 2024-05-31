const IMAGE_INTERVAL_MS = 500;

function getWebSocketUrl(path = '') {
  const currentUrl = new URL(window.location.href);

  // Ensure protocol is 'ws:' (unencrypted)
  currentUrl.protocol = 'ws:';

  // Append the path if provided
  if (path) {
    currentUrl.pathname = path.trim(); // Trim leading/trailing slashes
  }

  return currentUrl.toString();
}


function debug(msg, level="danger"){
  const debug = document.getElementById('debug');
  if (debug) {
    debug.className = "";
    debug.classList.add("alert");
    debug.classList.add("alert-"+level);
    debug.innerText = msg;
  }
}

const drawFaceRectangles = (video, canvas, faces) => {
  const ctx = canvas.getContext('2d');

  ctx.width = video.videoWidth;
  ctx.height = video.videoHeight;

  ctx.beginPath();
  ctx.clearRect(0, 0, ctx.width, ctx.height);
  for (const [x, y, width, height] of faces.faces) {
    ctx.strokeStyle = "#49fb35";
    ctx.beginPath();
    ctx.rect(x, y, width, height);
    ctx.stroke();
  }
};

const startFaceDetection = (video, canvas, deviceId) => {
  console.log("WS_URL:", WS_URL)
  if (!WS_URL) return;
  ws_connect=getWebSocketUrl(WS_URL)
  console.log("ws_connect:", ws_connect)
  try {
    const socket = new WebSocket(ws_connect);
    socket.onopen = () => {
      msg = 'WebSocket connection opened!'
      console.log(msg);
      debug(msg, "info")
    };
    socket.onerror = (error) => {
      msg = "WebSocket connection error. "+ws_connect;
      debug(msg, "warning")
//      console.error('WebSocket connection error:', error);
    };

    let intervalId;
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

          // Send an image in the WebSocket every 42 ms
          intervalId = setInterval(() => {

            // Create a virtual canvas to draw current video image
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0);

            // Convert it to JPEG and send it to the WebSocket
            canvas.toBlob((blob) => socket.send(blob), 'image/jpeg');
          }, IMAGE_INTERVAL_MS);
        });
      });
    });

    // Listen for messages
    socket.addEventListener('message', function (event) {
      drawFaceRectangles(video, canvas, JSON.parse(event.data));
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

window.addEventListener('DOMContentLoaded', (event) => {
  const video = document.getElementById('video');
  const canvas = document.getElementById('canvas');
  const cameraSelect = document.getElementById('camera-select');
  let socket;


navigator.mediaDevices.getUserMedia({ audio: false, video: true })
    .then((stream) => {
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


  const button_stop = document.getElementById("button-stop");
  const button_start = document.getElementById("button-start");
  if (button_stop){
    button_stop.addEventListener('click', (event) => {
      event.preventDefault();
      button_start.classList.toggle("d-none");
      if (button_stop){
        button_stop.classList.toggle("d-none");
      }
    });
   };

  // Start face detection on the selected camera on submit
  document.getElementById('form-connect').addEventListener('submit', (event) => {
    event.preventDefault();

    // Close previous socket is there is one
    if (socket) {
      socket.close();
    }

    const deviceId = cameraSelect.selectedOptions[0]?.value;
    if (deviceId){
      socket = startFaceDetection(video, canvas, deviceId);
    }else{
      debug("Not detected device ID");
    }
  });

});