const assistantVideo = document.querySelector(".assistant-video video");

if (assistantVideo) {
  const toggle = document.querySelector(".assistant-video-toggle");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const labels = { play: toggle.dataset.play, pause: toggle.dataset.pause };
  let pausedByUser = reduceMotion;

  function sync() {
    toggle.textContent = assistantVideo.paused ? labels.play : labels.pause;
  }

  toggle.addEventListener("click", () => {
    if (assistantVideo.paused) {
      pausedByUser = false;
      assistantVideo.play();
    } else {
      pausedByUser = true;
      assistantVideo.pause();
    }
  });

  assistantVideo.addEventListener("play", sync);
  assistantVideo.addEventListener("pause", sync);

  new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting && !pausedByUser) assistantVideo.play().catch(() => {});
    if (!entry.isIntersecting) assistantVideo.pause();
  }, { threshold: 0.4 }).observe(assistantVideo);

  sync();
  toggle.hidden = false;
}
