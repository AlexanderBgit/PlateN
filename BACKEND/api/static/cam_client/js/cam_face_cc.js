const draw_detected = (video, canvas, detected, scale = 1.0) => {
  const ctx = canvas.getContext("2d");
  ctx.width = video.videoWidth;
  ctx.height = video.videoHeight;
  ctx.clearRect(0, 0, ctx.width, ctx.height);
  if (!detected) return;
  ctx.lineWidth = 5; // Set line thickness in pixels
  ctx.beginPath();
  if (detected.objects === undefined) return;
  for (obj of detected.objects) {
    const [x1, y1, x2, y2] = obj.boundary;
    ctx.strokeStyle = "#49fb35";
    ctx.beginPath();
    ctx.rect(x1 * scale, y1 * scale, x2 * scale, y2 * scale);
    ctx.stroke();
  }
};
