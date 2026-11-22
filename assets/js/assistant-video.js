(() => {
  const figures = document.querySelectorAll(".platform-video");
  if (!figures.length) return;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const tr = document.documentElement.lang.startsWith("tr");
  const label = { play: tr ? "Videoyu oynat" : "Play video", pause: tr ? "Videoyu duraklat" : "Pause video" };

  figures.forEach((figure) => {
    const video = figure.querySelector("video");
    const button = figure.querySelector(".platform-video-toggle");
    if (!video || !button) return;

    video.removeAttribute("controls");
    video.muted = true;
    button.hidden = false;
    let stoppedByUser = reduce;

    const sync = () => {
      const paused = video.paused;
      button.dataset.state = paused ? "paused" : "playing";
      button.setAttribute("aria-label", paused ? label.play : label.pause);
    };
    video.addEventListener("play", sync);
    video.addEventListener("pause", sync);
    sync();

    button.addEventListener("click", () => {
      if (video.paused) {
        stoppedByUser = false;
        video.play().catch(() => {});
      } else {
        stoppedByUser = true;
        video.pause();
      }
    });

    if (!("IntersectionObserver" in window)) return;
    new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !stoppedByUser) video.play().catch(() => {});
      else if (!entry.isIntersecting && !video.paused) video.pause();
    }, { threshold: 0.4 }).observe(video);
  });
})();
