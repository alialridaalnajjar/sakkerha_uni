/* ════════════════════════════════════════════════════════
   Profile page — collapsible sections + delete actions
════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Collapsible: Edit Profile ─────────────────────────
  bindToggle('edit-toggle', 'edit-form');

  // ── Collapsible: Change Password ──────────────────────
  bindToggle('pw-toggle', 'pw-form');

  // ── Collapsible: Delete Account (danger zone) ─────────
  bindToggle('danger-toggle', 'danger-form');

  // ── Delete own report (pending/rejected/invalid only) ──
  document.querySelectorAll('.delete-my-report-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (btn.disabled) return;
      deleteMyReport(btn.dataset.id, btn);
    });
  });

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

/* ── Delete a user's own report via AJAX ───────────────── */
async function deleteMyReport(id, btn) {
  if (!confirm('Delete this report? This cannot be undone.')) return;

  btn.disabled  = true;
  btn.innerHTML = '...';

  try {
    const res  = await fetch(`/report/${id}/delete`, { method: 'POST' });
    const data = await res.json();

    if (data.ok) {
      const row = document.querySelector(`[data-report-id="${id}"]`);
      if (row) row.remove();
    } else {
      alert(data.error || 'Could not delete report.');
      btn.disabled  = false;
      btn.innerHTML = '&#x1F5D1;';
    }
  } catch (err) {
    alert('Network error.');
    btn.disabled  = false;
    btn.innerHTML = '&#x1F5D1;';
  }
}