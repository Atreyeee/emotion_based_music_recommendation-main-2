// Emotion Radar — webcam capture, backend polling, and HUD overlay rendering.
(() => {
  const video = document.getElementById("webcam");
  const overlay = document.getElementById("overlay");
  const overlayCtx = overlay.getContext("2d");
  const cameraOffMessage = document.getElementById("cameraOffMessage");
  const toggleVideoButton = document.getElementById("toggleVideo");
  const fileInput = document.getElementById("imageUpload");
  const recommendedPlaylistButton = document.getElementById("recommendedPlaylist");
  const linkStatus = document.getElementById("linkStatus");
  const faceStatus = document.getElementById("faceStatus");
  const emotionStatus = document.getElementById("emotionStatus");

  const DETECT_URL = window.DETECT_EMOTION_URL;
  const CSRF_TOKEN = window.CSRF_TOKEN;
  const FRAME_INTERVAL_MS = 500;
  const CAPTURE_WIDTH = 640;
  const CAPTURE_HEIGHT = 480;

  let mediaStream = null;
  let isVideoOn = false;
  let lastFrameTime = 0;
  let detectedEmotion = null;
  let currentPlaylistUrl = null;

  // Hidden capture canvas — always CAPTURE_WIDTH x CAPTURE_HEIGHT (4:3),
  // matching the video frame's CSS aspect-ratio so the overlay scale
  // factor below stays uniform on both axes.
  const captureCanvas = document.createElement("canvas");
  captureCanvas.width = CAPTURE_WIDTH;
  captureCanvas.height = CAPTURE_HEIGHT;
  const captureCtx = captureCanvas.getContext("2d");

  function setLinkStatus(text, color) {
    linkStatus.textContent = text;
    linkStatus.style.color = color || "var(--green)";
  }

  function resizeOverlay() {
    const rect = video.getBoundingClientRect();
    overlay.width = rect.width;
    overlay.height = rect.height;
  }
  window.addEventListener("resize", resizeOverlay);
  video.addEventListener("loadeddata", resizeOverlay);

  function drawFaceBox(box) {
    overlayCtx.clearRect(0, 0, overlay.width, overlay.height);
    if (!box) return;

    const scaleX = overlay.width / CAPTURE_WIDTH;
    const scaleY = overlay.height / CAPTURE_HEIGHT;
    const x = box.x * scaleX;
    const y = box.y * scaleY;
    const w = box.width * scaleX;
    const h = box.height * scaleY;
    const bracket = Math.min(w, h) * 0.22;

    overlayCtx.strokeStyle = "#3dffa0";
    overlayCtx.lineWidth = 2;
    overlayCtx.shadowColor = "#3dffa0";
    overlayCtx.shadowBlur = 8;

    // Four corner brackets instead of a plain rectangle — matches the HUD panel style.
    const corners = [
      [x, y, 1, 1],
      [x + w, y, -1, 1],
      [x, y + h, 1, -1],
      [x + w, y + h, -1, -1],
    ];
    corners.forEach(([cx, cy, dx, dy]) => {
      overlayCtx.beginPath();
      overlayCtx.moveTo(cx, cy + bracket * dy);
      overlayCtx.lineTo(cx, cy);
      overlayCtx.lineTo(cx + bracket * dx, cy);
      overlayCtx.stroke();
    });

    if (detectedEmotion) {
      overlayCtx.shadowBlur = 0;
      overlayCtx.font = "16px 'Share Tech Mono', monospace";
      overlayCtx.fillStyle = "#3dffa0";
      overlayCtx.fillText(detectedEmotion.toUpperCase(), x, Math.max(14, y - 8));
    }
  }

  function getCSRFToken() {
    return (
      document.cookie
        .split("; ")
        .find((row) => row.startsWith("csrftoken="))
        ?.split("=")[1] || CSRF_TOKEN
    );
  }

  async function sendFrame(dataUrl) {
    setLinkStatus("SCANNING", "var(--amber)");
    try {
      const response = await fetch(DETECT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
        body: JSON.stringify({ frame: dataUrl }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();

      detectedEmotion = result.emotion || null;
      currentPlaylistUrl = result.playlist_url || null;

      faceStatus.textContent = result.face_box ? "LOCKED" : "NO SIGNAL";
      emotionStatus.textContent = detectedEmotion ? detectedEmotion.toUpperCase() : "—";
      recommendedPlaylistButton.disabled = !currentPlaylistUrl;
      drawFaceBox(result.face_box);
      setLinkStatus("ONLINE", "var(--green)");
    } catch (err) {
      console.error("Emotion detection request failed:", err);
      setLinkStatus("ERROR", "var(--red)");
    }
  }

  function captureLoop(timestamp) {
    if (isVideoOn && video.readyState === 4 && timestamp - lastFrameTime >= FRAME_INTERVAL_MS) {
      captureCtx.drawImage(video, 0, 0, CAPTURE_WIDTH, CAPTURE_HEIGHT);
      sendFrame(captureCanvas.toDataURL("image/jpeg", 0.8));
      lastFrameTime = timestamp;
    }
    requestAnimationFrame(captureLoop);
  }

  function startWebcam() {
    navigator.mediaDevices
      .getUserMedia({ video: { width: CAPTURE_WIDTH, height: CAPTURE_HEIGHT } })
      .then((stream) => {
        mediaStream = stream;
        video.srcObject = stream;
        cameraOffMessage.style.display = "none";
        isVideoOn = true;
        toggleVideoButton.textContent = "Turn Camera Off";
        setLinkStatus("ONLINE", "var(--green)");
      })
      .catch(() => {
        setLinkStatus("DENIED", "var(--red)");
        alert("Camera access is required for live scanning. You can still use Upload Image below.");
      });
  }

  function stopWebcam() {
    mediaStream?.getTracks().forEach((track) => track.stop());
    mediaStream = null;
    video.srcObject = null;
    cameraOffMessage.style.display = "flex";
    isVideoOn = false;
    toggleVideoButton.textContent = "Turn Camera On";
    overlayCtx.clearRect(0, 0, overlay.width, overlay.height);
    faceStatus.textContent = "—";
    emotionStatus.textContent = "—";
    setLinkStatus("STANDBY");
  }

  toggleVideoButton.addEventListener("click", () => (isVideoOn ? stopWebcam() : startWebcam()));

  fileInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => sendFrame(e.target.result);
    reader.readAsDataURL(file);
  });

  recommendedPlaylistButton.addEventListener("click", () => {
    if (currentPlaylistUrl) window.location.href = currentPlaylistUrl;
  });

  startWebcam();
  requestAnimationFrame(captureLoop);
})();
