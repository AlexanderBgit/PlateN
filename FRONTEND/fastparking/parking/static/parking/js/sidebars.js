function toggle_md(e) {
  const team_short = document.querySelector("#team_short");
  if (team_short) {
    team_short.classList.toggle("d-none");
  }
  const btn = document.querySelector("#btn_collapse .fa-solid.fa-angles-right");
  if (btn) {
    btn.classList.toggle("d-none");
  }
  const sidebar = document.querySelector(".sidebar");
  if (sidebar) {
    sidebar.classList.toggle("sidebar_mobile");
  }
  const nav_items = Array.from(document.querySelectorAll(".nav-item"));
  nav_items.forEach((nav_item) => {
    nav_item.classList.toggle("d-none");
  });
}

/* global bootstrap: false */
function init_tooltip() {
  "use strict";
  const tooltipTriggerList = Array.from(document.querySelectorAll('.sidebar [data-bs-toggle="tooltip"]'));
  tooltipTriggerList.forEach((tooltipTriggerEl) => {
    const child_span = tooltipTriggerEl?.querySelector("span");
    const displayValue = child_span ? window.getComputedStyle(child_span)?.getPropertyValue("display") : "none";
    const tooltip = bootstrap.Tooltip.getInstance(tooltipTriggerEl);
    if (tooltip) {
      tooltip.dispose();
    }
    if (displayValue == "none") {
      new bootstrap.Tooltip(tooltipTriggerEl);
      console.log(tooltipTriggerEl);
    }
  });
}

function init_tooltip_const() {
  "use strict";
  const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]:not(.sidebar)'));
  tooltipTriggerList.forEach((tooltipTriggerEl) => {
    const tooltip = bootstrap.Tooltip.getInstance(tooltipTriggerEl);
    if (tooltip) {
      tooltip.dispose();
    }
    new bootstrap.Tooltip(tooltipTriggerEl);
  });
}
