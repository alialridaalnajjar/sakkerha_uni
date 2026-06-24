/* ════════════════════════════════════════════════════════
   Admin — Single Report Detail page
   Renders the mini Leaflet map for the report location.
   Status updates and deletion are plain HTML form posts —
   no AJAX, this script only handles the map display.
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