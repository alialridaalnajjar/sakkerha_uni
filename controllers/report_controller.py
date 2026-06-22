import json, requests, uuid, base64
from flask import render_template, redirect, url_for, session, request, flash, jsonify, current_app
from werkzeug.utils import secure_filename
from models.report import Report
from models.builders.report_builder import ReportBuilder
from config import Config

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def _upload_to_firebase(file, folder="reports"):
    """Upload file to Firebase Storage server-side, return public download URL."""
    from urllib.parse import quote
    ext      = secure_filename(file.filename).rsplit(".", 1)[1].lower()
    filename = f"{folder}/{uuid.uuid4().hex}.{ext}"
    bucket   = Config.FIREBASE_STORAGE_BUCKET
    api_key  = Config.FIREBASE_API_KEY
    mime     = {"png":"image/png","gif":"image/gif","webp":"image/webp"}.get(ext,"image/jpeg")
    file_bytes = file.read()
    upload_url = (
        f"https://firebasestorage.googleapis.com/v0/b/{bucket}/o"
        f"?name={quote(filename)}&key={api_key}"
    )
    resp = requests.post(upload_url, data=file_bytes,
                         headers={"Content-Type": mime}, timeout=30)
    resp.raise_for_status()
    data    = resp.json()
    encoded = quote(filename, safe="")
    return (f"https://firebasestorage.googleapis.com/v0/b/{bucket}/o/"
            f"{encoded}?alt=media&token={data.get('downloadTokens','')}")

def save_image(file):
    """Upload image to Firebase Storage, return URL. Falls back to None on error."""
    if not file or file.filename == "":
        return None
    if not allowed_file(file.filename):
        return None
    try:
        return _upload_to_firebase(file, folder="reports")
    except Exception as e:
        print(f"[Firebase Upload Error] {e}")
        return None

# ── Map view ──────────────────────────────────────────────
def map_view():
    public_reports = Report.find_public()
    reports_json = json.dumps([{
        "id":          r.id,
        "lat":         float(r.latitude),
        "lng":         float(r.longitude),
        "description": r.description,
        "severity":    r.severity,
        "status":      r.status,
        "reporter":    r.reporter_name,
        "images":      r.images,
        "created_at":  r.created_at.strftime("%b %d, %Y") if r.created_at else "",
    } for r in public_reports])
    return render_template("reports/map.html", reports_json=reports_json)

# ── Submit report ─────────────────────────────────────────
def submit_report():
    user_id     = session.get("user_id")
    description = request.form.get("description", "").strip()
    latitude    = request.form.get("latitude",    "").strip()
    longitude   = request.form.get("longitude",   "").strip()

    # Save uploaded images to disk
    image_url_1 = save_image(request.files.get("image_1"))
    image_url_2 = save_image(request.files.get("image_2"))
    image_url_3 = save_image(request.files.get("image_3"))

    print(f"[Submit] image_1={image_url_1}")
    print(f"[Submit] image_2={image_url_2}")
    print(f"[Submit] image_3={image_url_3}")

    if not description:
        return jsonify({"ok": False, "error": "Description is required."}), 400
    try:
        lat = float(latitude)
        lng = float(longitude)
    except (ValueError, TypeError):
        return jsonify({"ok": False, "error": "Invalid coordinates."}), 400

    image_urls = [u for u in [image_url_1, image_url_2, image_url_3] if u]
    severity, ai_note = _assess_with_gemini(
        description=description, lat=lat, lng=lng, image_urls=image_urls
    )

    # Invalid reports are auto-flagged and excluded from the admin queue
    initial_status = "invalid" if severity == "invalid" else "pending"

    try:
        report = (ReportBuilder()
                  .set_user(user_id)
                  .set_description(description)
                  .set_location(lat, lng)
                  .set_images(image_url_1, image_url_2, image_url_3)
                  .set_ai_result(severity, ai_note)
                  .set_status(initial_status)
                  .build()
                  .save())
        return jsonify({
            "ok": True,
            "report_id": report.id,
            "severity": severity,
            "invalid": severity == "invalid",
            "ai_note": ai_note,
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ── Report detail ─────────────────────────────────────────
def delete_report(report_id):
    user_id = session.get("user_id")
    report  = Report.find_by_id(report_id)

    if not report:
        return jsonify({"ok": False, "error": "Report not found."}), 404
    if report.user_id != user_id:
        return jsonify({"ok": False, "error": "You can only delete your own reports."}), 403
    if report.status not in ("pending", "rejected", "invalid"):
        return jsonify({"ok": False, "error": "Only pending, rejected, or invalid reports can be deleted."}), 400

    Report.delete(report_id)
    return jsonify({"ok": True})


def report_detail(report_id):
    report = Report.find_by_id(report_id)
    if not report:
        flash("Report not found.", "error")
        return redirect(url_for("report.map_view"))
    return render_template("reports/detail.html", report=report)

# ── Gemini AI assessment ──────────────────────────────────
def _assess_with_gemini(description, lat, lng, image_urls):
    api_key = Config.GEMINI_API_KEY
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash:generateContent?key=" + api_key
    )

    prompt_text = f"""You are a strict civic infrastructure assessment AI for the Sakkerha platform in Lebanon.
A citizen has reported a street/infrastructure issue. Your job is to rate severity ACCURATELY, and detect invalid/fake/irrelevant reports.

Location: Latitude {lat}, Longitude {lng}
Citizen description: "{description}"

{"IMPORTANT: Carefully examine the attached images. The visual evidence is the PRIMARY factor in your rating." if image_urls else "No images provided — base rating on description only."}

STEP 1 — VALIDITY CHECK (most important):
Mark a report as "invalid" if ANY of these apply:
- The image shows something unrelated to street/infrastructure issues (e.g. a car, a person, a pet, food, a screenshot, random objects, memes).
- The coordinates fall in open water/sea, clearly outside any city/street area.
- The description is gibberish, spam, or makes no sense (e.g. random keyboard mashing).
- The image and description clearly contradict each other in a way suggesting a fake/joke report.
- There is no real civic infrastructure issue depicted or described at all.

If invalid, respond with severity "invalid" and explain why in the assessment.

STEP 2 — IF VALID, RATE SEVERITY:
- "low": Small debris, minor cracks, faded paint, small potholes under 10cm, cosmetic damage. If description says small/minor → LOW.
- "medium": Medium potholes 10-30cm, partial road damage, broken signage, moderate debris.
- "high": Large sinkholes, collapsed road, exposed wiring, deep potholes over 30cm, complete blockage, anything causing immediate injury risk.

RULES:
1. Do NOT default to medium. Analyze carefully.
2. Small debris on sidewalk = LOW always.
3. Giant hole/sinkhole = HIGH always.
4. Images are PRIMARY evidence — trust them over description.
5. Be strict about invalid detection — a picture of a car, a selfie, or an unrelated object is INVALID even if the description claims it's a road issue.

Respond ONLY with valid JSON, no markdown:
{{
  "severity": "low" | "medium" | "high" | "invalid",
  "assessment": "1-2 sentences explaining your rating or why it's invalid."
}}"""

    parts = [{"text": prompt_text}]

    print(f"[Gemini] Image URLs to process: {image_urls}")

    for img_url in image_urls[:3]:
        try:
            print(f"[Gemini] Fetching remote: {img_url}")
            img_resp  = requests.get(img_url, timeout=15)
            img_resp.raise_for_status()
            mime      = img_resp.headers.get("Content-Type", "image/jpeg").split(";")[0]
            img_bytes = img_resp.content
            print(f"[Gemini] Fetched {len(img_bytes)} bytes, mime={mime}")
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            parts.append({"inline_data": {"mime_type": mime, "data": b64}})
            print(f"[Gemini] Image added OK")
        except Exception as e:
            print(f"[Gemini] FAILED to fetch image {img_url}: {e}")

    print(f"[Gemini] Sending {len(parts)} parts ({len(parts)-1} images) to Gemini")

    try:
        resp = requests.post(url, json={"contents": [{"parts": parts}]}, timeout=30)
        resp.raise_for_status()
        raw  = resp.json()
        text = raw["candidates"][0]["content"]["parts"][0]["text"].strip()
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        severity = data.get("severity", "medium").lower()
        if severity not in ("low", "medium", "high", "invalid"):
            severity = "medium"
        print(f"[Gemini] Result: severity={severity}")
        return severity, data.get("assessment", "")
    except Exception as e:
        print(f"[Gemini] API Error: {e}")
        return "medium", "AI assessment unavailable. Defaulted to medium severity."