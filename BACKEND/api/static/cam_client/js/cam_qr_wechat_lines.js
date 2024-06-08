function draw_lines(ctx, points, titleText) {
  if (points.length != 4) return; //skip if points not present
  // Draw the box (replace with line drawing)
  ctx.strokeStyle = "#49fb35"; // Set stroke color
  ctx.lineWidth = 5; // Set line thickness in pixels
  ctx.beginPath(); // Start a new path
  ctx.moveTo(points[0].x, points[0].y); // Move to the first point
  ctx.lineTo(points[1].x, points[1].y); // Draw line to second point
  ctx.lineTo(points[2].x, points[2].y); // Draw line to third point
  ctx.lineTo(points[3].x, points[3].y); // Draw line to fourth point
  ctx.closePath(); // Close the path (optional for a closed figure)
  ctx.stroke(); // Stroke the path (draw lines)

  if (!titleText) return; //skip if title not present

  // const scaledBox = {
  //   x: Math.min(points[3].x, points[2].x, points[1].x, points[0].x),
  //   y: Math.min(points[3].y, points[2].y, points[1].y, points[0].y),
  //   width:
  //     Math.max(points[3].x, points[2].x, points[1].x, points[0].x) -
  //     Math.min(points[3].x, points[2].x, points[1].x, points[0].x),
  //   height:
  //     Math.max(points[3].y, points[2].y, points[1].y, points[0].y) -
  //     Math.min(points[3].y, points[2].y, points[1].y, points[0].y),
  // };

  const scaledBox = {
    x: Math.min(...points.map((point) => point.x)),
    y: Math.min(...points.map((point) => point.y)),
    width: Math.max(...points.map((point) => point.x)) - Math.min(...points.map((point) => point.x)),
    height: Math.max(...points.map((point) => point.y)) - Math.min(...points.map((point) => point.y)),
  };

  // Title text properties
  const titleFontSize = 16;
  const titleYOffset = 20; // Adjust offset for text placement

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
  //  ctx.font = `${titleFontSize}px Arial`; // Set font style and size
  ctx.fillStyle = ctx.strokeStyle; // Set text color
  ctx.fillText(titleText, scaledBox.x + scaledBox.width / 2 - textWidth / 2, scaledBox.y - titleYOffset); // Center text on top of the box
}

// Function to create point objects from boundary coordinates
function createPoints(boundary, scale = 1.0) {
  const points = [];
  for (point of boundary) {
    points.push({ x: point[0] * scale, y: point[1] * scale });
  }
  return points;
}

function draw_detected(video, canvas, detected, scale = 1.0) {
  const ctx = canvas.getContext("2d");
  ctx.width = video.videoWidth;
  ctx.height = video.videoHeight;
  ctx.clearRect(0, 0, ctx.width, ctx.height);
  if (detected.objects === undefined) return;
  ctx.beginPath();
  for (obj of detected.objects) {
    const points = createPoints(obj.boundary, scale);
    const titleText = `QR: ${obj.text}`;
    draw_lines(ctx, points, titleText);
  }
}
