/* Dog Grooming USA — landing page behaviour. No dependencies. */
(function () {
  'use strict';

  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- year ---------- */
  var year = $('#year');
  if (year) year.textContent = new Date().getFullYear();

  /* ---------- header state ---------- */
  var header = $('#siteHeader');
  var onScroll = function () {
    if (header) header.classList.toggle('stuck', window.scrollY > 8);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---------- mobile nav ---------- */
  var burger = $('#burger');
  var nav    = $('#primaryNav');
  var scrim  = $('#navScrim');

  function setNav(open) {
    if (!burger || !nav) return;
    nav.classList.toggle('open', open);
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.classList.toggle('nav-open', open);
    if (scrim) scrim.hidden = !open;
  }

  if (burger) {
    burger.addEventListener('click', function () {
      setNav(burger.getAttribute('aria-expanded') !== 'true');
    });
  }
  if (scrim) scrim.addEventListener('click', function () { setNav(false); });
  $$('#primaryNav a').forEach(function (a) {
    a.addEventListener('click', function () { setNav(false); });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') setNav(false);
  });

  /* ---------- active section in nav ---------- */
  var navLinks = $$('#primaryNav a[href^="#"]');
  var sections = navLinks
    .map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); })
    .filter(Boolean);

  if (sections.length && 'IntersectionObserver' in window) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        navLinks.forEach(function (a) {
          a.classList.toggle('active', a.getAttribute('href') === '#' + entry.target.id);
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach(function (s) { spy.observe(s); });
  }

  /* ---------- scroll reveal ---------- */
  var revealables = $$('.reveal');
  if (!reduced && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var siblings = Array.prototype.slice.call(entry.target.parentNode.children);
        var i = Math.min(siblings.indexOf(entry.target), 5);
        entry.target.style.transitionDelay = (i * 70) + 'ms';
        entry.target.classList.add('in');
        obs.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealables.forEach(function (el) { io.observe(el); });
  }

  /* ---------- before / after comparison ---------- */
  $$('[data-ba]').forEach(function (fig) {
    var range = $('.ba-range', fig);
    var after = $('.ba-after', fig);
    var line  = $('.ba-line', fig);
    if (!range || !after || !line) return;

    var paint = function () {
      var pos = range.value + '%';
      after.style.setProperty('--pos', pos);
      line.style.left = pos;
    };
    range.addEventListener('input', paint);
    paint();
  });

  /* ---------- service preselect from any CTA ---------- */
  var serviceField = $('#f-service');
  var messageField = $('#f-message');

  $$('a[href="#book"][data-service]').forEach(function (a) {
    a.addEventListener('click', function () {
      if (serviceField) serviceField.value = a.getAttribute('data-service');
      var note = a.getAttribute('data-note');
      if (note && messageField && !messageField.value.trim()) {
        messageField.value = 'I’d like information about: ' + note + '.';
      }
    });
  });

  /* ---------- appointment form ---------- */
  var form   = $('#bookForm');
  var status = $('#formStatus');

  var RULES = {
    'f-name':  function (v) { return v.trim().length >= 2 || 'Please enter your name.'; },
    'f-email': function (v) { return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) || 'Please enter a valid email address.'; },
    'f-phone': function (v) { return (v.replace(/\D/g, '').length >= 10) || 'Please enter a 10-digit phone number.'; }
  };

  function validateField(id) {
    var input = document.getElementById(id);
    if (!input) return true;
    var result = RULES[id](input.value);
    var field  = input.closest('.field');
    var slot   = $('[data-err-for="' + id + '"]');
    var ok     = result === true;

    if (field) field.classList.toggle('invalid', !ok);
    if (slot)  slot.textContent = ok ? '' : result;
    input.setAttribute('aria-invalid', String(!ok));
    return ok;
  }

  Object.keys(RULES).forEach(function (id) {
    var input = document.getElementById(id);
    if (!input) return;
    input.addEventListener('blur', function () { validateField(id); });
    input.addEventListener('input', function () {
      if (input.closest('.field').classList.contains('invalid')) validateField(id);
    });
  });

  /* Format the phone as (305) 300-2863 while typing. */
  var phone = $('#f-phone');
  if (phone) {
    phone.addEventListener('input', function () {
      var d = phone.value.replace(/\D/g, '').slice(0, 10);
      if (!d) { phone.value = ''; return; }
      if (d.length < 4)      phone.value = '(' + d;
      else if (d.length < 7) phone.value = '(' + d.slice(0, 3) + ') ' + d.slice(3);
      else                   phone.value = '(' + d.slice(0, 3) + ') ' + d.slice(3, 6) + '-' + d.slice(6);
    });
  }

  function say(msg, kind) {
    if (!status) return;
    status.textContent = msg;
    status.className = 'form-status' + (kind ? ' ' + kind : '');
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      /* Honeypot — silently accept and drop. */
      if (form.company && form.company.value) {
        say('Thank you — we’ll be in touch shortly.', 'ok');
        form.reset();
        return;
      }

      var valid = Object.keys(RULES).map(validateField).every(Boolean);
      if (!valid) {
        say('Please correct the highlighted fields.', 'bad');
        var firstBad = $('.field.invalid input');
        if (firstBad) firstBad.focus();
        return;
      }

      var data = {
        name:    form.name.value.trim(),
        email:   form.email.value.trim(),
        phone:   form.phone.value.trim(),
        service: form.service.value,
        message: form.message.value.trim()
      };

      var endpoint = form.getAttribute('data-endpoint');
      var button   = $('button[type="submit"]', form);

      if (!endpoint) {
        /* No handler wired yet — hand off to the visitor's mail client so an
           enquiry is never silently lost. */
        var body = [
          'Name: '    + data.name,
          'Email: '   + data.email,
          'Phone: '   + data.phone,
          'Service: ' + data.service,
          '',
          data.message || '(no additional details)'
        ].join('\n');

        window.location.href = 'mailto:info@doggroomingusa.com'
          + '?subject=' + encodeURIComponent('Appointment request — ' + data.service + ' — ' + data.name)
          + '&body='    + encodeURIComponent(body);

        say('Opening your email app to send this request. Prefer to talk? Call 305-300-2863.', 'ok');
        return;
      }

      button.disabled = true;
      say('Sending…');

      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(data)
      }).then(function (res) {
        if (!res.ok) throw new Error(res.status);
        form.reset();
        say('Thank you — we’ll be in touch shortly to confirm your appointment.', 'ok');
      }).catch(function () {
        say('Something went wrong. Please call us at 305-300-2863 and we’ll get you booked.', 'bad');
      }).then(function () {
        button.disabled = false;
      });
    });
  }

  /* ---------- gallery lightbox ---------- */
  var lb     = $('#lightbox');
  var lbImg  = $('#lbImg');
  var lbCap  = $('#lbCap');
  var items  = $$('.gal');
  var index  = 0;
  var opener = null;

  function show(i) {
    index = (i + items.length) % items.length;
    var btn = items[index];
    lbImg.src = btn.getAttribute('data-full');
    lbImg.alt = btn.getAttribute('data-cap') || '';
    lbCap.textContent = (btn.getAttribute('data-cap') || '')
      + '  ·  ' + (index + 1) + ' / ' + items.length;
  }

  function openLb(i) {
    if (!lb) return;
    opener = document.activeElement;
    show(i);
    lb.hidden = false;
    document.body.classList.add('nav-open');
    $('.lb-close', lb).focus();
  }

  function closeLb() {
    if (!lb) return;
    lb.hidden = true;
    document.body.classList.remove('nav-open');
    if (opener) opener.focus();
  }

  items.forEach(function (btn, i) {
    btn.addEventListener('click', function () { openLb(i); });
  });

  if (lb) {
    $('.lb-close', lb).addEventListener('click', closeLb);
    $('.lb-prev',  lb).addEventListener('click', function () { show(index - 1); });
    $('.lb-next',  lb).addEventListener('click', function () { show(index + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) closeLb(); });

    document.addEventListener('keydown', function (e) {
      if (lb.hidden) return;
      if (e.key === 'Escape')     closeLb();
      if (e.key === 'ArrowLeft')  show(index - 1);
      if (e.key === 'ArrowRight') show(index + 1);
    });
  }


  /* ---------- ambient film ---------- */
  var reelFrame = $('#reelFrame');
  var reelVideo = $('#reelVideo');
  var reelToggle = $('#reelToggle');

  if (reelFrame && reelVideo) {
    var userPaused = false;
    var opened = false;

    /* Reveal the footage through the heart aperture, once. The mask is only
       ever applied here and is removed again the moment the growth finishes,
       so a missed transition can never leave the video clipped. */
    function openAperture() {
      if (opened) return;
      opened = true;
      if (reduced) return;

      reelFrame.classList.add('armed');
      void reelFrame.offsetWidth;           /* paint the small mask first */
      reelFrame.classList.add('open');

      var drop = function () { reelFrame.classList.remove('armed', 'open'); };
      reelFrame.addEventListener('transitionend', drop, { once: true });
      setTimeout(drop, 2400);
    }

    function setToggle(isPaused) {
      reelToggle.classList.toggle('paused', isPaused);
      reelToggle.setAttribute('aria-label',
        isPaused ? 'Play the background footage' : 'Pause the background footage');
    }

    function tryPlay() {
      if (userPaused || reduced) return;
      var p = reelVideo.play();
      if (p && p.catch) p.catch(function () { setToggle(true); });
    }

    if (reelToggle) {
      setToggle(reduced);
      reelToggle.addEventListener('click', function () {
        if (reelVideo.paused) { userPaused = false; reelVideo.play(); setToggle(false); }
        else { userPaused = true; reelVideo.pause(); setToggle(true); }
      });
      reelVideo.addEventListener('play',  function () { setToggle(false); });
      reelVideo.addEventListener('pause', function () { setToggle(true); });
    }

    /* Only run while on screen — it costs the visitor nothing in battery or
       data while they are further down the page. */
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) { openAperture(); tryPlay(); }
          else if (!reelVideo.paused) reelVideo.pause();
        });
      }, { threshold: 0.35 }).observe(reelFrame);
    } else {
      tryPlay();
    }
  }
})();