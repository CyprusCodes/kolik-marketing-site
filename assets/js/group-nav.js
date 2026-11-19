const groupNav = document.querySelector(".group-nav");
const siteHeader = document.querySelector(".site-header");

if (groupNav && siteHeader) {
  const stick = () => { groupNav.style.top = `${siteHeader.offsetHeight}px`; };
  stick();
  window.addEventListener("resize", stick);
}

if (groupNav && "IntersectionObserver" in window) {
  const links = new Map(
    [...groupNav.querySelectorAll('a[href^="#"]')].map((link) => [link.hash.slice(1), link])
  );

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        links.forEach((link) => link.removeAttribute("aria-current"));
        const link = links.get(entry.target.id);
        if (!link) return;
        link.setAttribute("aria-current", "true");
        link.scrollIntoView({ block: "nearest", inline: "nearest" });
      });
    },
    { rootMargin: "-45% 0px -50% 0px" }
  );

  links.forEach((_, id) => {
    const section = document.getElementById(id);
    if (section) observer.observe(section);
  });
}
