/* ════════════════════════════════════════════════════════
   User-facing report detail page — mini Leaflet map
   Reads window.REPORT_DATA (set inline by the template)
════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
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
});