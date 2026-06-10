(function () {
  "use strict";

  if (window.__insuranceAiEmbedMounted) {
    return;
  }

  var script = document.currentScript;
  if (!script) {
    return;
  }

  window.__insuranceAiEmbedMounted = true;

  var siteId = script.dataset.siteId || "demo";
  var brand = script.dataset.brand || "InsuranceAI";
  var position = script.dataset.position === "left" ? "left" : "right";
  var buttonLabel = script.dataset.buttonLabel || "Life assistant";
  var baseUrl = script.dataset.baseUrl || new URL(script.src, window.location.href).origin;
  var widgetUrl = new URL("/widget", baseUrl);

  widgetUrl.searchParams.set("site_id", siteId);
  widgetUrl.searchParams.set("brand", brand);
  widgetUrl.searchParams.set("embedded", "1");

  var host = document.createElement("div");
  host.id = "insuranceai-embed";
  document.body.appendChild(host);

  var root = host.attachShadow({ mode: "open" });
  var wrapper = document.createElement("div");
  wrapper.className = "insuranceai-launcher insuranceai-launcher--" + position;

  wrapper.innerHTML = [
    '<button class="insuranceai-toggle" type="button" aria-expanded="false" aria-label="Open life insurance assistant">',
    '  <span class="insuranceai-toggle__icon" aria-hidden="true">',
    '    <svg viewBox="0 0 24 24" fill="none"><path d="M7 10.5h10M7 14h6M6.5 19l-3 1 1-3.5A8 8 0 1 1 12 20H8.5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "  </span>",
    '  <span class="insuranceai-toggle__text">' + escapeHtml(buttonLabel) + "</span>",
    "</button>",
    '<section class="insuranceai-panel" role="dialog" aria-label="' + escapeHtml(brand) + ' life insurance assistant" aria-hidden="true">',
    '  <button class="insuranceai-close" type="button" aria-label="Close life insurance assistant">',
    '    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
    "  </button>",
    '  <iframe class="insuranceai-frame" title="' + escapeHtml(brand) + ' life insurance assistant" loading="lazy" src="' + escapeHtml(widgetUrl.toString()) + '"></iframe>',
    "</section>",
  ].join("");

  var style = document.createElement("style");
  style.textContent = [
    ":host { all: initial; }",
    "*, *::before, *::after { box-sizing: border-box; }",
    ".insuranceai-launcher { position: fixed; bottom: 20px; z-index: 2147483000; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif; }",
    ".insuranceai-launcher--right { right: 20px; }",
    ".insuranceai-launcher--left { left: 20px; }",
    ".insuranceai-toggle { height: 52px; display: inline-flex; align-items: center; gap: 10px; border: 1px solid rgba(215,173,85,.38); border-radius: 8px; background: #111315; color: #f8f5ed; padding: 0 16px 0 12px; box-shadow: 0 16px 48px rgba(0,0,0,.36); cursor: pointer; transition: transform .18s ease, border-color .18s ease, background .18s ease; }",
    ".insuranceai-toggle:hover { transform: translateY(-2px); border-color: rgba(215,173,85,.72); background: #17191c; }",
    ".insuranceai-toggle:focus-visible, .insuranceai-close:focus-visible { outline: 2px solid #d7ad55; outline-offset: 3px; }",
    ".insuranceai-toggle__icon { width: 30px; height: 30px; display: grid; place-items: center; border-radius: 6px; background: #d7ad55; color: #111; }",
    ".insuranceai-toggle__icon svg { width: 19px; height: 19px; }",
    ".insuranceai-toggle__text { font-size: 13px; line-height: 1; font-weight: 650; letter-spacing: 0; white-space: nowrap; }",
    ".insuranceai-panel { position: absolute; bottom: 66px; width: min(420px, calc(100vw - 32px)); height: min(720px, calc(100dvh - 104px)); overflow: hidden; border: 1px solid rgba(215,173,85,.32); border-radius: 10px; background: #0b0d10; box-shadow: 0 28px 90px rgba(0,0,0,.52); opacity: 0; visibility: hidden; transform: translateY(12px) scale(.985); transform-origin: bottom right; transition: opacity .2s ease, transform .2s ease, visibility .2s ease; }",
    ".insuranceai-launcher--right .insuranceai-panel { right: 0; }",
    ".insuranceai-launcher--left .insuranceai-panel { left: 0; transform-origin: bottom left; }",
    ".insuranceai-launcher[data-open=\"true\"] .insuranceai-panel { opacity: 1; visibility: visible; transform: translateY(0) scale(1); }",
    ".insuranceai-launcher[data-open=\"true\"] .insuranceai-toggle { border-color: rgba(215,173,85,.72); }",
    ".insuranceai-close { position: absolute; top: 12px; right: 12px; z-index: 2; width: 34px; height: 34px; display: grid; place-items: center; border: 1px solid rgba(255,255,255,.1); border-radius: 6px; background: rgba(11,13,16,.92); color: rgba(255,255,255,.72); cursor: pointer; transition: color .18s ease, background .18s ease, border-color .18s ease; }",
    ".insuranceai-close:hover { color: #fff; background: #191c20; border-color: rgba(215,173,85,.38); }",
    ".insuranceai-close svg { width: 17px; height: 17px; }",
    ".insuranceai-frame { width: 100%; height: 100%; display: block; border: 0; background: #0b0d10; }",
    "@media (max-width: 640px) {",
    "  .insuranceai-launcher { right: 12px; bottom: 12px; left: auto; }",
    "  .insuranceai-panel, .insuranceai-launcher--left .insuranceai-panel, .insuranceai-launcher--right .insuranceai-panel { position: fixed; inset: 0; width: 100vw; height: 100dvh; border: 0; border-radius: 0; transform-origin: bottom center; }",
    "  .insuranceai-launcher[data-open=\"true\"] .insuranceai-toggle { opacity: 0; pointer-events: none; }",
    "  .insuranceai-close { top: 10px; right: 10px; }",
    "}",
    "@media (prefers-reduced-motion: reduce) { .insuranceai-toggle, .insuranceai-panel, .insuranceai-close { transition: none; } }",
  ].join("\n");

  root.appendChild(style);
  root.appendChild(wrapper);

  var toggle = wrapper.querySelector(".insuranceai-toggle");
  var close = wrapper.querySelector(".insuranceai-close");
  var panel = wrapper.querySelector(".insuranceai-panel");
  var previousBodyOverflow = "";

  function setOpen(open) {
    wrapper.dataset.open = open ? "true" : "false";
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "Close life insurance assistant" : "Open life insurance assistant");
    panel.setAttribute("aria-hidden", open ? "false" : "true");

    if (window.matchMedia("(max-width: 640px)").matches) {
      if (open) {
        previousBodyOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";
      } else {
        document.body.style.overflow = previousBodyOverflow;
      }
    }
  }

  toggle.addEventListener("click", function () {
    setOpen(wrapper.dataset.open !== "true");
  });

  close.addEventListener("click", function () {
    setOpen(false);
    toggle.focus();
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && wrapper.dataset.open === "true") {
      setOpen(false);
      toggle.focus();
    }
  });

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }
})();
