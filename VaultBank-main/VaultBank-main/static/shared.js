/* ── VAULT BANK — SHARED JS ── */

// Custom cursor
(function initCursor() {
  const cursor = document.getElementById('vCursor');
  const ring   = document.getElementById('vRing');
  if (!cursor || !ring) return;
  let mx = 0, my = 0, rx = 0, ry = 0;
  document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; cursor.style.left = mx+'px'; cursor.style.top = my+'px'; });
  (function loop() {
    rx += (mx - rx) * 0.13; ry += (my - ry) * 0.13;
    ring.style.left = rx+'px'; ring.style.top = ry+'px';
    requestAnimationFrame(loop);
  })();
  const hoverTargets = 'button,a,.sidebar-link,.loan-type-card,.plan-card,.card-showcase,.nav-link,[onclick]';
  document.querySelectorAll(hoverTargets).forEach(el => {
    el.addEventListener('mouseenter', () => ring.classList.add('hover'));
    el.addEventListener('mouseleave', () => ring.classList.remove('hover'));
  });
})();

// Scroll progress
(function initScrollProgress() {
  const bar = document.getElementById('scrollProg');
  if (!bar) return;
  window.addEventListener('scroll', () => {
    const pct = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
    bar.style.width = Math.min(pct, 100) + '%';
  });
})();

// Count-up animation
function countUp(el, target, prefix='', suffix='', duration=1600) {
  if (!el) return;
  const start = performance.now();
  (function step(now) {
    const p = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    el.textContent = prefix + Math.round(target * ease).toLocaleString('en-IN') + suffix;
    if (p < 1) requestAnimationFrame(step);
  })(start);
}

// Sparkline chart builder
function buildSparkline(id, values, activeIndex) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = '';
  const max = Math.max(...values);
  values.forEach((v, i) => {
    const bar = document.createElement('div');
    bar.className = 'sparkline-bar' + (i === activeIndex ? ' active' : '');
    bar.style.height = Math.round((v / max) * 100) + '%';
    el.appendChild(bar);
  });
}

// EMI calculator
function calcEMI() {
  const P = parseInt(document.getElementById('amtSlider')?.value || 1000000);
  const r = parseFloat(document.getElementById('rateSlider')?.value || 10.5) / 100 / 12;
  const n = parseInt(document.getElementById('tenureSlider')?.value || 36);
  const emi   = P * r * Math.pow(1+r,n) / (Math.pow(1+r,n) - 1);
  const total = emi * n;
  const int   = total - P;
  const fmt = v => '₹' + Math.round(v).toLocaleString('en-IN');
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
  set('emiDisplay', fmt(emi));
  set('totalDisplay', fmt(total));
  set('interestDisplay', fmt(int));
  const lEl = document.getElementById('loanAmt');    if(lEl) lEl.textContent = fmt(P);
  const rEl = document.getElementById('rateDisplay'); if(rEl) rEl.textContent = parseFloat(document.getElementById('rateSlider').value).toFixed(1) + '%';
  const tEl = document.getElementById('tenureDisplay'); if(tEl) tEl.textContent = n + ' mo';
  // progress bar fill
  const pct = Math.min(Math.round((int / total) * 100), 100);
  const fill = document.getElementById('interestPctFill');
  if (fill) setTimeout(() => fill.style.width = pct + '%', 100);
}

// Dashboard date
(function setDate() {
  const el = document.getElementById('dashDate');
  if (!el) return;
  el.textContent = new Date().toLocaleDateString('en-IN', { weekday:'long', day:'numeric', month:'long', year:'numeric' });
})();

// Page nav (single-file mode)
function showPage(id, linkEl) {
  if (event) event.preventDefault();
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(a => a.classList.remove('active'));
  const pg = document.getElementById(id);
  if (pg) { pg.classList.add('active'); window.scrollTo(0,0); }
  if (linkEl) linkEl.classList.add('active');
  // re-run page inits
  setTimeout(() => {
    if (id === 'pg-dashboard') initDashboard();
    if (id === 'pg-loans')     calcEMI();
  }, 100);
}

function initDashboard() {
  countUp(document.getElementById('balAmt'), 284350, '₹');
  buildSparkline('spark1', [38,52,45,68,55,72,80,60,66,74,58,82], 11);
  buildSparkline('spark2', [50,55,48,65,70,68,75,80,72,84,78,88], 11);
}
