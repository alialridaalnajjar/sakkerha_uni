/* ════════════════════════════════════════════════════════
   Sakkerha — Map + Report Modal + Firebase Upload
   Depends on: Leaflet (CSS+JS), Firebase SDK (module, loaded
   via <script type="module"> in map.html)
   Globals injected by template:
     window.REPORTS_DATA  – array of public report objects
     window.IS_USER       – boolean
     window.SUBMIT_URL    – POST endpoint
════════════════════════════════════════════════════════ */

/* ── Wait for Firebase module to expose helpers ───────── */
document.addEventListener('DOMContentLoaded', () => {
  // Small delay ensures the map container is fully painted
  setTimeout(() => {
    initLeafletMap();
    if (window.IS_USER) initReportModal();
  }, 50);
});

/* ══════════════════════════════════════════════════════
   1. LEAFLET MAP
══════════════════════════════════════════════════════ */
let map, pinMarker;

function initLeafletMap() {
  // Default center: Beirut
  map = L.map('map', { zoomControl: true }).setView([33.8938, 35.5018], 13);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  }).addTo(map);

  // Plot existing public reports
  (window.REPORTS_DATA || []).forEach(addReportMarker);

  // Click to drop pin (users only)
  if (window.IS_USER) {
    map.on('click', onMapClick);
  }
}

function severityColor(sev) {
  return sev === 'high' ? '#d63a1d' : sev === 'medium' ? '#f0b562' : '#3b8a5a';
}
function statusColor(status) {
  return status === 'completed' ? '#1a1a1a' : '#3b8a5a';
}

function addReportMarker(r) {
  const color = severityColor(r.severity);
  const ring  = statusColor(r.status);

  const marker = L.circleMarker([r.lat, r.lng], {
    radius: 9, color: ring, weight: 3,
    fillColor: color, fillOpacity: 0.85,
  }).addTo(map);

  // Build popup HTML
  let imgsHtml = '';
  if (r.images && r.images.length) {
    imgsHtml = '<div class="map-popup-imgs">' +
      r.images.slice(0, 2).map(u =>
        `<img src="${u}" alt="Report image" loading="lazy" />`
      ).join('') +
      '</div>';
  }

  const popup = `
    <div class="map-popup">
      <div class="map-popup-top">
        <span class="badge sev-${r.severity || 'unknown'}">${(r.severity || '—').toUpperCase()}</span>
        <span class="badge status-${r.status}">${cap(r.status)}</span>
      </div>
      <h4>${escHtml(r.description)}</h4>
      <div class="popup-meta">${r.reporter} · ${r.created_at}</div>
      ${imgsHtml}
      <a href="/report/${r.id}" class="popup-link">View full report →</a>
    </div>`;

  marker.bindPopup(popup, { maxWidth: 280, minWidth: 200 });
}

function onMapClick(e) {
  const { lat, lng } = e.latlng;

  // Move / place pin marker
  if (pinMarker) {
    pinMarker.setLatLng([lat, lng]);
  } else {
    pinMarker = L.marker([lat, lng], {
      icon: L.divIcon({
        className: '',
        html: `<div style="
          width:20px;height:20px;border-radius:50%;
          background:var(--primary,#d63a1d);
          border:3px solid #fff;
          box-shadow:0 2px 8px rgba(0,0,0,0.3)">
        </div>`,
        iconSize: [20, 20], iconAnchor: [10, 10],
      }),
    }).addTo(map);
  }

  // Fill lat/lng into form fields
  const latD = document.getElementById('lat-display');
  const lngD = document.getElementById('lng-display');
  if (latD) latD.value = lat.toFixed(6);
  if (lngD) lngD.value = lng.toFixed(6);

  // Store for submission
  window._pickedLat = lat;
  window._pickedLng = lng;
}

/* ══════════════════════════════════════════════════════
   2. REPORT MODAL
══════════════════════════════════════════════════════ */
function initReportModal() {
  const overlay    = document.getElementById('report-modal');
  const openBtn    = document.getElementById('open-report-btn');
  const closeBtn   = document.getElementById('close-modal');
  const submitBtn  = document.getElementById('submit-report-btn');
  const anotherBtn = document.getElementById('submit-another-btn');
  const tabMap     = document.getElementById('tab-map');
  const tabManual  = document.getElementById('tab-manual');
  const secMap     = document.getElementById('loc-map-section');
  const secManual  = document.getElementById('loc-manual-section');
  const errBox     = document.getElementById('submit-error');
  const successEl  = document.getElementById('submit-success');
  const sevEl      = document.getElementById('success-severity');
  const useLocBtn  = document.getElementById('use-location-btn');

  if (!overlay) return;

  // Use current geolocation
  if (useLocBtn) {
    useLocBtn.addEventListener('click', () => {
      if (!navigator.geolocation) {
        return showErr('Geolocation is not supported by your browser.');
      }
      useLocBtn.disabled  = true;
      useLocBtn.innerHTML = '<span class="spinner"></span>Locating...';

      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = pos.coords.latitude;
          const lng = pos.coords.longitude;

          document.getElementById('lat-display').value = lat.toFixed(6);
          document.getElementById('lng-display').value = lng.toFixed(6);
          window._pickedLat = lat;
          window._pickedLng = lng;

          // Drop/move pin + recenter map
          if (pinMarker) {
            pinMarker.setLatLng([lat, lng]);
          } else {
            pinMarker = L.marker([lat, lng], {
              icon: L.divIcon({
                className: '',
                html: `<div style="width:20px;height:20px;border-radius:50%;background:#d63a1d;border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,0.3)"></div>`,
                iconSize: [20, 20], iconAnchor: [10, 10],
              }),
            }).addTo(map);
          }
          map.setView([lat, lng], 16);

          useLocBtn.disabled  = false;
          useLocBtn.innerHTML = '✓ Location set';
          setTimeout(() => {
            useLocBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline;vertical-align:-3px;margin-right:6px"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>Use My Current Location`;
          }, 2000);
        },
        (err) => {
          useLocBtn.disabled  = false;
          useLocBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline;vertical-align:-3px;margin-right:6px"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>Use My Current Location`;
          let msg = 'Could not get your location.';
          if (err.code === 1) msg = 'Location permission denied. Please allow access or set location manually.';
          if (err.code === 2) msg = 'Location unavailable. Try manual entry instead.';
          if (err.code === 3) msg = 'Location request timed out. Try again.';
          showErr(msg);
        },
        { enableHighAccuracy: true, timeout: 10000 }
      );
    });
  }

  // Open / close
  openBtn.addEventListener('click', () => openModal());
  closeBtn.addEventListener('click', closeModal);
  overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

  function openModal() {
    overlay.classList.add('active');
    overlay.setAttribute('aria-hidden', 'false');
    // Pre-fill coords if pin was dropped
    if (window._pickedLat !== undefined) {
      document.getElementById('lat-display').value = window._pickedLat.toFixed(6);
      document.getElementById('lng-display').value = window._pickedLng.toFixed(6);
    }
  }
  function closeModal() {
    overlay.classList.remove('active');
    overlay.setAttribute('aria-hidden', 'true');
  }

  // Location tabs
  tabMap.addEventListener('click', () => {
    tabMap.classList.add('active'); tabManual.classList.remove('active');
    secMap.style.display = 'block'; secManual.style.display = 'none';
  });
  tabManual.addEventListener('click', () => {
    tabManual.classList.add('active'); tabMap.classList.remove('active');
    secManual.style.display = 'block'; secMap.style.display = 'none';
  });

  // Image previews
  document.querySelectorAll('.img-input').forEach(inp => {
    inp.addEventListener('change', function () {
      const file    = this.files[0];
      const slot    = this.closest('.img-slot');
      const preview = slot.querySelector('.img-preview');
      const inner   = slot.querySelector('.img-slot-inner');
      if (!file) return;
      const reader  = new FileReader();
      reader.onload = e => {
        preview.src = e.target.result;
        preview.style.display = 'block';
        inner.style.display   = 'none';
        slot.classList.add('has-img');
      };
      reader.readAsDataURL(file);
    });
  });

    submitBtn.addEventListener('click', async () => {
    errBox.style.display    = 'none';
    successEl.style.display = 'none';

    // Gather coords
    let lat, lng;
    const isManual = tabManual.classList.contains('active');
    if (isManual) {
      lat = parseFloat(document.getElementById('lat-manual').value);
      lng = parseFloat(document.getElementById('lng-manual').value);
    } else {
      lat = window._pickedLat;
      lng = window._pickedLng;
    }

    const desc = document.getElementById('description').value.trim();

    // Validate
    if (!desc)                    return showErr('Description is required.');
    if (lat == null || isNaN(lat) || lng == null || isNaN(lng))
      return showErr('Please set a location — click the map or enter coordinates manually.');
    if (lat < -90  || lat > 90)   return showErr('Latitude must be between -90 and 90.');
    if (lng < -180 || lng > 180)  return showErr('Longitude must be between -180 and 180.');

    submitBtn.disabled  = true;
    submitBtn.innerHTML = '<span class="spinner"></span>Analysing with AI…';

    // Build multipart form — send files directly to Flask
    const body = new FormData();
    body.append('description', desc);
    body.append('latitude',    lat);
    body.append('longitude',   lng);

    const slots = document.querySelectorAll('.img-input');
    slots.forEach((inp, i) => {
      if (inp.files[0]) body.append(`image_${i + 1}`, inp.files[0]);
    });

    try {
      const res  = await fetch(window.SUBMIT_URL, { method: 'POST', body });
      const data = await res.json();
      if (data.ok) {
        submitBtn.style.display  = 'none';
        successEl.style.display  = 'block';
        if (data.invalid) {
          successEl.classList.add('invalid-result');
          sevEl.textContent = 'Report flagged as INVALID';
          sevEl.style.color = '#595959';
          document.querySelector('#submit-success div:last-of-type').textContent =
            data.ai_note || "This report doesn't appear to show a valid street issue and won't be reviewed by admins.";
        } else {
          successEl.classList.remove('invalid-result');
          sevEl.textContent = 'Severity: ' + (data.severity || '—').toUpperCase();
          sevEl.style.color = '';
          document.querySelector('#submit-success div:last-of-type').textContent =
            'Your report is now pending admin review.';
        }
        resetModal();
      } else {
        showErr(data.error || 'Submission failed. Try again.');
        submitBtn.disabled    = false;
        submitBtn.textContent = 'Submit Report';
      }
    } catch (e) {
      showErr('Network error. Please check your connection.');
      submitBtn.disabled    = false;
      submitBtn.textContent = 'Submit Report';
    }
  });

  // Submit another — reset form back to fresh state
  if (anotherBtn) {
    anotherBtn.addEventListener('click', () => {
      successEl.style.display  = 'none';
      submitBtn.style.display  = 'block';
      submitBtn.disabled       = false;
      submitBtn.textContent    = 'Submit Report';
      errBox.style.display     = 'none';
      // Reset location tabs back to map mode
      tabMap.classList.add('active');
      tabManual.classList.remove('active');
      secMap.style.display    = 'block';
      secManual.style.display = 'none';
    });
  }

  function showErr(msg) {
    errBox.textContent    = msg;
    errBox.style.display  = 'block';
  }

  function resetModal() {
    document.getElementById('description').value = '';
    document.querySelectorAll('.img-input').forEach(i => { i.value = ''; });
    document.querySelectorAll('.img-preview').forEach(p => { p.style.display = 'none'; p.src = ''; });
    document.querySelectorAll('.img-slot-inner').forEach(i => { i.style.display = 'flex'; });
    document.querySelectorAll('.img-slot').forEach(s => s.classList.remove('has-img'));
    document.getElementById('lat-display').value = '';
    document.getElementById('lng-display').value = '';
    document.getElementById('lat-manual').value  = '';
    document.getElementById('lng-manual').value  = '';
    if (pinMarker) { map.removeLayer(pinMarker); pinMarker = null; }
    window._pickedLat = undefined;
    window._pickedLng = undefined;
  }
}

/* ══════════════════════════════════════════════════════
   3. FIREBASE STORAGE UPLOAD
   Uses helpers exposed by the <script type="module">
   block in map.html
══════════════════════════════════════════════════════ */
async function uploadToFirebase(file) {
  // Wait for firebase helpers (set by module script)
  const storage   = window._fbStorage;
  const fbRef     = window._fbRef;
  const fbUpload  = window._fbUpload;
  const fbGetURL  = window._fbGetURL;

  if (!storage) throw new Error('Firebase storage not initialised.');

  const ext      = file.name.split('.').pop();
  const fileName = `reports/${Date.now()}_${Math.random().toString(36).slice(2)}.${ext}`;
  const fileRef  = fbRef(storage, fileName);
  const snap     = await fbUpload(fileRef, file);
  return await fbGetURL(snap.ref);
}

/* ══════════════════════════════════════════════════════
   4. HELPERS
══════════════════════════════════════════════════════ */
function cap(s) { return s ? s[0].toUpperCase() + s.slice(1) : s; }
function escHtml(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}