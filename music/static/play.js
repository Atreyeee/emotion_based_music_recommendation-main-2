let audioPlayer = document.getElementById("audio-player");
let isPlaying = false;
let currentSongIndex = -1;
let songs = [];

function playSong(title, artist, audioUrl, imageUrl, index) {
  if (index !== currentSongIndex) {
    songs.push({ title, artist, audioUrl, imageUrl });
    currentSongIndex = index;
  }

  document.getElementById("player-title").innerText = title;
  document.getElementById("player-artist").innerText = artist;
  document.getElementById("player-cover").src = imageUrl;

  audioPlayer.src = audioUrl;
  audioPlayer.play();

  const musicPlayer = document.getElementById("music-player");
  musicPlayer.style.display = "flex";

  isPlaying = true;
  document.getElementById("play-pause-btn").innerHTML = "&#10074;&#10074;"; // Pause symbol
}

function togglePlayPause() {
  if (isPlaying) {
    audioPlayer.pause();
    isPlaying = false;
    document.getElementById("play-pause-btn").innerHTML = "&#9654;"; // Play symbol
  } else {
    audioPlayer.play();
    isPlaying = true;
    document.getElementById("play-pause-btn").innerHTML = "&#10074;&#10074;"; // Pause symbol
  }
}

function updateProgress() {
  let currentTime = audioPlayer.currentTime;
  let duration = audioPlayer.duration;
  let progressBar = document.getElementById("progress-bar");
  let currentTimeElement = document.getElementById("current-time");
  let durationTimeElement = document.getElementById("duration-time");

  let progress = (currentTime / duration) * 100;
  progressBar.style.width = progress + "%";

  currentTimeElement.innerText = formatTime(currentTime);
  durationTimeElement.innerText = formatTime(duration);
}

function formatTime(time) {
  let minutes = Math.floor(time / 60);
  let seconds = Math.floor(time % 60);
  return (
    (minutes < 10 ? "0" : "") +
    minutes +
    ":" +
    (seconds < 10 ? "0" : "") +
    seconds
  );
}

function seek(event) {
  let progressBar = document.querySelector(".progress-container");
  let offsetX = event.offsetX;
  let width = progressBar.offsetWidth;
  let newTime = (offsetX / width) * audioPlayer.duration;
  audioPlayer.currentTime = newTime;
}

function nextSong() {
  if (currentSongIndex < songs.length - 1) {
    currentSongIndex++;
    let nextSong = songs[currentSongIndex];
    playSong(
      nextSong.title,
      nextSong.artist,
      nextSong.audioUrl,
      nextSong.imageUrl,
      currentSongIndex
    );
  }
}

function prevSong() {
  if (currentSongIndex > 0) {
    currentSongIndex--;
    let prevSong = songs[currentSongIndex];
    playSong(
      prevSong.title,
      prevSong.artist,
      prevSong.audioUrl,
      prevSong.imageUrl,
      currentSongIndex
    );
  }
}
