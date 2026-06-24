/* ════════════════════════════════════════════════════════
   Profile page — collapsible section toggles only.
   All data-changing actions (edit, delete, password change)
   are plain HTML form submissions — no AJAX here.
════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  bindToggle('edit-toggle', 'edit-form');
  bindToggle('pw-toggle', 'pw-form');
  bindToggle('danger-toggle', 'danger-form');
});

/* ── Generic collapsible section toggle ────────────────── */
function bindToggle(toggleId, formId) {
  const toggle = document.getElementById(toggleId);
  const form   = document.getElementById(formId);
  if (!toggle || !form) return;

  toggle.addEventListener('click', () => {
    form.classList.toggle('open');
    const arrow = toggle.querySelector('.toggle-arrow');
    if (arrow) {
      arrow.textContent = form.classList.contains('open') ? '▴' : '▾';
    }
  });
}