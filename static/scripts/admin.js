/* ════════════════════════════════════════════════════════
   Sakkerha — Admin: Status Update (AJAX)
   Used by: admin/dashboard.html + admin/report_detail.html
════════════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {
  // ── Dashboard table buttons ───────────────────────────
  document.querySelectorAll("[data-id][data-status]").forEach((btn) => {
    btn.dataset.origLabel = btn.textContent.trim();
    btn.addEventListener("click", () => {
      if (btn.disabled || btn.dataset.busy === "1") return;
      updateStatus(btn.dataset.id, btn.dataset.status, btn);
    });
  });

  // ── Detail page buttons (.status-btn) ────────────────
  document.querySelectorAll(".status-btn").forEach((btn) => {
    btn.dataset.origLabel = btn.textContent.trim();
    btn.addEventListener("click", () => {
      if (btn.disabled || btn.dataset.busy === "1") return;
      updateStatus(btn.dataset.id, btn.dataset.status, btn, true);
    });
  });
});

/* ── Core update function ──────────────────────────────── */
async function updateStatus(id, status, triggerEl, isDetailPage = false) {
  const errBox = document.getElementById("action-error");

  // Lock the button immediately — prevents double submission
  triggerEl.disabled = true;
  triggerEl.dataset.busy = "1";
  triggerEl.innerHTML = '<span class="spinner"></span>';

  try {
    const res = await fetch(`/admin/report/${id}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
    const data = await res.json();

    if (data.ok) {
      if (isDetailPage) {
        window.location.reload();
      } else {
        updateTableRow(id, data.new_status);
      }
      // Leave button disabled — row/page will reflect the new terminal/transition state
    } else {
      showErr(errBox, data.error || "Update failed.");
      triggerEl.disabled = false;
      triggerEl.dataset.busy = "0";
      triggerEl.textContent = triggerEl.dataset.origLabel || "Update";
    }
  } catch (e) {
    showErr(errBox, "Network error. Please try again.");
    triggerEl.disabled = false;
    triggerEl.dataset.busy = "0";
    triggerEl.textContent = triggerEl.dataset.origLabel || "Update";
  }
}

/* ── Update the table row without reload ──────────────── */
function updateTableRow(id, newStatus) {
  const row = document.querySelector(`tr[data-report-id="${id}"]`);
  if (!row) return;

  // Update status badge
  const statusCell = row.querySelector('.badge[class*="status-"]');
  if (statusCell) {
    statusCell.className = `badge status-${newStatus}`;
    statusCell.textContent = cap(newStatus);
  }

  // Replace action buttons with terminal state message
  const actionsCell = row.querySelector(".action-btns");
  if (actionsCell) {
    if (newStatus === "completed" || newStatus === "rejected") {
      actionsCell.innerHTML = `<span class="mono" style="font-size:11px;color:var(--muted)">${cap(newStatus)}</span>`;
    } else if (newStatus === "ongoing") {
      // Show complete + reject
      actionsCell.innerHTML = `
        <a href="/admin/report/${id}" class="btn-sm btn-outline">View</a>
        <button class="btn-sm btn-action"  data-id="${id}" data-status="completed">Complete</button>
        <button class="btn-sm btn-danger"  data-id="${id}" data-status="rejected">Reject</button>`;
      // Re-attach listeners on new buttons
      actionsCell.querySelectorAll("[data-id][data-status]").forEach((btn) => {
        btn.addEventListener("click", () => {
          if (
            !confirm(
              `Mark report #${btn.dataset.id} as "${statusLabel(btn.dataset.status)}"?`,
            )
          )
            return;
          updateStatus(btn.dataset.id, btn.dataset.status, btn);
        });
      });
    }
  }
}

/* ── Helpers ───────────────────────────────────────────── */
function statusLabel(s) {
  const map = {
    ongoing: "Ongoing",
    completed: "Completed",
    rejected: "Rejected",
  };
  return map[s] || cap(s);
}
function cap(s) {
  return s ? s[0].toUpperCase() + s.slice(1) : s;
}
function showErr(el, msg) {
  if (!el) {
    // Fallback inline banner instead of a native alert popup
    const banner = document.createElement("div");
    banner.className = "form-error";
    banner.style.position = "fixed";
    banner.style.top = "20px";
    banner.style.right = "20px";
    banner.style.zIndex = "9999";
    banner.style.maxWidth = "320px";
    banner.textContent = msg;
    document.body.appendChild(banner);
    setTimeout(() => banner.remove(), 4000);
    return;
  }
  el.textContent = msg;
  el.style.display = "block";
  setTimeout(() => {
    el.style.display = "none";
  }, 5000);
}



