const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

if (!reducedMotion.matches && "IntersectionObserver" in window) {
  const sections = document.querySelectorAll(
    "main > .workday, .landing-features > .feature, " +
    "main > .deployment, main > .landing-demo, main > .module-overview > .shell, " +
    "main > .product-features, main > .product-faq > .shell, main > .product-cta, " +
    "main > .about-flow > .shell, main > .about-design, main > .about-invite > .shell"
  );

  const observer = new IntersectionObserver((entries) => {
    for (const { target, isIntersecting } of entries) {
      if (!isIntersecting) continue;
      observer.unobserve(target);
      if (reducedMotion.matches || target.matches(":focus-within")) continue;

      target.animate(
        [
          { opacity: 0.72, transform: "translateY(14px)" },
          { opacity: 1, transform: "translateY(0)" }
        ],
        { duration: 420, easing: "cubic-bezier(0.22, 1, 0.36, 1)" }
      );
    }
  }, { rootMargin: "0px 0px -45px 0px" });

  for (const section of sections) {
    if (section.getBoundingClientRect().top >= window.innerHeight) {
      observer.observe(section);
    }
  }
}
