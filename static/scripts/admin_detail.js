/* ════════════════════════════════════════════════════════
   Admin — Single Report Detail page
   Reads report data from window.REPORT_DATA (set by template)
════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  initDetailMap();
  bindDeleteButton();
});

function initDetailMap() {
  const mapEl = document.getElementById('detail-map');
  if (!mapEl || typeof L === 'undefined' || !window.REPORT_DATA) return;

  const { lat, lng, id } = window.REPORT_DATA;

  const map = L.map('detail-map').setView([lat, lng], 16);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  L.circleMarker([lat, lng], {
    radius: 10,
    color: '#d63a1d',
    fillColor: '#d63a1d',
    fillOpacity: 0.85,
    weight: 2
  }).addTo(map).bindPopup(`Report #${id}`).openPopup();
}

function bindDeleteButton() {
  const delBtn = document.getElementById('delete-report-btn');
  if (!delBtn || !window.REPORT_DATA) return;

  delBtn.addEventListener('click', async () => {
    if (delBtn.disabled) return;
    if (!confirm('Permanently delete this report? This cannot be undone.')) return;

    delBtn.disabled  = true;
    delBtn.innerHTML = '<span class="spinner"></span>';

    try {
      const res  = await fetch(`/admin/report/${window.REPORT_DATA.id}/delete`, { method: 'POST' });
      const data = await res.json();

      if (data.ok) {
        window.location.href = window.REPORT_DATA.dashboardUrl;
      } else {
        alert(data.error || 'Delete failed.');
        delBtn.disabled    = false;
        delBtn.textContent = 'Delete Report Permanently';
      }
    } catch (e) {
      alert('Network error.');
      delBtn.disabled    = false;
      delBtn.textContent = 'Delete Report Permanently';
    }
  });
}