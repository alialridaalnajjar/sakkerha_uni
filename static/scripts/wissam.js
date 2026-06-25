
(function () {
  const HINTS = [
    "Tip: click the map to drop a pin and file a report!",
    "Use 'My Current Location' for faster reporting.",
    "Up to 3 photos help our AI judge severity better.",
    "Pending reports can be deleted from your profile.",
    "High severity reports get prioritized by admins.",
    "You can track your report's status anytime.",
    "Small debris? Mark it low — every report counts!",
    "Lost your password? Use the reset link on login.",
  ];

  let scene, camera, renderer, headGroup, container;
  let bobT = 0;
  let dismissed = false;

  function init() {
    container = document.getElementById("wissam-container");
    if (!container || typeof THREE === "undefined") return;

    const w = 140,
      h = 160;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(35, w / h, 0.1, 100);
    camera.position.set(0, 0.3, 5.2);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(w, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // ── Lighting (flat, simple) ───────────────────────────
    const ambient = new THREE.AmbientLight(0xffffff, 0.75);
    scene.add(ambient);
    const dir = new THREE.DirectionalLight(0xffffff, 0.6);
    dir.position.set(2, 3, 4);
    scene.add(dir);

    // ── Build Wissam ───────────────────────────────────────
    headGroup = new THREE.Group();

    const skinColor = 0xf0b562;
    const shirtColor = 0xd63a1d;

    // Shoulders / torso (flattened sphere)
    const shoulderGeo = new THREE.SphereGeometry(1.3, 16, 12);
    shoulderGeo.scale(1, 0.55, 0.85);
    const shoulderMat = new THREE.MeshLambertMaterial({
      color: shirtColor,
      flatShading: true,
    });
    const shoulders = new THREE.Mesh(shoulderGeo, shoulderMat);
    shoulders.position.y = -1.05;
    headGroup.add(shoulders);

    // Neck
    const neckGeo = new THREE.CylinderGeometry(0.32, 0.36, 0.35, 10);
    const neckMat = new THREE.MeshLambertMaterial({
      color: skinColor,
      flatShading: true,
    });
    const neck = new THREE.Mesh(neckGeo, neckMat);
    neck.position.y = -0.55;
    headGroup.add(neck);

    // Head (low-poly sphere)
    const headGeo = new THREE.SphereGeometry(0.85, 14, 12);
    const headMat = new THREE.MeshLambertMaterial({
      color: skinColor,
      flatShading: true,
    });
    const head = new THREE.Mesh(headGeo, headMat);
    head.position.y = 0.25;
    headGroup.add(head);

    // Hair (simple dark cap, top half sphere)
    const hairGeo = new THREE.SphereGeometry(
      0.88,
      14,
      12,
      0,
      Math.PI * 2,
      0,
      Math.PI * 0.55,
    );
    const hairMat = new THREE.MeshLambertMaterial({
      color: 0x2b2118,
      flatShading: true,
    });
    const hair = new THREE.Mesh(hairGeo, hairMat);
    hair.position.y = 0.45;
    headGroup.add(hair);

    // Eyes (small dark spheres)
    const eyeGeo = new THREE.SphereGeometry(0.08, 8, 8);
    const eyeMat = new THREE.MeshLambertMaterial({
      color: 0x1a1a1a,
      flatShading: true,
    });
    const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
    eyeL.position.set(-0.3, 0.28, 0.72);
    const eyeR = eyeL.clone();
    eyeR.position.x = 0.3;
    headGroup.add(eyeL, eyeR);

    // Mouth (small flattened box, slight smile)
    const mouthGeo = new THREE.BoxGeometry(0.34, 0.06, 0.05);
    const mouthMat = new THREE.MeshLambertMaterial({
      color: 0x8a4a3a,
      flatShading: true,
    });
    const mouth = new THREE.Mesh(mouthGeo, mouthMat);
    mouth.position.set(0, -0.02, 0.82);
    mouth.rotation.z = 0.0;
    headGroup.add(mouth);

    // Ears (small spheres)
    const earGeo = new THREE.SphereGeometry(0.14, 8, 8);
    const earMat = headMat;
    const earL = new THREE.Mesh(earGeo, earMat);
    earL.position.set(-0.82, 0.22, 0.05);
    const earR = earL.clone();
    earR.position.x = 0.82;
    headGroup.add(earL, earR);

    headGroup.position.y = 0.35;
    scene.add(headGroup);

    animate();
  }

  function animate() {
    if (dismissed) return;
    requestAnimationFrame(animate);
    bobT += 0.02;
    headGroup.position.y = 0.35 + Math.sin(bobT) * 0.06;
    headGroup.rotation.y = Math.sin(bobT * 0.5) * 0.15;
    renderer.render(scene, camera);
  }

  function showHint() {
    const bubble = document.getElementById("wissam-bubble");
    if (!bubble) return;
    const hint = HINTS[Math.floor(Math.random() * HINTS.length)];
    bubble.textContent = hint;
    bubble.classList.add("show");
    clearTimeout(bubble._hideTimer);
    bubble._hideTimer = setTimeout(() => bubble.classList.remove("show"), 5000);
  }

  function dismissWissam() {
    dismissed = true;
    const wrap = document.getElementById("wissam-wrap");
    if (wrap) wrap.style.display = "none";
    try {
      sessionStorage.setItem("wissam_dismissed", "1");
    } catch (e) {}
  }

  document.addEventListener("DOMContentLoaded", () => {
    let alreadyDismissed = false;
    try {
      alreadyDismissed = sessionStorage.getItem("wissam_dismissed") === "1";
    } catch (e) {}

    if (alreadyDismissed) {
      const wrap = document.getElementById("wissam-wrap");
      if (wrap) wrap.style.display = "none";
      return;
    }

    init();

    const clickTarget = document.getElementById("wissam-container");
    if (clickTarget) clickTarget.addEventListener("click", showHint);

    const closeBtn = document.getElementById("wissam-close");
    if (closeBtn)
      closeBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        dismissWissam();
      });

    // Greet after a short delay
    setTimeout(showHint, 1200);
  });
})();
