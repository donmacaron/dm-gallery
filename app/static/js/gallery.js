/* =================================================
   gallery.js — Lightbox, swipe, lazy loading
   Don Macaron Gallery
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
  if (Math.abs(dx) > 50 && dy < 80 && typeof lightboxNav === 'function') {
    lightboxNav(dx > 0 ? 1 : -1);
  }
}, { passive: true });


// ── Mobile nav burger toggle ─────────────────────────────
function initNavToggle() {
  const toggle  = document.querySelector('.nav-toggle');
  const navList = document.querySelector('.nav-list');
  if (!toggle || !navList) return;

  // Single authoritative click handler — NO inline onclick on the button
  toggle.addEventListener('click', function(e) {
    e.stopPropagation();
    navList.classList.toggle('is-open');
    // Update aria
    const open = navList.classList.contains('is-open');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  // Close menu when clicking outside
  document.addEventListener('click', function(e) {
    if (!toggle.contains(e.target) && !navList.contains(e.target)) {
      navList.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });

  // Close menu when a nav link is clicked (mobile UX)
  navList.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
      navList.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });
}


// ── IntersectionObserver lazy fade-in ───────────────────────
function initLazyFade() {
  if (!('IntersectionObserver' in window)) {
    // Fallback: just make all visible immediately
    document.querySelectorAll('.lazy-item').forEach(el => el.classList.add('visible'));
    return;
  }
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


// ── Init ────────────────────────────────────────────────
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => { initNavToggle(); initLazyFade(); });
} else {
  initNavToggle(); initLazyFade();
}
