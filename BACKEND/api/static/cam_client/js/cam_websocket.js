const IMAGE_INTERVAL_MS = 250;
const SNAP_IMAGE_SCALE = CAM_DOWNSCALE ? CAM_DOWNSCALE : 4; // down scale for sending image to api server
let cam_size_array = undefined;
if (CAM_SIZE) {
  cam_size_array = JSON.parse(CAM_SIZE);
}
const MAX_CAM_SIZE = {
  width: cam_size_array ? cam_size_array[0] : 1280,
  height: cam_size_array ? cam_size_array[1] : 720,
};
const ADAPTIVE_FACTOR = 1.15;
const COMMAND_SIZE = 4;
const cam_control = {};
const CAM_COMMANDS = {
  default: 0,
  snap: 1,
};

let isStreaming = false; // Flag to track streaming state
let button_stop;
let button_snap;
let button_start;
let intervalId;
let canvas_video_snap;
let canvas_video;
let canvas_zoom;
let cameraSelect;
let ctx_zoom;
let zoomFactor = 2;
let video;
let canvas;
let socket;
let controls;

function packMessage_0(imageData, commandId = 0) {
  const totalSize = COMMAND_SIZE + imageData.size;
  if (!COMMAND_SIZE) return imageData;
  // Create the buffer and view
  const buffer = new ArrayBuffer(totalSize);
  const dataView = new DataView(buffer);

  // Write command ID (assuming 32-bit integer)
  dataView.setUint32(0, commandId, true); // Little-endian

  // Copy image data into the buffer
  const uint8Array = new Uint8Array(buffer, COMMAND_SIZE, imageData.length);
  uint8Array.set(imageData);

  return buffer;
}

function packMessage(commandId, binaryData) {
  if (!(binaryData instanceof Blob)) {
    throw new Error("binaryData must be a Blob. Type: " + typeof binaryData);
  }
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = function (event) {
      const arrayBuffer = event.target.result;
      const binaryArray = new Uint8Array(arrayBuffer);
      const encoder = new TextEncoder();
      const fileType = binaryData.type.split("/")[1];
      const header = `${fileType},${commandId}`;
      const headerBytes = encoder.encode(header);
      const headerLength = headerBytes.length;
      // Total size: 1 byte for header length + header + binary data
      const totalSize = 1 + headerLength + binaryArray.length;
      const buffer = new ArrayBuffer(totalSize);
      const dataView = new DataView(buffer);
      // Write the header length (1 byte)
      dataView.setUint8(0, headerLength);
      // Write the header
      new Uint8Array(buffer, 1, headerLength).set(headerBytes);
      // Write the binary data
      new Uint8Array(buffer, 1 + headerLength, binaryArray.length).set(binaryArray);
      resolve(buffer);
    };
    reader.onerror = function (event) {
      reject(new Error("Error reading the Blob: " + event.target.error));
    };
    reader.readAsArrayBuffer(binaryData);
  });
}

async function sendPackedMessage(socket, commandId, blob) {
  try {
    const packedData = await packMessage(commandId, blob);
    socket.send(packedData);
    //    console.log("Packed message sent over WebSocket");
  } catch (error) {
    console.error("Error packing or sending message:", error);
  }
}

function getWebSocketUrl(path = "") {
  const currentUrl = new URL(window.location.href);

  // Ensure protocol is 'ws:' (unencrypted)
  if (currentUrl.protocol == "https:") {
    currentUrl.protocol = "wss:";
  } else {
    currentUrl.protocol = "ws:";
  }
  // Append the path if provided
  if (path) {
    currentUrl.pathname = path.trim(); // Trim leading/trailing slashes
  }
  return currentUrl.toString();
}

function debug(msg, level = "danger") {
  const debug_div = document.getElementById("debug");
  if (debug_div) {
    debug_div.className = "";
    debug_div.classList.add("alert");
    debug_div.classList.add("alert-" + level);
    debug_div.innerText = msg;
  }
}

function info(msg, level = "info") {
  const info_div = document.getElementById("info");
  if (info_div) {
    //    info_div.className = "";
    //    info_div.classList.add("alert");
    //    info_div.classList.add("alert-"+level);
    info_div.innerText = msg;
  }
}
function show_result(msg) {
  const result_div = document.getElementById("result");
  if (result_div) {
    result_div.classList.remove("d-none");
    result_div.innerText = msg;
  }
}

function hide_result() {
  const result_div = document.getElementById("result");
  if (result_div) {
    result_div.classList.add("d-none");
  }
}

function clear_snap_container() {
  const result_div = document.getElementById("snap-container");
  if (result_div) {
    result_div.innerHTML = "";
  }
}

function info_toggle() {
  const info_div = document.getElementById("info");
  info_div.classList.toggle("d-none");
  info_div.innerText = "";
}

function video_canvas_toggle() {
  const div = document.getElementById("video_canvas");
  div.classList.toggle("d-none");
}

function snap_container_toggle() {
  const div = document.getElementById("snap-container");
  div.classList.toggle("d-none");
}

function resize_canvas(src, dst) {
  dst.width = src.clientWidth;
  dst.height = src.clientHeight;
}

function isFirefoxMobile() {
  const url = new URL(window.location.href);
  const detect_browser = url.searchParams.get("dct_br");
  if (detect_browser == 0) return false;
  const userAgent = navigator.userAgent?.toLowerCase();
  return userAgent?.includes("firefox") && userAgent?.includes("mobile");
}

function handleOrientationChange(video, canvas) {
  let angle = screen.orientation.angle || window.orientation;
  if (angle !== undefined) {
    const skip_rotate = !isFirefoxMobile();
    if (skip_rotate) {
      angle = 0;
    }
    video.setAttribute("skip_rotate", skip_rotate);
    video.style.transform = `rotate(${angle}deg)`;
  }
  // resize_canvas(canvas_zoom, canvas);
  setTimeout(() => {
    resize_canvas(canvas_zoom, canvas);
  }, 600);
}

function get_command_id() {
  let command_id = undefined;
  if (cam_control?.snap?.checked) {
    command_id = CAM_COMMANDS?.snap;
    // command_id = key in CAM_COMMANDS ? CAM_COMMANDS[key] : CAM_COMMANDS.default;
  }
  command_id = command_id ? command_id : CAM_COMMANDS.default;
  return command_id;
}

// Function to start video stream and get capabilities
async function getCameraCapabilities(deviceId) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { deviceId: { exact: deviceId } } });
    const videoTrack = stream.getVideoTracks()[0];
    let result;
    // Check if getCapabilities is available
    if (videoTrack.getCapabilities) {
      result = videoTrack.getCapabilities();
    } else {
      const settings = videoTrack.getSettings();
      result = {
        width: { max: settings.width, min: 1 },
        height: { max: settings.height, min: 1 },
      };
    }
    // Stop the stream after checking capabilities
    videoTrack.stop();
    return result;
  } catch (error) {
    console.error("Error getting capabilities:", error);
  }
}

function canvas_transformations() {
  const ctx_video = canvas_video.getContext("2d");
  const scaledWidth_video = canvas_zoom.width;
  const scaledHeight_video = canvas_zoom.height;

  const ctx = canvas_video_snap.getContext("2d");
  const scaledWidth = canvas_zoom.width / SNAP_IMAGE_SCALE;
  const scaledHeight = canvas_zoom.height / SNAP_IMAGE_SCALE;

  const angle = screen.orientation.angle || window.orientation;
  if (angle === 90 || angle === 270) {
    // if video declared as rotated
    if (video.getAttribute("skip_rotate") === "true") {
      // if video need to skip rotate
      canvas_video.width = scaledWidth_video;
      canvas_video.height = scaledHeight_video;
      canvas_video_snap.width = scaledWidth;
      canvas_video_snap.height = scaledHeight;
      ctx_video.drawImage(
        video,
        0,
        0,
        canvas_zoom.width,
        canvas_zoom.height,
        0,
        0,
        canvas_video.width,
        canvas_video.height
      );
      try {
        ctx.drawImage(
          canvas_video,
          0,
          0,
          canvas_video.width,
          canvas_video.height,
          0,
          0,
          canvas_video_snap.width,
          canvas_video_snap.height
        );
      } catch (error) {
        console.error("Error ctx.drawImage:");
        return;
      }
    } else {
      // if video need to rotate by +-90 degree, it firefox mobile in genreral
      // swap h <-> w
      canvas_video.height = scaledWidth_video;
      canvas_video.width = scaledHeight_video;
      const radians = (angle * Math.PI) / 180;
      ctx_video.save();
      ctx_video.translate(scaledWidth_video / 2, scaledHeight_video / 2);
      ctx_video.rotate(radians);
      ctx_video.drawImage(
        video,
        0,
        0,
        canvas_zoom.width,
        canvas_zoom.height,
        -scaledWidth_video / 2,
        -scaledHeight_video / 2,
        scaledWidth_video,
        scaledHeight_video
      );
      ctx_video.restore();
      // just copy with downscale
      canvas_video_snap.height = scaledWidth;
      canvas_video_snap.width = scaledHeight;
      try {
        ctx.drawImage(canvas_video, 0, 0, canvas_video.height, canvas_video.width, 0, 0, scaledWidth, scaledHeight);
      } catch (error) {
        console.error("Error ctx.drawImage:");
        return;
      }
    }
  } else {
    // if video declared as not roatated
    canvas_video.width = scaledWidth_video;
    canvas_video.height = scaledHeight_video;
    // ctx_video.clearRect(0, 0, canvas_video.width, canvas_video.height);
    ctx_video.drawImage(
      canvas_zoom,
      0,
      0,
      canvas_video.width,
      canvas_video.height,
      0,
      0,
      scaledWidth_video,
      scaledHeight_video
    );
    canvas_video_snap.width = scaledWidth;
    canvas_video_snap.height = scaledHeight;
    try {
      ctx.drawImage(canvas_video, 0, 0, scaledWidth_video, scaledHeight_video, 0, 0, scaledWidth, scaledHeight);
    } catch (error) {
      console.error("Error ctx.drawImage:");
      return;
    }
  }
  return true;
}

function video_zoom(video) {
  video.addEventListener("loadedmetadata", () => {
    const videoWidth = video.videoWidth;
    const videoHeight = video.videoHeight;
    const cropWidth = videoWidth / zoomFactor;
    const cropHeight = videoHeight / zoomFactor;
    // Set canvas dimensions
    console.log(
      "canvas_zoom:",
      canvas_zoom.width,
      canvas_zoom.height,
      canvas_zoom.clientWidth,
      canvas_zoom.clientHeight
    );
    console.log("cropWidth, cropHeight:", cropWidth, cropHeight);
    // canvas_zoom.width = cropWidth; // Adjust based on your needs
    // canvas_zoom.height = cropHeight; // Adjust based on your needs

    function drawZoomedVideo() {
      const videoWidth = video.videoWidth;
      const videoHeight = video.videoHeight;

      // Calculate the crop area
      const cropWidth = videoWidth / zoomFactor;
      const cropHeight = videoHeight / zoomFactor;
      const cropX = (videoWidth - cropWidth) / 2;
      const cropY = (videoHeight - cropHeight) / 2;
      // Clear the canvas
      ctx_zoom.clearRect(0, 0, canvas_zoom.width, canvas_zoom.height);

      // Draw the zoomed and cropped area
      ctx_zoom.drawImage(
        video,
        cropX,
        cropY,
        cropWidth,
        cropHeight, // Source rectangle
        0,
        0,
        canvas_zoom.width,
        canvas_zoom.height // Destination rectangle
      );

      // Continue drawing
      requestAnimationFrame(drawZoomedVideo);
    }

    // Start drawing the video onto the canvas
    drawZoomedVideo();
  });
}

function commands_processor(message, scale = 1.0) {
  switch (message?.command_id) {
    case CAM_COMMANDS?.snap:
      cam_control.snap.checked = false;
      // console.log("CAM_COMMANDS.snap command");
      if (typeof get_snap_result === "function") {
        result = get_snap_result(message, scale);
        if (result?.result) {
          window.clearInterval(intervalId);
          // button_stop?.click();
          show_result(result?.describe);
          return result?.result;
        }
      }
      break;
  }
}

function commands_post_processor(result_processor, video) {
  const images = [];
  let id = 0;
  for (const result of result_processor) {
    id += 1;
    const crop_boundary = result?.boundary;
    if (!crop_boundary) return;
    const canvas_crop = document.createElement("canvas");
    canvas_crop.id = "canvas_crop_" + id;
    const ctx_crop = canvas_crop.getContext("2d");
    canvas_crop.width = crop_boundary.width;
    canvas_crop.height = crop_boundary.height;
    ctx_crop.drawImage(
      video,
      crop_boundary.x,
      crop_boundary.y,
      crop_boundary.width,
      crop_boundary.height,
      0,
      0,
      crop_boundary.width,
      crop_boundary.height
    );

    const dataURL = canvas_crop.toDataURL("image/png");
    // Create img element and set its source to the data URL
    // imgElement.setAttribute("id", "result-img_" + id);
    images.push({ src: dataURL, title: result?.title, width: crop_boundary.width, height: crop_boundary.height });
    // images.push({ src: dataURL, title: result?.title, width: crop_boundary.width, height: crop_boundary.height });
    // images.push({ src: dataURL, title: result?.title, width: crop_boundary.width, height: crop_boundary.height });
    // images.push({ src: dataURL, title: result?.title, width: crop_boundary.width, height: crop_boundary.height });
    // images.push({ src: dataURL, title: result?.title, width: crop_boundary.width, height: crop_boundary.height });
  }
  const imageContainer = document.getElementById("snap-container");
  imageContainer.innerHTML = ""; // Clear previous images

  for (const image of images) {
    // Append the img element to the container
    const divElement = document.createElement("div");
    divElement.className = "card p-2 pb-0";
    divElement.style = "width: 180px;";
    const imgElement = document.createElement("img");
    imgElement.className = "shadow rounded mx-auto";
    imgElement.src = image.src;
    imgElement.style = `width: 100%; height: 100%; max-width: ${image.width}px;max-height: ${image.height}px;`;
    divElement.appendChild(imgElement);
    const divBodylement = document.createElement("div");
    divBodylement.className = "card-body pb-0";
    const cardtitle = document.createElement("h6");
    cardtitle.innerText = image.title ? image.title : "";
    imgElement.title = image.title ? image.title : "";
    divBodylement.appendChild(cardtitle);
    divElement.appendChild(divBodylement);
    imageContainer.appendChild(divElement);
  }
}

async function startDetection(video, canvas, deviceId) {
  if (!WS_URL) {
    console.error("WS_URL:", WS_URL);
    return;
  }
  const ws_connect = getWebSocketUrl(WS_URL);
  console.log("ws_connect:", ws_connect);
  try {
    info_toggle();
    video_canvas_toggle();
    snap_container_toggle();
    const socket = new WebSocket(ws_connect);
    socket.onopen = () => {
      msg = "WebSocket connection opened!";
      console.log(msg);
      debug(msg, "info");
    };
    socket.onerror = (error) => {
      const msg = "WebSocket connection error. " + ws_connect;
      debug(msg);
    };
    let interval_measure;
    let is_answered = true;
    let skipped_frames = 0;
    let sent_frames = 0;
    let total_frames = 0;
    let adaptive_interval_ms = IMAGE_INTERVAL_MS;
    let average_duration = 0;
    let average_duration_time = 0;
    let average_duration_fps = 0;
    let avg_duration = 0;
    let average_duration_calc = 0;
    let avg_duration_calc = 0;
    let max_queue = 0;
    let cam_cap = await getCameraCapabilities(deviceId);
    socket.addEventListener("open", () => {
      // Start reading video from device
      navigator.mediaDevices
        .getUserMedia({
          audio: false,
          video: {
            deviceId,
            width: cam_cap.width,
            height: cam_cap.height,
          },
        })
        .then((stream) => {
          video.srcObject = stream;
          video_zoom(video);
          handleOrientationChange(canvas_zoom, canvas);
          video.play().then(() => {
            // Adapt overlay canvas size to the video size
            canvas.width = canvas_zoom.width;
            canvas.height = canvas_zoom.height;
            isStreaming = true;

            // Send an image in the WebSocket every DEFINED ms
            const sendImage = () => {
              total_frames += 1;
              intervalId = setTimeout(sendImage, adaptive_interval_ms);
              if (!is_answered) {
                skipped_frames += 1;
                const sk_perc = ((skipped_frames / total_frames) * 100).toFixed(2);
                const currentTime = new Date().toLocaleTimeString();
                debug(
                  `At ${currentTime}: skipped for the sending frame, not received in time. Total frames was skipped: ${skipped_frames} (${sk_perc}%) of ${total_frames}`,
                  "info"
                );
                return;
              }
              is_answered = false;
              // On canvas to draw current video image
              if (!canvas) {
                console.error("No Canvas...");
                return;
              }
              if (!canvas_video) {
                canvas_video = document.createElement("canvas");
                canvas_video.id = "canvas_video";
              }
              if (!canvas_video_snap) {
                canvas_video_snap = document.createElement("canvas");
                canvas_video_snap.id = "canvas_video_snap";
              }
              if (!canvas_transformations()) return;

              // Convert it to JPEG and send it to the WebSocket
              interval_measure = performance.now();
              const commandId = get_command_id();
              canvas_video_snap.toBlob((blob) => {
                if (blob) {
                  // Send the image data and command ID
                  // return socket.send(packMessage(commandId, blob));
                  return sendPackedMessage(socket, commandId, blob);
                } else {
                  console.error("Failed to capture image data!");
                }
              }, "image/jpeg");
              sent_frames += 1;
            }; // sendImage
            intervalId = setTimeout(sendImage, IMAGE_INTERVAL_MS);
          });
        });
    });

    // Listen for messages
    const MEASURE_FRAMES = 100;
    socket.addEventListener("message", function (event) {
      is_answered = true;
      let avg_correction = 1;
      const duration = Math.round(performance.now() - interval_measure);
      average_duration += duration;
      message_data = JSON.parse(event.data);
      average_duration_calc += message_data?.duration_ms;
      if (sent_frames % MEASURE_FRAMES == 0) {
        if (average_duration > 0) {
          avg_duration = Math.round(average_duration / MEASURE_FRAMES);
          if (avg_duration < 75) avg_correction = 2;
          else if (avg_duration < 30) avg_correction = 3;
          adaptive_interval_ms = Math.round(avg_duration * ADAPTIVE_FACTOR * avg_correction);
          average_duration = 0;
          average_duration_fps = (MEASURE_FRAMES / ((performance.now() - average_duration_time) / 1000.0)).toFixed(1);
          average_duration_time = performance.now();
        }
        if (average_duration_calc > 0) {
          avg_duration_calc = Math.round(average_duration_calc / MEASURE_FRAMES);
          average_duration_calc = 0;
        }
      }
      if (draw_detected) {
        result = draw_detected(video, canvas, message_data, SNAP_IMAGE_SCALE);
        if (result?.error) debug(result.error);
      }
      max_queue = Math.max(message_data.queue_id, max_queue);
      const angle = screen.orientation.angle || window.orientation;
      //      const sr = video.getAttribute("skip_rotate");
      let info_text = `Queue: ${message_data?.queue_id}`;
      if (max_queue) info_text += ` (max:${max_queue})`;
      info_text += `. Sending adaptive interval: ${adaptive_interval_ms} ms.`;
      info_text += ` Answer time: ${duration}`;
      if (avg_duration) info_text += ` (avg: ${avg_duration})`;
      info_text += " ms.";
      if (average_duration_fps) info_text += ` ${average_duration_fps} fps.`;
      info_text += ` Calculated API method duration: ${message_data?.duration_ms}`;
      if (avg_duration_calc) info_text += ` (avg:${avg_duration_calc})`;
      info_text += " ms.";
      if (angle !== undefined) info_text += ` Rotation: ${angle} degree.`;
      info(info_text);
      const result_processor = commands_processor(message_data, SNAP_IMAGE_SCALE);
      if (result_processor) {
        console.log(canvas_video_snap);
        commands_post_processor(result_processor, canvas_video);
        button_stop?.click();
      }
    }); //on_message

    // Stop the interval and video reading on close
    socket.addEventListener("close", function () {
      window.clearInterval(intervalId);
      video.pause();
    });
    return socket;
  } catch (error) {
    if (error instanceof SyntaxError) {
      debug("Invalid WebSocket URL format:" + error.message);
      console.error("Invalid WebSocket URL format:", error.message);
    } else {
      debug("WebSocket connection error:" + error.message);
      console.error("WebSocket connection error:", error);
    }
  }
}

// Function to stop the video stream and turn off the LED (if possible)
function stopDetection(video, canvas) {
  if (canvas) {
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
    setTimeout(() => {
      debug("Video stream stopped", "info");
    }, 2000);
  }
  info_toggle();
  video_canvas_toggle();
  snap_container_toggle();
}

function cam_detect(cameraSelect) {
  navigator.mediaDevices
    .getUserMedia({ audio: false, video: true })
    .then((stream) => {
      const tracks = stream.getTracks();
      tracks.forEach(function (track) {
        track.stop(); // Stop individual media track
      });
      // console.log(cam_capabilities);
      navigator.mediaDevices
        .enumerateDevices()
        .then(async (devices) => {
          const videoDevices = devices.filter((device) => device.kind === "videoinput");
          // Check for available cameras
          // console.log('Check for available cameras',devices);
          if (!videoDevices.length) {
            const noCameraOption = document.createElement("option");
            noCameraOption.value = ""; // Set an empty value to avoid potential selection issues
            noCameraOption.innerText = "No cameras detected";
            console.log("No cameras detected", noCameraOption.innerText);
            cameraSelect.appendChild(noCameraOption);
            return; // Exit if no cameras are found
          }

          // Filter and populate options
          let video_dev_id = 0;
          for (const device of videoDevices) {
            console.log("Check for available cameras");
            const cam_cap = await getCameraCapabilities(device.deviceId);

            const deviceOption = document.createElement("option");
            if (device.deviceId) {
              deviceOption.value = device.deviceId;
              deviceOption.innerText = device.label || `Camera ${devices.indexOf(device) + 1}`; // Use label or fallback
              if (cam_cap) {
                deviceOption.innerText += `, max: ${cam_cap?.width.max}x${cam_cap?.height.max}`;
              }
              console.log("cameras detected", video_dev_id);
              cameraSelect.appendChild(deviceOption);
              video_dev_id += 1;
            } else {
              console.log("cameras detected but empty");
              deviceOption.value = "";
              deviceOption.innerText = "WARNING: Cameras detected but with empty names";
              cameraSelect.appendChild(deviceOption);
            }
          }
        })
        .catch((error) => {
          console.error("Error listing cameras:", error);
          // Handle errors gracefully (e.g., display an error message to the user)
        });
    })
    .catch((err) => {
      const noCameraOption = document.createElement("option");
      noCameraOption.value = ""; // Set an empty value to avoid potential selection issues
      noCameraOption.innerText = "No cameras detected. Permission required.";
      console.error("No cameras detected", err);
      cameraSelect.appendChild(noCameraOption);
    });
}

function onClickButtonStop(event) {
  event.preventDefault();
  // Close the WebSocket connection (if it exists)
  if (socket) {
    stopDetection(video, canvas);
    socket.close();
    setTimeout(() => {
      debug("WebSocket connection closed", "info");
    }, 600);
    socket = null; // Clear the socket reference
  } else {
    console.log("No WebSocket connection to close");
  }
  // buttons
  if (button_stop) {
    button_start.classList.toggle("d-none");
  }
  if (button_stop) {
    button_stop.classList.toggle("d-none");
  }
  if (button_snap) {
    if (typeof get_snap_result === "function") {
      button_snap.classList.toggle("d-none");
    }
  }
}

async function onClickButtonStart(event) {
  event.preventDefault();
  // Close previous socket is there is one
  if (socket) {
    socket.close();
  }
  const deviceId = cameraSelect?.selectedOptions[0]?.value;
  if (deviceId) {
    socket = await startDetection(video, canvas, deviceId);
    if (socket) {
      if (button_start) {
        button_start.classList.toggle("d-none");
      }
      if (button_stop) {
        button_stop.classList.toggle("d-none");
      }
      if (button_snap) {
        if (typeof get_snap_result === "function") {
          button_snap.classList.toggle("d-none");
        }
      }
      hide_result();
      clear_snap_container();
    }
  } else {
    debug("Not detected device ID");
  }
}

function add_zoom_controls(controls) {
  // Create a div to contain the form control
  const formGroupDivCol = document.createElement("div");
  formGroupDivCol.className = "col-auto ps-0";
  const formGroupDiv = document.createElement("div");
  formGroupDiv.className = "input-group input-group-sm";

  // Create a label for the input
  const labelElement = document.createElement("span");
  labelElement.setAttribute("for", "zoom_control");
  labelElement.className = "input-group-text";
  labelElement.textContent = "Zoom Scale";

  // Create an input element for the zoom control
  const inputElement = document.createElement("input");
  inputElement.setAttribute("type", "number"); // Use "number" for numeric input
  inputElement.setAttribute("id", "zoom_control");
  inputElement.setAttribute("name", "zoom_control"); // Set a name for form submission if needed
  inputElement.className = "form-control";
  inputElement.value = zoomFactor; // Default zoom scale
  inputElement.min = 1; // Set the minimum value
  inputElement.max = 6; // Set the minimum value
  inputElement.step = 1; // Set the step value (increments/decrements)

  // Append label and input to the div
  formGroupDiv.appendChild(labelElement);
  formGroupDiv.appendChild(inputElement);
  formGroupDivCol.appendChild(formGroupDiv);

  // Append the div to the parent controls element
  controls.appendChild(formGroupDivCol);
  inputElement.addEventListener("change", (e) => {
    zoomFactor = e.target.value;
  });
}

// DOMContentLoaded
function onDOMLoaded(event) {
  video = document.getElementById("video");
  canvas = document.getElementById("canvas");
  canvas_video = document.getElementById("canvas_video");
  canvas_zoom = document.getElementById("canvas_zoom");
  ctx_zoom = canvas_zoom.getContext("2d");
  cameraSelect = document.getElementById("camera-select");
  controls = document.getElementById("controls");
  add_zoom_controls(controls);
  if (typeof init_controls === "function") {
    init_controls(controls);
  }
  cam_control["snap"] = document.getElementById("checkbox-snap");
  cam_detect(cameraSelect);
  button_start = document.getElementById("button-start");
  button_stop = document.getElementById("button-stop");
  button_snap = document.getElementById("button-snap");
  button_stop?.addEventListener("click", onClickButtonStop); // click_btn_stop
  // Start face detection on the selected camera on submit
  button_start?.addEventListener("click", onClickButtonStart);

  // video.addEventListener("loadedmetadata", function () {
  //   //    console.log("loadedmetadata");
  //   // resize_canvas(video, canvas);
  // });
}
// DOMContentLoaded

window.addEventListener("DOMContentLoaded", onDOMLoaded);
// Add event listeners for resize and orientation change
window.addEventListener("resize", (event) => {
  //    video.pause();
  handleOrientationChange(video, canvas);
});
