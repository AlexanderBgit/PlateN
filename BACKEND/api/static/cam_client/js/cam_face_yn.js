const glasses_img = new Image();
const control = {};

function apply_mask(ctx, eye_right, eye_left) {
  if (glasses_img.complete) {
    const aspect = glasses_img.height / glasses_img.width;
    const eye_width = eye_right.x - eye_left.x;
    const img_width = eye_width * 2.5;
    const img_height = img_width * aspect;
    const eye_center = {
      x: Math.round((eye_left.x + eye_right.x) / 2),
      y: Math.round((eye_left.y + eye_right.y) / 2),
    };

    // Calculate the angle of rotation in radians
    const angle = Math.atan2(eye_right.y - eye_left.y, eye_right.x - eye_left.x);

    // Save the current context state
    ctx.save();

    // Move the context to the center of the eyes
    ctx.translate(eye_center.x, eye_center.y);

    // Rotate the context around the center of the eyes
    ctx.rotate(angle);

    // Draw the glasses image, offsetting by half the image dimensions to center it
    ctx.drawImage(glasses_img, -img_width / 2, -img_height / 2, img_width, img_height);

    // Restore the context to its original state
    ctx.restore();
  }
}

function apply_scale(boundary, scale) {
  const keys = Object.keys(boundary);
  for (const key of keys) {
    boundary[key] *= scale;
  }
  return boundary;
}

function apply_scale_array(boundary, scale) {
  return boundary.map((point) => {
    return apply_scale(point);
  });
}

function draw_landmarks(ctx, landmarks, scale) {
  for (const landmark of landmarks) {
    // Set drawing properties
    ctx.fillStyle = "#00FF00"; // Set fill color (green)
    ctx.beginPath(); // Start a new path

    // Draw a circle at each landmark
    const radius = 2; // Adjust radius as needed
    ctx.arc(landmark[0] * scale, landmark[1] * scale, radius, 0, Math.PI * 2); // Draw circle (x, y, radius, start angle, end angle)

    // Fill the circle (optional, comment out for unfilled circles)
    ctx.fill();
  }
}

function draw_box(ctx, scaledBox, titleText) {
  if (!scaledBox) return;
  // Title text properties
  const titleFontSize = 16;
  const titleYOffset = 20; // Adjust offset for text placement
  // Draw the box
  ctx.strokeStyle = "#49fb35"; // Set stroke color
  ctx.lineWidth = 5; // Set line thickness in pixels
  ctx.beginPath(); // Start a new path
  ctx.rect(scaledBox.x, scaledBox.y, scaledBox.width, scaledBox.height); // Define the rectangle
  ctx.stroke(); // Stroke the path (draw lines)

  if (!titleText) return;

  ctx.font = `${titleFontSize}px Arial`; // Set font style and size
  const textMetrics = ctx.measureText(titleText); // Get text dimensions
  const textWidth = textMetrics.width;
  const textHeight = titleFontSize; // Assuming font height is equal to font size

  // Adjust padding as needed
  const padding = { x: 10, y: 6 };
  const background = {
    x: scaledBox.x + scaledBox.width / 2 - textWidth / 2 - padding.x,
    y: scaledBox.y - titleYOffset - textHeight - padding.y / 2,
    width: textWidth + padding.x * 2,
    height: textHeight + padding.y * 2,
  };
  ctx.fillStyle = "#000000A0"; // Set background color
  ctx.fillRect(background.x, background.y, background.width, background.height);

  // Draw the title text
  ctx.font = `${titleFontSize}px Arial`; // Set font style and size
  ctx.fillStyle = ctx.strokeStyle; // Set text color
  ctx.fillText(titleText, scaledBox.x + scaledBox.width / 2 - textWidth / 2, scaledBox.y - titleYOffset); // Center text on top of the box
}

const draw_detected = (video, canvas, detected, scale = 1.0) => {
  if (detected.error) {
    return { error: detected.error };
  }
  const ctx = canvas.getContext("2d");
  ctx.width = video.videoWidth;
  ctx.height = video.videoHeight;
  ctx.clearRect(0, 0, ctx.width, ctx.height);
  if (detected.objects === undefined) return;
  ctx.beginPath();
  for (obj of detected.objects) {
    const [boxX, boxY, boxWidth, boxHeight] = obj.boundary;
    const [eye_left_x, eye_left_y] = obj.eye_left;
    const [eye_right_x, eye_right_y] = obj.eye_right;

    const eye_left = {
      x: eye_left_x * scale,
      y: eye_left_y * scale,
    };

    const eye_right = {
      x: eye_right_x * scale,
      y: eye_right_y * scale,
    };

    // Efficient scaling using destructuring and spread operator
    const scaledBox = {
      x: boxX * scale,
      y: boxY * scale,
      width: boxWidth * scale,
      height: boxHeight * scale,
    };
    const titleText = control?.scores.checked ? `Score: ${obj.score}` : undefined;

    draw_box(ctx, scaledBox, titleText);
    if (control?.glasses.checked) apply_mask(ctx, eye_right, eye_left);
    if (control?.landmarks.checked) draw_landmarks(ctx, obj.landmarks, scale);
  }
};

// function get_snap_result(message) {
//   if (message?.objects) {
//     detected = message.objects.length;
//     scores = message?.objects.map((obj) => obj.scores, obj);
//     return `Detected objects: ${detected}, scores: ${scores}`;
//   }
// }

function describe_boundary(boundary) {
  if (boundary?.length != 4) {
    return boundary;
  }
  return {
    x: boundary[0],
    y: boundary[1],
    width: boundary[2],
    height: boundary[3],
  };
}

function get_snap_result(message, scale = 1.0) {
  // console.log("get_snap_result", scale);
  if (message?.objects) {
    const detected_obj = message.objects.length;
    const result = [];
    for (const obj of message.objects) {
      const boundary = apply_scale(describe_boundary(obj.boundary), scale);
      const score = obj.score;
      const title = `Score: ${Math.round(score * 100)}%`;
      result.push({
        title: title,
        score: score,
        boundary: boundary,
      });
    }
    const replacer = (key, value) => (key === "title" ? undefined : value);
    const result_formated = JSON.stringify(result, replacer).replace(/,/g, ", ");
    return {
      result: result,
      describe: `Detected Face objects: ${detected_obj}.  Objects: ` + result_formated,
    };
  }
}

function init_controls(controls) {
  glasses_img.src = "/api/v1/static/cam_client/glasses.png";
  if (!controls) return;
  const controlConfigs = [
    { label: "Glasses", id: "glasses_id", name: "glasses" },
    { label: "Landmarks", id: "landmarks_id", name: "landmarks" },
    { label: "Scores", id: "scores_id", name: "scores" },
  ];
  const elements = [];

  controlConfigs.forEach((config) => {
    const formCheckDiv = document.createElement("div");
    formCheckDiv.className = "form-check";

    const checkboxElement = document.createElement("input");
    checkboxElement.setAttribute("type", "checkbox");
    checkboxElement.setAttribute("id", config.id);
    checkboxElement.className = "form-check-input";
    checkboxElement.checked = true;
    if (config?.name) control[config.name] = checkboxElement;

    const labelElement = document.createElement("label");
    labelElement.setAttribute("for", config.id);
    labelElement.className = "form-check-label";
    labelElement.innerText = config.label;

    formCheckDiv.appendChild(checkboxElement);
    formCheckDiv.appendChild(labelElement);

    controls.appendChild(formCheckDiv);
  });

  for (const element of elements) {
    controls.appendChild(element);
  }
}

// glasses_img.src = "/api/v1/static/cam_client/glasses.png";
