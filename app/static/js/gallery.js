/* =================================================
   gallery.js — Lightbox, swipe, lazy loading
   Don Macaron Gallery  —  Phase 5/6
   ================================================= */

// ── Touch / Swipe support ─────────────────────────────────
let _touchStartX = 0;
let _touchStartY = 0;

document.addEventListener('touchstart', (e) => {
  _touchStartX = e.changedTouches[0].clientX;
  _touchStartY = e.changedTouches[0].clientY;
}, { passive: true });

document.addEventListener('touchend', (e) => {
  const lb = document.getElementById('lightbox');
  if (!lb || !lb.classList.contains('is-open')) return;

  const dx = _touchStartX - e.changedTouches[0].clientX;
  const dy = Math.abs(_touchStartY - e.changedTouches[0].clientY);

  // Only swipe horizontally (ignore vertical scrolls)
  if (Math.abs(dx) > 50 && dy < 80 && typeof lightboxNav === 'function') {
    lightboxNav(dx > 0 ? 1 : -1);
  }
}, { passive: true });


// ── IntersectionObserver lazy loading ────────────────────────
function initLazyFade() {
  if (!('IntersectionObserver' in window)) return;

  const obs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.05, rootMargin: '100px' });

  document.querySelectorAll('.lazy-item').forEach(el => obs.observe(el));
}


// ── Mobile nav toggle ─────────────────────────────────
function initNavToggle() {
  const toggle  = document.querySelector('.nav-toggle');
  const navList = document.querySelector('.nav-list');
  if (!toggle || !navList) return;
  toggle.addEventListener('click', () => {
    navList.classList.toggle('is-open');
  });
}


// ── Keyboard shortcut hint (show on ?) ────────────────────
document.addEventListener('keydown', (e) => {
  if (e.key === '?' || e.key === '/') {
    const lb = document.getElementById('lightbox');
    if (lb && lb.classList.contains('is-open')) return;
    // Could show a help overlay in the future
  }
});


// ── Init on DOM ready ──────────────────────────────────
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initLazyFade();
    initNavToggle();
  });
} else {
  initLazyFade();
  initNavToggle();
}
