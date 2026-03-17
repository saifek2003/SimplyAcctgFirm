from flask import Flask, request, jsonify, render_template_string, session, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "saf-simply-accounting-2024-secret"

DB = "appointments.db"
BUSINESS = "SimplyAccountingFirm"
OWNER_PASSWORD = "Lance*@1994"
OWNER_PHONE = "863-738-9105"

SERVICES = ["Tax Consultation", "Bookkeeping Review",
            "Payroll Setup", "Business Audit", "Financial Planning"]

# Mon-Fri: 5 PM – 8 PM
WEEKDAY_HOURS = ["5:00 PM", "6:00 PM", "7:00 PM", "8:00 PM"]
# Sat-Sun: 9 AM – 6 PM
WEEKEND_HOURS = ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
                 "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM", "6:00 PM"]

# ─────────────────────────── MAIN APP HTML ───────────────────────────
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>SimplyAccountingFirm</title>
<style>
  :root {
    --gold: #B8902A;
    --gold-light: #D4A93A;
    --gold-dark: #8A6A18;
    --gold-bg: #FBF6EC;
    --black: #111111;
    --text: #1A1A1A;
    --text-muted: #6B5E45;
    --border: #E8DFC8;
    --card-bg: #FFFFFF;
    --page-bg: #F9F6F1;
    --input-bg: #FAFAF8;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: var(--page-bg); color: var(--text); min-height: 100vh; }

  /* HEADER */
  header { background: var(--black); padding: 26px 16px 22px; text-align: center; }
  .logo-diamond { display: inline-block; width: 42px; height: 42px; background: var(--gold);
                  transform: rotate(45deg); margin-bottom: 14px; }
  .logo-inner { display: inline-block; width: 22px; height: 22px; background: var(--black);
                transform: rotate(45deg); position: absolute; top: 10px; left: 10px; }
  .logo-wrap { position: relative; width: 42px; height: 42px; margin: 0 auto 12px; }
  header h1 { font-size: 1.5rem; font-weight: 900; color: #FFFFFF; letter-spacing: 0.3px; }
  header h1 span { color: var(--gold); }
  header p { font-size: 0.78rem; color: #999; margin-top: 5px; letter-spacing: 1.5px; text-transform: uppercase; }

  /* NAV TABS */
  .tabs { display: flex; background: #FFFFFF; border-bottom: 2px solid var(--border);
          overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .tabs::-webkit-scrollbar { display: none; }
  .tab { flex: 1; min-width: 72px; padding: 13px 6px 11px; text-align: center;
         font-size: 0.72rem; font-weight: 700; color: #999; cursor: pointer;
         transition: all 0.2s; white-space: nowrap; letter-spacing: 0.3px;
         text-transform: uppercase; border-bottom: 3px solid transparent; }
  .tab.active { color: var(--gold); border-bottom: 3px solid var(--gold); }
  .tab:hover:not(.active) { color: var(--text); background: var(--gold-bg); }

  /* SECTIONS */
  .section { display: none; padding: 20px 16px 40px; max-width: 500px; margin: 0 auto; }
  .section.active { display: block; }

  /* CARDS */
  .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px;
          padding: 20px; margin-bottom: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
  .card-title { font-size: 0.95rem; font-weight: 800; color: var(--black);
                margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
  .card-title .icon { color: var(--gold); }

  /* DASHBOARD HERO */
  .hero { background: var(--black); border-radius: 18px; padding: 28px 20px;
          text-align: center; margin-bottom: 16px; }
  .hero h2 { font-size: 1.4rem; font-weight: 900; color: #FFFFFF; margin-bottom: 6px; }
  .hero h2 span { color: var(--gold); }
  .hero p { color: #AAA; font-size: 0.88rem; line-height: 1.6; margin-bottom: 20px; }
  .hero-btn { display: inline-block; background: var(--gold); color: var(--black);
              font-weight: 800; font-size: 0.95rem; padding: 14px 32px;
              border-radius: 50px; border: none; cursor: pointer; transition: all 0.2s; }
  .hero-btn:hover { background: var(--gold-light); }

  /* STAT PILLS */
  .stat-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
  .stat-pill { background: var(--card-bg); border: 1px solid var(--border); border-radius: 14px;
               padding: 16px 14px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
  .stat-num { font-size: 1.6rem; font-weight: 900; color: var(--gold); }
  .stat-label { font-size: 0.75rem; color: var(--text-muted); margin-top: 3px; font-weight: 600;
                text-transform: uppercase; letter-spacing: 0.4px; }

  /* SERVICE LIST ON DASHBOARD */
  .service-list { list-style: none; }
  .service-list li { display: flex; align-items: center; gap: 10px; padding: 10px 0;
                     border-bottom: 1px solid var(--border); font-size: 0.9rem; color: var(--text); }
  .service-list li:last-child { border-bottom: none; }
  .service-list li::before { content: '◆'; color: var(--gold); font-size: 0.6rem; flex-shrink: 0; }

  /* HOURS TABLE */
  .hours-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
  .hours-table tr { border-bottom: 1px solid var(--border); }
  .hours-table tr:last-child { border-bottom: none; }
  .hours-table td { padding: 9px 4px; color: var(--text); }
  .hours-table td:last-child { text-align: right; color: var(--gold); font-weight: 700; }
  .hours-table .weekend { color: var(--text-muted); }

  /* STEPS */
  .steps { display: flex; align-items: center; justify-content: center; margin-bottom: 22px; gap: 6px; }
  .step { width: 30px; height: 30px; border-radius: 50%; border: 2px solid var(--border);
          display: flex; align-items: center; justify-content: center;
          font-size: 0.75rem; font-weight: 800; color: #BBB; transition: all 0.3s; }
  .step.active { border-color: var(--gold); color: var(--gold); background: var(--gold-bg); }
  .step.done { border-color: var(--gold); background: var(--gold); color: #FFF; }
  .step-line { flex: 1; height: 2px; background: var(--border); max-width: 40px; transition: all 0.3s; }
  .step-line.done { background: var(--gold); }

  /* FIELDS */
  .field { margin-bottom: 16px; }
  label { display: block; font-size: 0.75rem; font-weight: 800; color: var(--text-muted);
          margin-bottom: 7px; text-transform: uppercase; letter-spacing: 0.7px; }
  input, select { width: 100%; padding: 14px 12px; border: 1.5px solid var(--border);
                  border-radius: 10px; font-size: 1rem; background: var(--input-bg);
                  color: var(--text); transition: border-color 0.2s; -webkit-appearance: none; }
  input::placeholder { color: #CCC; }
  input:focus, select:focus { outline: none; border-color: var(--gold);
                               box-shadow: 0 0 0 3px rgba(184,144,42,0.1); background: #FFF; }

  /* SERVICE GRID */
  .service-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .service-btn { padding: 14px 10px; background: var(--input-bg); border: 2px solid var(--border);
                 border-radius: 12px; color: var(--text-muted); font-size: 0.82rem;
                 font-weight: 700; cursor: pointer; text-align: center; transition: all 0.2s; line-height: 1.3; }
  .service-btn:hover { border-color: var(--gold-light); color: var(--text); }
  .service-btn.selected { border-color: var(--gold); color: var(--gold); background: var(--gold-bg); }

  /* TIME GRID */
  .time-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
  .time-grid.wide { grid-template-columns: repeat(4, 1fr); }
  .time-btn { padding: 14px 4px; background: var(--input-bg); border: 2px solid var(--border);
              border-radius: 10px; color: var(--text-muted); font-size: 0.85rem;
              font-weight: 700; cursor: pointer; text-align: center; transition: all 0.2s; }
  .time-btn:hover { border-color: var(--gold-light); color: var(--text); }
  .time-btn.selected { border-color: var(--gold); color: var(--gold); background: var(--gold-bg); }
  .time-btn.taken { opacity: 0.35; cursor: not-allowed; text-decoration: line-through; }
  .hours-note { font-size: 0.78rem; color: var(--text-muted); background: var(--gold-bg);
                border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px; margin-bottom: 12px; }

  /* BUTTONS */
  .btn { width: 100%; padding: 16px; background: var(--gold); color: var(--black); border: none;
         border-radius: 12px; font-size: 1rem; font-weight: 800; cursor: pointer;
         transition: all 0.2s; margin-top: 6px; letter-spacing: 0.2px; }
  .btn:hover { background: var(--gold-light); }
  .btn:active { transform: scale(0.98); }
  .btn-outline { background: transparent; border: 2px solid var(--gold); color: var(--gold); font-weight: 700; }
  .btn-outline:hover { background: var(--gold-bg); }
  .btn-sm { padding: 10px 16px; font-size: 0.85rem; width: auto; }

  /* SUMMARY */
  .summary { background: var(--gold-bg); border: 1.5px solid var(--border);
             border-radius: 14px; padding: 18px; margin-bottom: 16px; }
  .summary-row { display: flex; justify-content: space-between; align-items: center;
                 padding: 7px 0; border-bottom: 1px solid var(--border); font-size: 0.9rem; }
  .summary-row:last-child { border-bottom: none; }
  .summary-label { color: var(--text-muted); font-size: 0.8rem; font-weight: 700; text-transform: uppercase; }
  .summary-value { color: var(--text); font-weight: 700; text-align: right; max-width: 60%; }

  /* APPOINTMENT CARDS */
  .appt-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 14px;
               padding: 16px; margin-bottom: 12px; border-left: 4px solid var(--gold);
               box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
  .appt-name { font-weight: 800; font-size: 1rem; color: var(--black); }
  .appt-service { font-size: 0.8rem; color: var(--gold); font-weight: 700;
                  background: var(--gold-bg); padding: 3px 10px; border-radius: 20px;
                  display: inline-block; margin: 6px 0; border: 1px solid var(--border); }
  .appt-time-row { display: flex; gap: 16px; margin-top: 6px; flex-wrap: wrap; }
  .appt-time-item { font-size: 0.84rem; color: var(--text-muted); font-weight: 600; }

  /* SEARCH BOX */
  .search-box { background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px;
                padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
  .search-box p { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 14px; line-height: 1.6; }

  /* CONTACT */
  .contact-hero { background: var(--black); border-radius: 18px; padding: 28px 20px;
                  text-align: center; margin-bottom: 16px; }
  .contact-hero p { color: #999; font-size: 0.85rem; margin-top: 6px; letter-spacing: 1px;
                    text-transform: uppercase; }
  .contact-phone { font-size: 2rem; font-weight: 900; color: var(--gold); margin: 10px 0; letter-spacing: 1px; }
  .call-btn { display: inline-block; background: var(--gold); color: var(--black);
              font-weight: 800; font-size: 1rem; padding: 14px 36px; border-radius: 50px;
              text-decoration: none; margin-top: 8px; transition: all 0.2s; }
  .call-btn:hover { background: var(--gold-light); }
  .contact-row { display: flex; align-items: center; gap: 14px; padding: 14px 0;
                 border-bottom: 1px solid var(--border); }
  .contact-row:last-child { border-bottom: none; }
  .contact-icon { width: 40px; height: 40px; background: var(--gold-bg); border: 1px solid var(--border);
                  border-radius: 10px; display: flex; align-items: center; justify-content: center;
                  font-size: 1.2rem; flex-shrink: 0; }
  .contact-label { font-size: 0.75rem; font-weight: 800; color: var(--text-muted);
                   text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
  .contact-value { font-size: 0.95rem; font-weight: 700; color: var(--black); }
  .contact-value a { color: var(--gold); text-decoration: none; }

  /* TOAST */
  .toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
           background: var(--black); border: 1px solid var(--gold); color: #FFF;
           padding: 14px 22px; border-radius: 12px; font-size: 0.9rem; display: none;
           z-index: 999; text-align: center; min-width: 260px; max-width: 90vw;
           box-shadow: 0 4px 20px rgba(0,0,0,0.2); font-weight: 600; }
  .toast.error { border-color: #e74c3c; }

  /* MISC */
  .empty { text-align: center; padding: 48px 16px; }
  .empty-icon { font-size: 3rem; margin-bottom: 12px; }
  .empty p { color: var(--text-muted); font-size: 0.95rem; }
  .confirm-icon { text-align: center; font-size: 3.5rem; margin-bottom: 10px; }
  .confirm-title { text-align: center; font-size: 1.2rem; font-weight: 900; color: var(--black); margin-bottom: 4px; }
  .confirm-sub { text-align: center; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 20px; }
  .divider { height: 1px; background: var(--border); margin: 14px 0; }
  .hidden { display: none !important; }
  .section-label { font-size: 0.72rem; font-weight: 800; color: var(--text-muted);
                   text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
  footer { text-align: center; padding: 20px 16px 36px; }
  footer a { color: #CCC; font-size: 0.72rem; text-decoration: none; letter-spacing: 0.5px; }
  footer a:hover { color: var(--gold); }
</style>
</head>
<body>

<header>
  <div class="logo-wrap">
    <div class="logo-diamond"></div>
    <div class="logo-inner"></div>
  </div>
  <h1>Simply<span>Accounting</span>Firm</h1>
  <p>Professional Accounting Services</p>
</header>

<div class="tabs">
  <div class="tab active" onclick="showTab('home')">&#127968; Home</div>
  <div class="tab" onclick="showTab('book')">&#128197; Book</div>
  <div class="tab" onclick="showTab('appointments')">&#128203; My Appts</div>
  <div class="tab" onclick="showTab('contact')">&#128222; Contact</div>
</div>

<!-- ===== HOME / DASHBOARD TAB ===== -->
<div id="home" class="section active">
  <div class="hero">
    <h2>Welcome to <span>Simply</span>AccountingFirm</h2>
    <p>Professional accounting services tailored for individuals and businesses. Book your appointment today.</p>
    <button class="hero-btn" onclick="showTab('book'); syncTabs('book')">Book an Appointment</button>
  </div>

  <div class="stat-row">
    <div class="stat-pill">
      <div class="stat-num" id="dash-total">—</div>
      <div class="stat-label">Total Bookings</div>
    </div>
    <div class="stat-pill">
      <div class="stat-num">5</div>
      <div class="stat-label">Services</div>
    </div>
  </div>

  <div class="card">
    <div class="card-title"><span class="icon">◆</span> Our Services</div>
    <ul class="service-list">
      {% for s in services %}
      <li>{{ s }}</li>
      {% endfor %}
    </ul>
  </div>

  <div class="card">
    <div class="card-title"><span class="icon">◆</span> Business Hours</div>
    <table class="hours-table">
      <tr><td>Monday – Friday</td><td>5:00 PM – 8:00 PM</td></tr>
      <tr class="weekend"><td>Saturday</td><td>9:00 AM – 6:00 PM</td></tr>
      <tr class="weekend"><td>Sunday</td><td>9:00 AM – 6:00 PM</td></tr>
    </table>
  </div>

  <div class="card">
    <div class="card-title"><span class="icon">◆</span> Contact Us</div>
    <div class="contact-row">
      <div class="contact-icon">&#128222;</div>
      <div>
        <div class="contact-label">Phone</div>
        <div class="contact-value"><a href="tel:{{ owner_phone }}">{{ owner_phone }}</a></div>
      </div>
    </div>
  </div>
</div>

<!-- ===== BOOK TAB ===== -->
<div id="book" class="section">
  <div class="steps">
    <div class="step active" id="s1">1</div>
    <div class="step-line" id="l1"></div>
    <div class="step" id="s2">2</div>
    <div class="step-line" id="l2"></div>
    <div class="step" id="s3">3</div>
    <div class="step-line" id="l3"></div>
    <div class="step" id="s4">4</div>
  </div>

  <div id="step1">
    <div class="card">
      <div class="card-title"><span class="icon">◆</span> Your Information</div>
      <div class="field">
        <label>Full Name</label>
        <input id="name" type="text" placeholder="e.g. Jane Smith" autocomplete="name">
      </div>
      <div class="field">
        <label>Phone Number</label>
        <input id="phone" type="tel" placeholder="e.g. (555) 123-4567" autocomplete="tel">
      </div>
      <button class="btn" onclick="goStep(2)">Continue &#8594;</button>
    </div>
  </div>

  <div id="step2" class="hidden">
    <div class="card">
      <div class="card-title"><span class="icon">◆</span> Select a Service</div>
      <div class="service-grid">
        {% for s in services %}
        <div class="service-btn" onclick="selectService(this, '{{ s }}')">{{ s }}</div>
        {% endfor %}
      </div>
    </div>
    <button class="btn btn-outline" onclick="goStep(1)">&#8592; Back</button>
  </div>

  <div id="step3" class="hidden">
    <div class="card">
      <div class="card-title"><span class="icon">◆</span> Pick a Date</div>
      <div class="field" style="margin-bottom:0;">
        <input id="date" type="date" onchange="loadTimes()">
      </div>
    </div>
    <div class="card" id="time-card" style="display:none;">
      <div class="card-title"><span class="icon">◆</span> Available Times</div>
      <div class="hours-note" id="hours-note"></div>
      <div class="time-grid" id="time-grid"></div>
    </div>
    <button class="btn btn-outline" onclick="goStep(2)" style="margin-bottom:10px;">&#8592; Back</button>
  </div>

  <div id="step4" class="hidden">
    <div class="card">
      <div class="confirm-icon">&#9989;</div>
      <div class="confirm-title">Confirm Appointment</div>
      <div class="confirm-sub">Please review your details below</div>
      <div class="summary" id="summary"></div>
      <button class="btn" onclick="bookAppointment()">Confirm Booking</button>
      <button class="btn btn-outline" onclick="goStep(3)" style="margin-top:10px;">&#8592; Back</button>
    </div>
  </div>
</div>

<!-- ===== MY APPOINTMENTS TAB ===== -->
<div id="appointments" class="section">
  <div class="search-box">
    <p>Enter the phone number you used when booking to view your appointments.</p>
    <div class="field" style="margin-bottom:10px;">
      <input id="search-phone" type="tel" placeholder="Your phone number">
    </div>
    <button class="btn" onclick="loadAppointments()">Find My Appointments</button>
  </div>
  <div id="appt-list"></div>
</div>

<!-- ===== CONTACT TAB ===== -->
<div id="contact" class="section">
  <div class="contact-hero">
    <p>Get in touch with us</p>
    <div class="contact-phone">{{ owner_phone }}</div>
    <a class="call-btn" href="tel:{{ owner_phone }}">&#128222; Call Now</a>
  </div>

  <div class="card">
    <div class="card-title"><span class="icon">◆</span> Contact Information</div>
    <div class="contact-row">
      <div class="contact-icon">&#128222;</div>
      <div>
        <div class="contact-label">Phone</div>
        <div class="contact-value"><a href="tel:{{ owner_phone }}">{{ owner_phone }}</a></div>
      </div>
    </div>
    <div class="contact-row">
      <div class="contact-icon">&#128337;</div>
      <div>
        <div class="contact-label">Weekday Hours</div>
        <div class="contact-value">Mon – Fri &nbsp; 5:00 PM – 8:00 PM</div>
      </div>
    </div>
    <div class="contact-row">
      <div class="contact-icon">&#128336;</div>
      <div>
        <div class="contact-label">Weekend Hours</div>
        <div class="contact-value">Sat – Sun &nbsp; 9:00 AM – 6:00 PM</div>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="card-title"><span class="icon">◆</span> Have a Question?</div>
    <p style="font-size:0.88rem; color:var(--text-muted); line-height:1.7; margin-bottom:14px;">
      For questions about our services, pricing, or to schedule a consultation, give us a call. We're happy to help!
    </p>
    <a class="btn" href="tel:{{ owner_phone }}" style="display:block; text-align:center; text-decoration:none;">
      &#128222; &nbsp; Call {{ owner_phone }}
    </a>
  </div>
</div>

<footer>
  <a href="/owner">Owner Access</a>
</footer>

<div class="toast" id="toast"></div>

<script>
const WEEKDAY_HOURS = {{ weekday_hours|tojson }};
const WEEKEND_HOURS = {{ weekend_hours|tojson }};
let selectedService = '', selectedTime = '', currentStep = 1;

// ── TAB SWITCHING ──
function syncTabs(name) {
  document.querySelectorAll('.tab').forEach((t, i) => {
    t.classList.toggle('active', ['home','book','appointments','contact'][i] === name);
  });
  document.querySelectorAll('.section').forEach(s => {
    s.classList.toggle('active', s.id === name);
  });
}
function showTab(name) {
  syncTabs(name);
  window.scrollTo(0, 0);
}

// ── TOAST ──
function toast(msg, type = 'success') {
  const el = document.getElementById('toast');
  el.textContent = msg; el.className = 'toast ' + type;
  el.style.display = 'block';
  setTimeout(() => el.style.display = 'none', 3200);
}

// ── STEP NAVIGATION ──
function goStep(n) {
  if (n === 2) {
    const name = document.getElementById('name').value.trim();
    const phone = document.getElementById('phone').value.trim();
    if (!name || !phone) { toast('Please fill in your name and phone number.', 'error'); return; }
  }
  if (n === 3 && !selectedService) { toast('Please select a service.', 'error'); return; }
  if (n === 4) {
    if (!document.getElementById('date').value) { toast('Please select a date.', 'error'); return; }
    if (!selectedTime) { toast('Please select a time.', 'error'); return; }
    buildSummary();
  }
  for (let i = 1; i <= 4; i++) {
    document.getElementById('step' + i).classList.toggle('hidden', i !== n);
    const el = document.getElementById('s' + i);
    if (i < n) { el.classList.remove('active'); el.classList.add('done'); el.textContent = '✓'; }
    else if (i === n) { el.classList.add('active'); el.classList.remove('done'); el.textContent = i; }
    else { el.classList.remove('active','done'); el.textContent = i; }
    if (i < 4) document.getElementById('l' + i).classList.toggle('done', i < n);
  }
  currentStep = n;
  window.scrollTo(0, 0);
}

// ── SERVICE SELECTION ──
function selectService(el, name) {
  document.querySelectorAll('.service-btn').forEach(b => b.classList.remove('selected'));
  el.classList.add('selected');
  selectedService = name;
  setTimeout(() => goStep(3), 180);
}

// ── LOAD TIMES ──
async function loadTimes() {
  const date = document.getElementById('date').value;
  if (!date) return;
  selectedTime = '';
  const dow = new Date(date + 'T12:00:00').getDay();
  const isWeekend = dow === 0 || dow === 6;
  const hours = isWeekend ? WEEKEND_HOURS : WEEKDAY_HOURS;
  document.getElementById('hours-note').textContent = isWeekend
    ? 'Weekend hours: 9:00 AM – 6:00 PM'
    : 'Weekday hours: 5:00 PM – 8:00 PM';
  const res = await fetch('/taken?date=' + encodeURIComponent(date));
  const taken = await res.json();
  const grid = document.getElementById('time-grid');
  grid.className = 'time-grid' + (isWeekend ? ' wide' : '');
  grid.innerHTML = hours.map(h => {
    const isTaken = taken.includes(h);
    return `<div class="time-btn${isTaken ? ' taken' : ''}" ${isTaken ? '' : `onclick="selectTime(this,'${h}')"`}>${h}</div>`;
  }).join('');
  document.getElementById('time-card').style.display = 'block';
}

// ── SELECT TIME ──
function selectTime(el, t) {
  document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('selected'));
  el.classList.add('selected');
  selectedTime = t;
  setTimeout(() => goStep(4), 180);
}

// ── BUILD SUMMARY ──
function buildSummary() {
  const name = document.getElementById('name').value.trim();
  const phone = document.getElementById('phone').value.trim();
  const date = document.getElementById('date').value;
  const rows = [
    ['Name', name], ['Phone', phone], ['Service', selectedService],
    ['Date', new Date(date + 'T12:00:00').toLocaleDateString('en-US',
      {weekday:'long', year:'numeric', month:'long', day:'numeric'})],
    ['Time', selectedTime]
  ];
  document.getElementById('summary').innerHTML = rows.map(([l, v]) =>
    `<div class="summary-row"><span class="summary-label">${l}</span><span class="summary-value">${v}</span></div>`
  ).join('');
}

// ── BOOK ──
async function bookAppointment() {
  const name = document.getElementById('name').value.trim();
  const phone = document.getElementById('phone').value.trim();
  const date = document.getElementById('date').value;
  const res = await fetch('/book', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name, phone, service: selectedService, date, time: selectedTime})
  });
  const data = await res.json();
  if (data.success) {
    toast('Appointment confirmed!');
    ['name','phone','date'].forEach(id => document.getElementById(id).value = '');
    document.getElementById('time-card').style.display = 'none';
    selectedService = ''; selectedTime = '';
    document.querySelectorAll('.service-btn').forEach(b => b.classList.remove('selected'));
    goStep(1);
    loadDashStats();
  } else {
    toast(data.error || 'That slot was just taken. Please choose another.', 'error');
    goStep(3);
  }
}

// ── MY APPOINTMENTS ──
async function loadAppointments() {
  const phone = document.getElementById('search-phone').value.trim();
  if (!phone) { toast('Enter your phone number.', 'error'); return; }
  const res = await fetch('/appointments?phone=' + encodeURIComponent(phone));
  const data = await res.json();
  const list = document.getElementById('appt-list');
  if (!data.length) {
    list.innerHTML = `<div class="empty"><div class="empty-icon">&#128197;</div><p>No appointments found for this number.</p></div>`;
    return;
  }
  list.innerHTML = data.map(a => {
    const dateStr = new Date(a.date + 'T12:00:00').toLocaleDateString('en-US',
      {weekday:'short', month:'short', day:'numeric', year:'numeric'});
    return `
    <div class="appt-card">
      <div class="appt-name">${a.name}</div>
      <div class="appt-service">${a.service}</div>
      <div class="appt-time-row">
        <div class="appt-time-item">&#128197; ${dateStr}</div>
        <div class="appt-time-item">&#128336; ${a.time}</div>
      </div>
    </div>`;
  }).join('');
}

// ── DASHBOARD STATS ──
async function loadDashStats() {
  try {
    const res = await fetch('/stats');
    const data = await res.json();
    document.getElementById('dash-total').textContent = data.total;
  } catch(e) {}
}

document.getElementById('date').min = new Date().toISOString().split('T')[0];
loadDashStats();
</script>
</body>
</html>
"""

# ─────────────────────────── OWNER / ADMIN HTML ───────────────────────────
OWNER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>Owner Dashboard – SimplyAccountingFirm</title>
<style>
  :root {
    --gold: #B8902A; --gold-light: #D4A93A; --gold-dark: #8A6A18;
    --gold-bg: #FBF6EC; --black: #111111; --text: #1A1A1A; --text-muted: #6B5E45;
    --border: #E8DFC8; --card-bg: #FFFFFF; --page-bg: #F9F6F1; --input-bg: #FAFAF8;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: var(--page-bg); color: var(--text); min-height: 100vh; }
  header { background: var(--black); padding: 20px 16px; text-align: center; }
  header h1 { font-size: 1.2rem; font-weight: 900; color: #FFFFFF; }
  header h1 span { color: var(--gold); }
  header p { font-size: 0.78rem; color: #999; margin-top: 4px; letter-spacing: 1px; }
  .container { padding: 20px 16px 40px; max-width: 520px; margin: 0 auto; }
  .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px;
          padding: 22px; margin-bottom: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
  .card-title { font-size: 0.95rem; font-weight: 800; color: var(--black); margin-bottom: 16px; }
  .field { margin-bottom: 16px; }
  label { display: block; font-size: 0.75rem; font-weight: 800; color: var(--text-muted);
          margin-bottom: 7px; text-transform: uppercase; letter-spacing: 0.7px; }
  input { width: 100%; padding: 14px 12px; border: 1.5px solid var(--border);
          border-radius: 10px; font-size: 1rem; background: var(--input-bg); color: var(--text); }
  input:focus { outline: none; border-color: var(--gold); }
  input::placeholder { color: #CCC; }
  .btn { width: 100%; padding: 15px; background: var(--gold); color: var(--black); border: none;
         border-radius: 12px; font-size: 1rem; font-weight: 800; cursor: pointer; }
  .btn:hover { background: var(--gold-light); }
  .btn-danger { background: transparent; border: 2px solid #c0392b; color: #c0392b;
                font-weight: 700; padding: 9px 14px; font-size: 0.82rem; width: auto;
                border-radius: 8px; cursor: pointer; transition: all 0.2s; }
  .btn-danger:hover { background: rgba(192,57,43,0.08); }
  .btn-logout { background: transparent; border: 2px solid var(--border); color: var(--text-muted);
                font-size: 0.85rem; padding: 10px 16px; width: auto; border-radius: 8px;
                cursor: pointer; margin-bottom: 16px; }
  .btn-logout:hover { border-color: var(--text-muted); }
  .appt-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px;
               padding: 14px; margin-bottom: 10px; border-left: 4px solid var(--gold);
               box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
  .appt-name { font-weight: 800; font-size: 0.95rem; color: var(--black); }
  .appt-meta { font-size: 0.82rem; color: var(--text-muted); margin-top: 3px; }
  .appt-service { font-size: 0.78rem; color: var(--gold); font-weight: 700;
                  background: var(--gold-bg); padding: 3px 9px; border-radius: 20px;
                  display: inline-block; margin: 6px 0; border: 1px solid var(--border); }
  .appt-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
  .appt-time { font-size: 0.82rem; color: var(--text-muted); font-weight: 600; }
  .error-msg { background: #FDF0EE; border: 1px solid #e8a89e; border-radius: 10px;
               padding: 12px 14px; font-size: 0.9rem; color: #c0392b; margin-bottom: 14px; }
  .filter-row { display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }
  .filter-btn { padding: 8px 14px; border-radius: 20px; border: 1.5px solid var(--border);
                background: var(--input-bg); color: var(--text-muted); font-size: 0.78rem;
                font-weight: 700; cursor: pointer; transition: all 0.2s; text-transform: uppercase; }
  .filter-btn.active { border-color: var(--gold); color: var(--gold); background: var(--gold-bg); }
  .empty { text-align: center; padding: 40px 16px; color: var(--text-muted); font-size: 0.9rem; }
  .divider { height: 1px; background: var(--border); margin: 8px 0 10px; }
  .back-link { display: inline-block; color: var(--text-muted); font-size: 0.82rem;
               text-decoration: none; margin-top: 8px; }
  .back-link:hover { color: var(--gold); }
  .stat-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 14px; }
  .stat-pill { background: var(--card-bg); border: 1px solid var(--border); border-radius: 14px;
               padding: 14px 10px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
  .stat-num { font-size: 1.5rem; font-weight: 900; color: var(--gold); }
  .stat-label { font-size: 0.68rem; color: var(--text-muted); margin-top: 3px; font-weight: 700;
                text-transform: uppercase; letter-spacing: 0.3px; }
</style>
</head>
<body>
<header>
  <h1>Simply<span>Accounting</span>Firm</h1>
  <p>Owner Dashboard</p>
</header>

<div class="container">
{% if not logged_in %}
<div class="card">
  <div class="card-title">&#128274; Owner Login</div>
  {% if error %}<div class="error-msg">{{ error }}</div>{% endif %}
  <form method="POST" action="/owner/login">
    <div class="field">
      <label>Password</label>
      <input type="password" name="password" placeholder="Enter owner password" autofocus>
    </div>
    <button type="submit" class="btn">Login</button>
  </form>
</div>
<a href="/" class="back-link">&#8592; Back to App</a>

{% else %}
<button class="btn-logout" onclick="location.href='/owner/logout'">&#128274; Log Out</button>

<div class="stat-row">
  <div class="stat-pill">
    <div class="stat-num">{{ appointments|length }}</div>
    <div class="stat-label">Total</div>
  </div>
  <div class="stat-pill">
    <div class="stat-num" id="today-count">—</div>
    <div class="stat-label">Today</div>
  </div>
  <div class="stat-pill">
    <div class="stat-num" id="upcoming-count">—</div>
    <div class="stat-label">Upcoming</div>
  </div>
</div>

<div class="card">
  <div class="card-title">&#128203; All Appointments</div>
  <div class="filter-row">
    <div class="filter-btn active" onclick="filterAppts('all', this)">All</div>
    <div class="filter-btn" onclick="filterAppts('upcoming', this)">Upcoming</div>
    <div class="filter-btn" onclick="filterAppts('today', this)">Today</div>
  </div>
  <div id="admin-list">
    {% if appointments %}
      {% for a in appointments %}
      <div class="appt-card" data-date="{{ a.date }}">
        <div class="appt-name">{{ a.name }}</div>
        <div class="appt-meta">&#128222; {{ a.phone }}</div>
        <div class="appt-service">{{ a.service }}</div>
        <div class="divider"></div>
        <div class="appt-footer">
          <div class="appt-time">&#128197; {{ a.date }} &nbsp; &#128336; {{ a.time }}</div>
          <button class="btn-danger" onclick="cancelAppt({{ a.id }}, this)">Cancel</button>
        </div>
      </div>
      {% endfor %}
    {% else %}
      <div class="empty">No appointments yet.</div>
    {% endif %}
  </div>
</div>
<a href="/" class="back-link">&#8592; Back to App</a>
{% endif %}
</div>

<script>
const today = new Date().toISOString().split('T')[0];

function filterAppts(type, el) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  document.querySelectorAll('.appt-card').forEach(card => {
    const d = card.dataset.date;
    if (type === 'all') card.style.display = '';
    else if (type === 'today') card.style.display = d === today ? '' : 'none';
    else if (type === 'upcoming') card.style.display = d >= today ? '' : 'none';
  });
}

async function cancelAppt(id, btn) {
  if (!confirm('Cancel this appointment?')) return;
  const res = await fetch('/cancel/' + id, {method: 'DELETE'});
  const data = await res.json();
  if (data.success) {
    const card = btn.closest('.appt-card');
    card.style.opacity = '0'; card.style.transition = 'opacity 0.3s';
    setTimeout(() => { card.remove(); updateCounts(); }, 300);
  } else alert('Could not cancel. Try again.');
}

function updateCounts() {
  const cards = document.querySelectorAll('.appt-card');
  let todayN = 0, upN = 0;
  cards.forEach(c => {
    const d = c.dataset.date;
    if (d === today) todayN++;
    if (d >= today) upN++;
  });
  document.getElementById('today-count').textContent = todayN;
  document.getElementById('upcoming-count').textContent = upN;
}
updateCounts();
</script>
</body>
</html>
"""

# ─────────────────────────── DB ───────────────────────────


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                service TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)


def valid_time_for_date(date_str, time_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return False
    dow = d.weekday()  # 0=Mon…4=Fri, 5=Sat, 6=Sun
    return time_str in (WEEKDAY_HOURS if dow < 5 else WEEKEND_HOURS)

# ─────────────────────────── ROUTES ───────────────────────────


@app.route("/")
def index():
    return render_template_string(HTML, services=SERVICES,
                                  weekday_hours=WEEKDAY_HOURS,
                                  weekend_hours=WEEKEND_HOURS,
                                  owner_phone=OWNER_PHONE)


@app.route("/book", methods=["POST"])
def book():
    data = request.json
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    service = data.get("service", "").strip()
    date = data.get("date", "").strip()
    time = data.get("time", "").strip()
    if not all([name, phone, service, date, time]):
        return jsonify({"success": False, "error": "All fields are required."})
    if service not in SERVICES:
        return jsonify({"success": False, "error": "Invalid service."})
    if not valid_time_for_date(date, time):
        return jsonify({"success": False, "error": "That time is not available on the selected day."})
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM appointments WHERE date=? AND time=?", (date, time)
        ).fetchone()
        if existing:
            return jsonify({"success": False, "error": "That time slot is already booked."})
        conn.execute(
            "INSERT INTO appointments (name, phone, service, date, time) VALUES (?,?,?,?,?)",
            (name, phone, service, date, time)
        )
    return jsonify({"success": True})


@app.route("/taken")
def taken():
    date = request.args.get("date", "").strip()
    with get_db() as conn:
        rows = conn.execute(
            "SELECT time FROM appointments WHERE date=?", (date,)).fetchall()
    return jsonify([r["time"] for r in rows])


@app.route("/appointments")
def appointments():
    phone = request.args.get("phone", "").strip()
    if not phone:
        return jsonify([])
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, name, phone, service, date, time FROM appointments WHERE phone=? ORDER BY date, time",
            (phone,)
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/stats")
def stats():
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    return jsonify({"total": total})


@app.route("/cancel/<int:appt_id>", methods=["DELETE"])
def cancel(appt_id):
    if not session.get("owner"):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    with get_db() as conn:
        conn.execute("DELETE FROM appointments WHERE id=?", (appt_id,))
    return jsonify({"success": True})


@app.route("/owner")
def owner():
    if session.get("owner"):
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM appointments ORDER BY date, time").fetchall()
        return render_template_string(OWNER_HTML, logged_in=True,
                                      appointments=[dict(r) for r in rows], error=None)
    return render_template_string(OWNER_HTML, logged_in=False, appointments=[], error=None)


@app.route("/owner/login", methods=["POST"])
def owner_login():
    if request.form.get("password", "") == OWNER_PASSWORD:
        session["owner"] = True
        return redirect("/owner")
    return render_template_string(OWNER_HTML, logged_in=False, appointments=[],
                                  error="Incorrect password.")


@app.route("/owner/logout")
def owner_logout():
    session.pop("owner", None)
    return redirect("/owner")


if __name__ == "__main__":
    init_db()
    print(f"\n{'='*44}")
    print(f"  {BUSINESS}")
    print(f"  App:    http://localhost:5000")
    print(f"  Owner:  http://localhost:5000/owner")
    print(f"  Owner password: {OWNER_PASSWORD}")
    print(f"{'='*44}\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
# okay nice
