// HTML Elements
const video = document.getElementById("webcam");
const toggleVideoButton = document.getElementById("toggleVideo");
const cameraOffMessage = document.getElementById("cameraOffMessage");
const recommendedPlaylistButton = document.getElementById("recommendedPlaylist");
const fileInput = document.getElementById("imageUpload");

// State Variables
let isVideoOn = true;
let mediaStream = null;
let detectedEmotion = null;
let faceBox = null;
const frameInterval = 500;
let lastFrameTime = Date.now();
const csrfToken = getCSRFToken();

// CSRF Token Helper
function getCSRFToken() {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1] || "";
}

// Webcam Functions
function startWebcam() {
  console.log("Starting webcam...");
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then((stream) => {
      mediaStream = stream;
      video.srcObject = stream;
      video.style.display = "block";
      cameraOffMessage.style.display = "none";
      isVideoOn = true;
      toggleVideoButton.textContent = "Turn Video Off";
      console.log("Webcam started successfully.");
    })
    .catch(() => alert("Please allow access to the webcam."));
}

function stopWebcam() {
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }
  video.style.display = "none";
  cameraOffMessage.style.display = "flex";
  isVideoOn = false;
  toggleVideoButton.textContent = "Turn Video On";
  clearFaceOverlay();
}

// Overlay Canvas
const overlayCanvas = document.createElement("canvas");
const overlayCtx = overlayCanvas.getContext("2d");
document.body.appendChild(overlayCanvas);
overlayCanvas.style.position = "absolute";
overlayCanvas.style.zIndex = "10";
overlayCanvas.width = 640;
overlayCanvas.height = 480;

function alignCanvas() {
  const rect = video.getBoundingClientRect();
  overlayCanvas.style.width = `${rect.width}px`;
  overlayCanvas.style.height = `${rect.height}px`;
  overlayCanvas.style.top = `${rect.top}px`;
  overlayCanvas.style.left = `${rect.left}px`;
}

window.addEventListener("resize", alignCanvas);
video.addEventListener("loadeddata", alignCanvas);

function drawFaceOverlay() {
  overlayCtx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
  if (faceBox) {
    overlayCtx.strokeStyle = "pink";
    overlayCtx.lineWidth = 3;
    overlayCtx.strokeRect(faceBox.x, faceBox.y, faceBox.width, faceBox.height);
    overlayCtx.fillStyle = "black";
    overlayCtx.font = "18px Arial";
    overlayCtx.fillText(detectedEmotion, faceBox.x, faceBox.y - 10);
  }
}

function clearFaceOverlay() {
  overlayCtx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
}

// Emotion Detection
const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d");
canvas.width = 640;
canvas.height = 480;

async function detectEmotionFromVideo() {
  if (!isVideoOn) return;
  const currentTime = Date.now();
  if (video.readyState === 4 && currentTime - lastFrameTime >= frameInterval) {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const frameData = canvas.toDataURL("image/jpeg");
    console.log("Captured frame data:", frameData);
    try {
      const response = await fetch("/detect-emotion", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
        body: JSON.stringify({ frame: frameData }),
      });
      const result = await response.json();
      console.log("Backend response:", result);
      detectedEmotion = result.emotion;
      faceBox = result.face_box || null;
      if (faceBox) {
        console.log("Received face box:", faceBox);
        drawFaceOverlay();
      } else {
        console.log("No face box detected.");
        clearFaceOverlay();
      }
      recommendedPlaylistButton.disabled = !detectedEmotion;
    } catch (error) {
      console.error("Error detecting emotion:", error);
    }
    lastFrameTime = currentTime;
  }
  requestAnimationFrame(detectEmotionFromVideo);
}

// Image Upload for Emotion Detection
fileInput.addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const response = await fetch("/detect-emotion", {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
          body: JSON.stringify({ frame: e.target.result }),
        });
        const result = await response.json();
        detectedEmotion = result.emotion;
        if (detectedEmotion) {
          recommendedPlaylistButton.disabled = false;
          const redirectUrl = playlists[detectedEmotion];
          if (redirectUrl) window.location.href = redirectUrl;
        } else {
          alert("No emotion detected.");
        }
      } catch (error) {
        console.error("Error detecting emotion from image:", error);
      }
    };
    reader.readAsDataURL(file);
  }
});

// Playlist Redirection
const playlists = {
  happy: "/happy_playlist",
  sad: "/sad_playlist",
  angry: "/angry_playlist",
  neutral: "/neutral_playlist",
  fear: "/fear_playlist",
  surprise: "/surprise_playlist",
};

recommendedPlaylistButton.addEventListener("click", () => {
  if (detectedEmotion) {
    const redirectUrl = playlists[detectedEmotion];
    if (redirectUrl) window.location.href = redirectUrl;
    else alert("Emotion not recognized.");
  } else {
    alert("No emotion detected yet!");
  }
});

// Toggle Video
toggleVideoButton.addEventListener("click", () => {
  isVideoOn ? stopWebcam() : startWebcam();
});

// Initialize
startWebcam();
detectEmotionFromVideo();
