(() => {
  const canvas = document.getElementById("starfield");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  let stars = [];
  const STAR_COUNT = 160;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function makeStar() {
    return {
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      z: Math.random() * 0.8 + 0.2, // depth: controls speed + size
    };
  }

  function init() {
    resize();
    stars = Array.from({ length: STAR_COUNT }, makeStar);
  }

  function tick() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#3dffa0";

    for (const star of stars) {
      star.x -= star.z * 0.4;
      if (star.x < 0) {
        star.x = canvas.width;
        star.y = Math.random() * canvas.height;
      }
      ctx.globalAlpha = star.z * 0.8;
      const size = star.z * 1.6;
      ctx.fillRect(star.x, star.y, size, size);
    }
    ctx.globalAlpha = 1;
    requestAnimationFrame(tick);
  }

  window.addEventListener("resize", resize);
  init();
  tick();
})();
