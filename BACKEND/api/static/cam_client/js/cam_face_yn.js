

const draw_detected = (video, canvas, detected, scale = 1.0) => {
  const ctx = canvas.getContext('2d');
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
  }
};