const glasses_img = new Image();

function apply_mask(ctx, eye_right, eye_left){
    if (glasses_img.complete) {
       const aspect = glasses_img.height / glasses_img.width;
       const eye_width = eye_right.x-eye_left.x;
       const img_width = eye_width * 2.5;
       const img_height = (img_width * aspect);
       const img_center = {
          x: eye_left.x + Math.round( img_width / 2),
          y: eye_left.y + Math.round( img_height / 2),
       }
       const eye_center = {
          x: Math.round((eye_left.x + eye_right.x) / 2),
          y: Math.abs(Math.round((eye_left.y + eye_right.y) / 2)),
       }

      ctx.drawImage(glasses_img, eye_left.x + (eye_center.x - img_center.x ) , eye_left.y + (eye_center.y - img_center.y ) , img_width, img_height);
    }
}


const draw_detected = (video, canvas, detected, scale = 1.0) => {
  const ctx = canvas.getContext('2d');
  ctx.width = video.videoWidth;
  ctx.height = video.videoHeight;
  ctx.beginPath();
  ctx.clearRect(0, 0, ctx.width, ctx.height);
  for (obj of detected.objects) {
    const [boxX, boxY, boxWidth, boxHeight] = obj.boundary;
    const [eye_left_x, eye_left_y] = obj.eye_left;
    const [eye_right_x, eye_right_y] = obj.eye_right;

    const eye_left = {
      x: eye_left_x * scale,
      y: eye_left_y * scale,
    }

    const eye_right = {
      x: eye_right_x * scale,
      y: eye_right_y * scale,
    }

    // Efficient scaling using destructuring and spread operator
    const scaledBox = {
      x: boxX * scale,
      y: boxY * scale,
      width: boxWidth * scale,
      height: boxHeight * scale,
    };

//    console.log(obj)

    // Title text properties
    const titleText = `Score: ${obj.score}`;
    const titleFontSize = 16;
    const titleYOffset = 20; // Adjust offset for text placement

    // Draw the box
    ctx.strokeStyle = "#49fb35"; // Set stroke color
    ctx.beginPath();  // Start a new path
    ctx.rect(scaledBox.x, scaledBox.y, scaledBox.width, scaledBox.height);  // Define the rectangle
    ctx.stroke();  // Stroke the path (draw lines)

    // Draw the title text
    ctx.font = `${titleFontSize}px Arial`; // Set font style and size
    ctx.fillStyle = ctx.strokeStyle; // Set text color
    ctx.fillText(titleText, scaledBox.x + (scaledBox.width / 2) - (ctx.measureText(titleText).width / 2), scaledBox.y - titleYOffset); // Center text on top of the box


     // Draw landmarks
    for (const landmark of obj.landmarks) {
      // Set drawing properties
      ctx.fillStyle = '#00FF00'; // Set fill color (green)
      ctx.beginPath(); // Start a new path

      // Draw a circle at each landmark
      const radius = 2; // Adjust radius as needed
      ctx.arc(landmark[0]*scale, landmark[1]*scale, radius, 0, Math.PI * 2); // Draw circle (x, y, radius, start angle, end angle)

      // Fill the circle (optional, comment out for unfilled circles)
      ctx.fill();
    }

    apply_mask(ctx, eye_right, eye_left);

  }
};


glasses_img.src = '/api/v1/static/cam_client/glasses.png';