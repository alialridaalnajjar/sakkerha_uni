(function () {
  const toggle = document.querySelector(".nav-toggle"),
    mobile = document.querySelector(".nav-mobile");
  if (!toggle || !mobile) return;
  toggle.addEventListener("click", function () {
    const open = mobile.classList.toggle("open");
    toggle.classList.toggle("open", open);
    toggle.setAttribute("aria-expanded", String(open));
  });
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".nav")) {
      mobile.classList.remove("open");
      toggle.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });
  window.addEventListener("resize", function () {
    if (window.innerWidth >= 768) {
      mobile.classList.remove("open");
      toggle.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });
})();
