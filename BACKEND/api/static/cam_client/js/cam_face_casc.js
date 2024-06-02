

const draw_detected = (video, canvas, detected) => {
  console.log("detected: ",detected)
  const ctx = canvas.getContext('2d');
  ctx.width = video.videoWidth;
  ctx.height = video.videoHeight;
  ctx.beginPath();
  ctx.clearRect(0, 0, ctx.width, ctx.height);
  for (obj of detected.objects) {
    const [x, y, width, height] = obj.boundary;
    ctx.strokeStyle = "#49fb35";
    ctx.beginPath();
    ctx.rect(x, y, width, height);
    ctx.stroke();
  }
};