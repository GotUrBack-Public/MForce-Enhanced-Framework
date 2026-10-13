(() => {
  "use strict";
  const nav = document.getElementById("site-nav");
  const toggle = document.querySelector(".nav-toggle");
  if (nav && toggle) {
    const close = () => {
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    };
    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") !== "true";
      nav.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
    });
    nav.querySelectorAll("a").forEach(link => link.addEventListener("click", close));
    document.addEventListener("keydown", event => {
      if (event.key === "Escape") { close(); toggle.focus(); }
    });
    document.addEventListener("click", event => {
      if (!nav.contains(event.target) && !toggle.contains(event.target)) close();
    });
  }
  const year = document.getElementById("current-year");
  if (year) year.textContent = String(new Date().getFullYear());
})();
