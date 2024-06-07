
function draw_box(ctx, scaledBox, titleText) {
  // Title text properties
  const titleFontSize = 16;
  const titleYOffset = 20; // Adjust offset for text placement
  // Draw the box
  ctx.strokeStyle = "#49fb35"; // Set stroke color
  ctx.lineWidth = 5; // Set line thickness in pixels
  ctx.beginPath(); // Start a new path
  ctx.rect(scaledBox.x, scaledBox.y, scaledBox.width, scaledBox.height); // Define the rectangle
  ctx.stroke(); // Stroke the path (draw lines)

  ctx.font = `${titleFontSize}px Arial`; // Set font style and size
  const textMetrics = ctx.measureText(titleText); // Get text dimensions
  const textWidth = textMetrics.width;
  const textHeight = titleFontSize; // Assuming font height is equal to font size

  // Adjust padding as needed (example: 5 pixels)
  const padding = { x: 5, y: 5 }
  const background = {
   x: scaledBox.x + scaledBox.width / 2 - textWidth / 2 - padding.x,
   y: scaledBox.y - titleYOffset - textHeight - padding.y,
   width: textWidth + padding.x * 2,
   height: textHeight + padding.y * 2,
  }
  ctx.fillStyle = "#000000A0"; // Set background color
  ctx.fillRect(background.x, background.y, background.width, background.height);


  // Draw the title text
  ctx.font = `${titleFontSize}px Arial`; // Set font style and size
  ctx.fillStyle = ctx.strokeStyle; // Set text color
  ctx.fillText(
    titleText,
    scaledBox.x + scaledBox.width / 2 - textWidth / 2,
    scaledBox.y - titleYOffset
  ); // Center text on top of the box
}

const draw_detected = (video, canvas, detected, scale = 1.0) => {
  const ctx = canvas.getContext("2d");
  ctx.width = video.videoWidth;
  ctx.height = video.videoHeight;
  ctx.beginPath();
  ctx.clearRect(0, 0, ctx.width, ctx.height);
  for (obj of detected.objects) {
    const [boxX, boxY, boxWidth, boxHeight] = obj.boundary;
    // Efficient scaling using destructuring and spread operator
    const scaledBox = {
      x: boxX * scale,
      y: boxY * scale,
      width: boxWidth * scale,
      height: boxHeight * scale,
    };
    const titleText = `QR: ${obj.text}`;
    draw_box(ctx, scaledBox, titleText);
  }
};
