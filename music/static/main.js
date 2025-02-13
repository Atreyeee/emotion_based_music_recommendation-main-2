// HTML Elements
const video = document.getElementById("webcam");
const toggleVideoButton = document.getElementById("toggleVideo");
const cameraOffMessage = document.getElementById("cameraOffMessage");
const recommendedPlaylistButton = document.getElementById("recommendedPlaylist");
const fileInput = document.getElementById("imageUpload");

// State Variables
let isVideoOn = true;
let mediaStream = null;
let detectedEmotion = null; // Detected emotion
let faceBox = null; // Bounding box data for the detected face
const frameInterval = 500; // Interval to process a frame (ms)
let lastFrameTime = Date.now();

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
    .catch((err) => {
      console.error("Error accessing webcam:", err);
      alert("Please allow access to the webcam.");
    });
}

function stopWebcam() {
  console.log("Stopping webcam...");

  // Stop all media tracks (video, audio, etc.)
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;  // Clear the media stream reference
  }

  // Hide the video element
  video.style.display = "none";

  // Show the "camera off" message
  cameraOffMessage.style.display = "flex";

  // Reset the video status flag
  isVideoOn = false;

  // Update the button text to indicate the camera is off
  toggleVideoButton.textContent = "Turn Video On";

  // Clear any face overlays (canvas)
  clearFaceOverlay();

  console.log("Webcam stopped.");
}


// Overlay Canvas
const overlayCanvas = document.createElement("canvas");
const overlayCtx = overlayCanvas.getContext("2d");
overlayCanvas.style.position = "absolute";
overlayCanvas.style.top = "0";
overlayCanvas.style.left = "0";
overlayCanvas.style.zIndex = "10";
overlayCanvas.width = 640;
overlayCanvas.height = 480;
document.body.appendChild(overlayCanvas);

// Align overlay canvas with video dimensions
function alignCanvas() {
  const rect = video.getBoundingClientRect();
  overlayCanvas.style.width = `${rect.width}px`;
  overlayCanvas.style.height = `${rect.height}px`;
  overlayCanvas.style.top = `${rect.top}px`;
  overlayCanvas.style.left = `${rect.left}px`;
  // Log the canvas and video dimensions
  console.log("Video dimensions:", video.videoWidth, video.videoHeight);
  console.log("Canvas dimensions:", overlayCanvas.width, overlayCanvas.height);
}

window.addEventListener("resize", alignCanvas);
video.addEventListener("loadeddata", () => {
  alignCanvas();
});

// Draw Face and Emotion Overlay
function drawFaceOverlay() {
  overlayCtx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);

  if (faceBox && faceBox.x !== undefined && faceBox.y !== undefined && faceBox.width !== undefined && faceBox.height !== undefined) {
    const { x, y, width, height } = faceBox;
    console.log("Drawing face box at:", x, y, width, height); // Log the bounding box values

    // Draw pink bounding box
    overlayCtx.strokeStyle = "pink";
    overlayCtx.lineWidth = 3; // Thicker bounding box
    overlayCtx.strokeRect(x, y, width, height);

    // Draw black label with emotion text
    overlayCtx.font = "18px Arial";
    overlayCtx.fillStyle = "black";
    const labelX = x;
    const labelY = y - 10 > 0 ? y - 10 : y + 20;
    overlayCtx.fillText(detectedEmotion, labelX, labelY);
  } else {
    console.log("No valid face box data to draw");
  }
}

// Function to clear any face detection overlays (like bounding boxes on canvas)
function clearFaceOverlay() {
  const canvas = document.getElementById('overlayCanvas'); // Your canvas element
  if (canvas) {
    const ctx = canvas.getContext("2d");
    // Clear the entire canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    console.log("Face overlay cleared.");
  }
}
// Hand Gesture Recognition
const hands = new Hands({ locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}` });
hands.setOptions({
  maxNumHands: 2,
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5
});

async function recognizeGesture(frame) {
  const rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB);
  const results = hands.process(rgbFrame);

  if (results.multiHandLandmarks) {
    results.multiHandLandmarks.forEach(handLandmarks => {
      const wristY = handLandmarks[0].y;
      if (wristY > 0.5) {
        currentGesture = "Hand Up (Volume Up)";
      } else {
        currentGesture = "Hand Down (Volume Down)";
      }

      console.log("Detected Gesture:", currentGesture);

      hands.drawLandmarks(frame, handLandmarks, Hands.BOX_CONNECTIONS);
    });
  } else {
    currentGesture = "No hand detected";
    console.log("No hand detected");
  }

  return frame;
}

// Detect Emotion from Video
const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d");
canvas.width = 640;
canvas.height = 480;

async function detectEmotionFromVideo() {
  const currentTime = Date.now();
  if (isVideoOn && video.readyState === 4 && currentTime - lastFrameTime >= frameInterval) {
    // Draw the current video frame
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const frameData = canvas.toDataURL("image/jpeg");
    console.log("Captured frame data:", frameData.slice(0, 50) + "..."); // Log first 50 characters of frame data

    try {
      const response = await fetch("/detect-emotion", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ frame: frameData }),
      });

      const result = await response.json();
      console.log("Backend response:", result); // Log backend response to inspect structure

      detectedEmotion = result.emotion;
      faceBox = result.face_box;
      if (faceBox) {
        console.log("Received face box:", faceBox); // Log face box
      } else {
        console.log("No face box detected.");
      }

      drawFaceOverlay();
      await recognizeGesture(frame);
      // Enable playlist button if emotion is detected
      recommendedPlaylistButton.disabled = !detectedEmotion;

    } catch (error) {
      console.error("Error detecting emotion:", error);
      alert("Error detecting emotion. Please try again.");
    }

    lastFrameTime = currentTime;
  }

  requestAnimationFrame(detectEmotionFromVideo);
}

// Image Upload for Emotion Detection
fileInput.addEventListener("change", async (event) => {
  const file = event.target.files[0];
  console.log("File uploaded:", file); // Log the file being uploaded

  if (file) {
    const reader = new FileReader();
    reader.onload = async (e) => {
      const imageData = e.target.result;
      console.log("Image data (base64):", imageData.slice(0, 50) + "..."); // Log first 50 characters of image data

      try {
        const response = await fetch("/detect-emotion", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
          },
          body: JSON.stringify({ frame: imageData }),
        });

        const result = await response.json();
        console.log("Backend response for image:", result); // Log backend response for image

        detectedEmotion = result.emotion;

        if (detectedEmotion) {
          alert(`Detected Emotion: ${detectedEmotion}`);
          recommendedPlaylistButton.disabled = false;

          // Redirect to the playlist
          const playlists = {
            happy: "/happy_playlist",
            sad: "/sad_playlist",
            angry: "/angry_playlist",
            neutral: "/neutral_playlist",
            fear: "/fear_playlist",
            surprise: "/surprise_playlist",
          };

          const redirectUrl = playlists[detectedEmotion];
          if (redirectUrl) {
            console.log(`Redirecting to: ${redirectUrl}`); // Log redirect URL
            window.location.href = redirectUrl;
          }
        } else {
          alert("No emotion detected.");
        }
      } catch (error) {
        console.error("Error detecting emotion from image:", error);
        alert("Error detecting emotion. Please try again.");
      }
    };
    reader.readAsDataURL(file);
  }
});




// Playlist Redirection
recommendedPlaylistButton.addEventListener("click", () => {
  console.log("Playlist button clicked"); // Log button click
  if (detectedEmotion) {
    const playlists = {
      happy: "/happy_playlist",
      sad: "/sad_playlist",
      angry: "/angry_playlist",
      neutral: "/neutral_playlist",
      fear: "/fear_playlist",
      surprise: "/surprise_playlist",
    };

    const redirectUrl = playlists[detectedEmotion];
    if (redirectUrl) {
      console.log(`Redirecting to: ${redirectUrl}`); // Log redirect URL
      window.location.href = redirectUrl;
    } else {
      alert("Emotion not recognized. Please try again.");
    }
  } else {
    alert("No emotion detected yet!");
  }
});


// Toggle Video On/Off
toggleVideoButton.addEventListener("click", () => {
  if (isVideoOn) {
    stopWebcam();
  } else {
    startWebcam();
  }
});

// Initialize Webcam and Emotion Detection
console.log("Initializing webcam and emotion detection...");
startWebcam();
detectEmotionFromVideo();
