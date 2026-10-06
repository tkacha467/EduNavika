/**
 * EduNavika — Interactive 3D Storytelling Engine & Simulation
 * High-performance 3D canvas renderers, interactive physics, and live simulation.
 */

(function () {
  'use strict';

  // =========================================================================
  // 1. STATE & NAVIGATION
  // =========================================================================
  const scenes = document.querySelectorAll('.story-scene');
  const totalScenes = scenes.length;
  let currentSceneIndex = 0;
  let isAutoPlaying = false;
  let autoPlayTimer = null;

  const progressFill = document.getElementById('progressFill');
  const navDots = document.querySelectorAll('.nav-dot');
  const counterCurrent = document.getElementById('counterCurrent');
  const counterTotal = document.getElementById('counterTotal');
  const btnPrev = document.getElementById('btnPrevScene');
  const btnNext = document.getElementById('btnNextScene');
  const btnAutoPlay = document.getElementById('btnAutoPlay');
  const btnJumpSim = document.getElementById('btnJumpSim');

  if (counterTotal) counterTotal.textContent = String(totalScenes).padStart(2, '0');

  // Global mouse coordinates for 3D parallax
  const mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
  window.addEventListener('mousemove', (e) => {
    mouse.targetX = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.targetY = -(e.clientY / window.innerHeight) * 2 + 1;
  }, { passive: true });

  // Scroll to scene helper
  window.scrollToScene = function (index) {
    const clamped = Math.max(0, Math.min(index, totalScenes - 1));
    const target = scenes[clamped];
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  // Scene Observer
  const sceneObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting && entry.intersectionRatio >= 0.3) {
        const idx = parseInt(entry.target.dataset.sceneIndex || '0', 10);
        currentSceneIndex = idx;
        updateUI();
      }
    });
  }, { threshold: [0.3, 0.6] });

  scenes.forEach((s) => sceneObserver.observe(s));

  function updateUI() {
    if (counterCurrent) {
      counterCurrent.textContent = String(currentSceneIndex + 1).padStart(2, '0');
    }
    navDots.forEach((dot) => {
      const targetIdx = parseInt(dot.dataset.target, 10);
      dot.classList.toggle('active', targetIdx === currentSceneIndex);
    });
  }

  // Scroll progress
  window.addEventListener('scroll', () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    if (progressFill) progressFill.style.width = `${progress}%`;
  }, { passive: true });

  // Button handlers
  navDots.forEach((dot) => {
    dot.addEventListener('click', () => {
      const idx = parseInt(dot.dataset.target, 10);
      window.scrollToScene(idx);
    });
  });

  btnPrev?.addEventListener('click', () => window.scrollToScene(currentSceneIndex - 1));
  btnNext?.addEventListener('click', () => window.scrollToScene(currentSceneIndex + 1));
  btnJumpSim?.addEventListener('click', () => window.scrollToScene(8));

  // Keyboard navigation
  window.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown' || e.key === 'PageDown') {
      e.preventDefault();
      window.scrollToScene(currentSceneIndex + 1);
    } else if (e.key === 'ArrowUp' || e.key === 'PageUp') {
      e.preventDefault();
      window.scrollToScene(currentSceneIndex - 1);
    }
  });

  // Auto-play tour
  btnAutoPlay?.addEventListener('click', () => {
    isAutoPlaying = !isAutoPlaying;
    if (isAutoPlaying) {
      btnAutoPlay.classList.add('highlight');
      btnAutoPlay.querySelector('.label').textContent = 'Pause Tour';
      startAutoPlay();
    } else {
      btnAutoPlay.classList.remove('highlight');
      btnAutoPlay.querySelector('.label').textContent = 'Play Tour';
      stopAutoPlay();
    }
  });

  function startAutoPlay() {
    stopAutoPlay();
    autoPlayTimer = setInterval(() => {
      if (currentSceneIndex >= totalScenes - 1) {
        window.scrollToScene(0);
      } else {
        window.scrollToScene(currentSceneIndex + 1);
      }
    }, 6000);
  }

  function stopAutoPlay() {
    if (autoPlayTimer) clearInterval(autoPlayTimer);
    autoPlayTimer = null;
  }

  // 3D Card Hover Tilt Effect
  document.querySelectorAll('.card-3d-glass, .interactive-card-3d, .phone-frame-3d, .roi-card-3d').forEach((el) => {
    el.addEventListener('mousemove', (e) => {
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      const rotateX = (-y / rect.height) * 12;
      const rotateY = (x / rect.width) * 12;
      el.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    });
    el.addEventListener('mouseleave', () => {
      el.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg)';
    });
  });


  // =========================================================================
  // 2. GLOBAL 3D BACKGROUND PARTICLE COSMOS
  // =========================================================================
  const bgCanvas = document.getElementById('bg3dCanvas');
  if (bgCanvas) {
    const ctx = bgCanvas.getContext('2d');
    let width, height;
    const particles = [];
    const NUM_PARTICLES = 90;

    function resizeBg() {
      width = bgCanvas.width = window.innerWidth;
      height = bgCanvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resizeBg);
    resizeBg();

    for (let i = 0; i < NUM_PARTICLES; i++) {
      particles.push({
        x: (Math.random() - 0.5) * 1800,
        y: (Math.random() - 0.5) * 1800,
        z: Math.random() * 1000 + 100,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        size: Math.random() * 2 + 1,
        color: Math.random() > 0.6 ? '#06b6d4' : (Math.random() > 0.3 ? '#6366f1' : '#a855f7')
      });
    }

    function renderBg() {
      ctx.clearRect(0, 0, width, height);
      mouse.x += (mouse.targetX - mouse.x) * 0.05;
      mouse.y += (mouse.targetY - mouse.y) * 0.05;

      const fov = 400;
      const cx = width / 2 + mouse.x * 40;
      const cy = height / 2 - mouse.y * 40;

      // Draw particle nodes & links
      for (let i = 0; i < NUM_PARTICLES; i++) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < -900) p.x = 900;
        if (p.x > 900) p.x = -900;
        if (p.y < -900) p.y = 900;
        if (p.y > 900) p.y = -900;

        const scale = fov / (fov + p.z);
        const screenX = cx + p.x * scale;
        const screenY = cy + p.y * scale;

        if (screenX >= 0 && screenX <= width && screenY >= 0 && screenY <= height) {
          ctx.beginPath();
          ctx.arc(screenX, screenY, p.size * scale * 1.5, 0, Math.PI * 2);
          ctx.fillStyle = p.color;
          ctx.shadowBlur = 8 * scale;
          ctx.shadowColor = p.color;
          ctx.fill();
        }

        // Connecting lines for close particles
        for (let j = i + 1; j < NUM_PARTICLES; j++) {
          const p2 = particles[j];
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 140) {
            const scale2 = fov / (fov + p2.z);
            const x2 = cx + p2.x * scale2;
            const y2 = cy + p2.y * scale2;
            const alpha = (1 - dist / 140) * 0.25 * scale;
            ctx.beginPath();
            ctx.moveTo(screenX, screenY);
            ctx.lineTo(x2, y2);
            ctx.strokeStyle = `rgba(99, 102, 241, ${alpha})`;
            ctx.lineWidth = 0.8;
            ctx.shadowBlur = 0;
            ctx.stroke();
          }
        }
      }

      requestAnimationFrame(renderBg);
    }
    renderBg();
  }


  // =========================================================================
  // 3. SCENE 0: HERO 3D KNOWLEDGE UNIVERSE ORB
  // =========================================================================
  const heroCanvas = document.getElementById('canvasHeroOrb');
  if (heroCanvas) {
    const ctx = heroCanvas.getContext('2d');
    let w, h;
    let angleX = 0;
    let angleY = 0;

    function resizeHero() {
      const rect = heroCanvas.parentElement.getBoundingClientRect();
      w = heroCanvas.width = rect.width;
      h = heroCanvas.height = rect.height;
    }
    resizeHero();
    window.addEventListener('resize', resizeHero);

    // Orbiting nodes
    const topics = [
      { name: 'Quadratic Eq', r: 120, speed: 0.015, phase: 0, color: '#10b981' },
      { name: 'Trigonometry', r: 150, speed: -0.012, phase: 2, color: '#06b6d4' },
      { name: 'Linear Algebra', r: 130, speed: 0.018, phase: 4, color: '#f59e0b' },
      { name: 'Probability', r: 160, speed: -0.014, phase: 1, color: '#a855f7' }
    ];

    function renderHeroOrb() {
      ctx.clearRect(0, 0, w, h);
      angleX += 0.008;
      angleY += 0.005;

      const cx = w / 2;
      const cy = h / 2;

      // 3D Core Globe
      const corePulse = Math.sin(Date.now() * 0.003) * 6;
      const coreRadius = 55 + corePulse;

      const grad = ctx.createRadialGradient(cx - 15, cy - 15, 5, cx, cy, coreRadius);
      grad.addColorStop(0, '#ffffff');
      grad.addColorStop(0.3, '#6366f1');
      grad.addColorStop(0.7, '#06b6d4');
      grad.addColorStop(1, 'rgba(7, 9, 19, 0.1)');

      ctx.beginPath();
      ctx.arc(cx, cy, coreRadius, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.shadowBlur = 35;
      ctx.shadowColor = '#06b6d4';
      ctx.fill();

      // Orbiting 3D Rings
      ctx.lineWidth = 1.5;
      for (let i = 0; i < 3; i++) {
        ctx.beginPath();
        const tilt = (i * Math.PI) / 3 + angleY * 0.5;
        ctx.ellipse(cx, cy, 140, 60, tilt, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(99, 102, 241, ${0.3 + i * 0.1})`;
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#6366f1';
        ctx.stroke();
      }

      // Orbiting Subject Nodes
      topics.forEach((t) => {
        t.phase += t.speed;
        const x = cx + Math.cos(t.phase) * t.r;
        const y = cy + Math.sin(t.phase) * (t.r * 0.45);
        const z = Math.sin(t.phase);

        const nodeScale = (z + 2) / 3;
        const nodeRadius = 8 * nodeScale;

        // Laser connector to core
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(x, y);
        ctx.strokeStyle = `rgba(6, 182, 212, ${0.2 * nodeScale})`;
        ctx.lineWidth = 1;
        ctx.stroke();

        // Node
        ctx.beginPath();
        ctx.arc(x, y, nodeRadius, 0, Math.PI * 2);
        ctx.fillStyle = t.color;
        ctx.shadowBlur = 15 * nodeScale;
        ctx.shadowColor = t.color;
        ctx.fill();

        // Node Label
        ctx.font = `600 ${11 * nodeScale}px Plus Jakarta Sans`;
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.shadowBlur = 0;
        ctx.fillText(t.name, x, y - 12 * nodeScale);
      });

      requestAnimationFrame(renderHeroOrb);
    }
    renderHeroOrb();
  }


  // =========================================================================
  // 4. SCENE 1: SYNAPTIC SPARK 3D CANVAS
  // =========================================================================
  const scene1Canvas = document.getElementById('canvasScene1');
  if (scene1Canvas) {
    const ctx = scene1Canvas.getContext('2d');
    let w, h;

    function resizeS1() {
      const rect = scene1Canvas.parentElement.getBoundingClientRect();
      w = scene1Canvas.width = rect.width;
      h = scene1Canvas.height = rect.height;
    }
    resizeS1();
    window.addEventListener('resize', resizeS1);

    const nodes = [];
    for (let i = 0; i < 24; i++) {
      nodes.push({
        x: (Math.random() - 0.5) * 260,
        y: (Math.random() - 0.5) * 260,
        z: (Math.random() - 0.5) * 260,
        color: Math.random() > 0.5 ? '#10b981' : '#34d399',
        pulse: Math.random() * Math.PI
      });
    }

    let rotY = 0;
    function renderScene1() {
      ctx.clearRect(0, 0, w, h);
      rotY += 0.012;
      const cx = w / 2;
      const cy = h / 2;

      // Central Energy Core
      const pulse = Math.sin(Date.now() * 0.005) * 8;
      const grad = ctx.createRadialGradient(cx, cy, 5, cx, cy, 60 + pulse);
      grad.addColorStop(0, '#ffffff');
      grad.addColorStop(0.4, '#10b981');
      grad.addColorStop(1, 'transparent');

      ctx.beginPath();
      ctx.arc(cx, cy, 60 + pulse, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.shadowBlur = 30;
      ctx.shadowColor = '#10b981';
      ctx.fill();

      // Rotating 3D Synapses
      nodes.forEach((n, i) => {
        n.pulse += 0.03;
        const cos = Math.cos(rotY);
        const sin = Math.sin(rotY);
        const x3d = n.x * cos - n.z * sin;
        const z3d = n.z * cos + n.x * sin;
        const y3d = n.y;

        const scale = 300 / (300 + z3d);
        const sx = cx + x3d * scale;
        const sy = cy + y3d * scale;

        // Spark connection
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(sx, sy);
        ctx.strokeStyle = `rgba(16, 185, 129, ${0.4 * scale})`;
        ctx.lineWidth = 1.5 * scale;
        ctx.stroke();

        // Synapse Head
        ctx.beginPath();
        ctx.arc(sx, sy, (4 + Math.sin(n.pulse) * 2) * scale, 0, Math.PI * 2);
        ctx.fillStyle = n.color;
        ctx.shadowBlur = 12 * scale;
        ctx.shadowColor = n.color;
        ctx.fill();
      });

      requestAnimationFrame(renderScene1);
    }
    renderScene1();
  }


  // =========================================================================
  // 5. SCENE 2: INTERACTIVE 30-DAY FORGETTING DECAY SIMULATOR
  // =========================================================================
  const decaySlider = document.getElementById('decaySlider');
  const decayStatDay = document.getElementById('decayStatDay');
  const decayStatDate = document.getElementById('decayStatDate');
  const decayStatRetention = document.getElementById('decayStatRetention');
  const decayStatCondition = document.getElementById('decayStatCondition');
  const decayStatTeacher = document.getElementById('decayStatTeacher');
  const hudCoreEnergy = document.getElementById('hudCoreEnergy');
  const hudDecayRate = document.getElementById('hudDecayRate');
  const btnPlayDecay = document.getElementById('btnPlayDecay');
  const btnResetDecay = document.getElementById('btnResetDecay');
  const canvasScene2 = document.getElementById('canvasScene2');

  let currentDecayDay = 1;
  let decayPlayInterval = null;

  function calculateRetention(day) {
    // Ebbinghaus Forgetting Curve formula: R = e^(-t/S)
    const retention = Math.round(98 * Math.exp(-0.038 * (day - 1)));
    return Math.max(28, retention);
  }

  function updateDecayDisplay(day) {
    currentDecayDay = day;
    if (decaySlider) decaySlider.value = String(day);

    const ret = calculateRetention(day);
    if (decayStatDay) decayStatDay.textContent = `Day ${day}`;
    if (decayStatDate) {
      if (day <= 3) decayStatDate.textContent = 'Sept 12 (Taught)';
      else if (day <= 10) decayStatDate.textContent = 'Sept 19 (1 Week Later)';
      else if (day <= 20) decayStatDate.textContent = 'Oct 02 (2 Weeks Later)';
      else decayStatDate.textContent = 'Oct 12 (Exam Eve)';
    }

    if (decayStatRetention) {
      decayStatRetention.textContent = `${ret}%`;
      decayStatRetention.className = 'val ' + (ret >= 75 ? 'text-green' : (ret >= 55 ? 'text-gold' : 'text-coral'));
    }

    if (decayStatCondition) {
      if (ret >= 80) decayStatCondition.textContent = 'Strong Recall';
      else if (ret >= 60) decayStatCondition.textContent = 'Hesitation Creeping In';
      else decayStatCondition.textContent = 'Severe Knowledge Gap';
    }

    if (decayStatTeacher) {
      decayStatTeacher.textContent = day <= 3 ? 'Concept Verified' : (day <= 14 ? 'Invisible Decline' : 'Critical Blindspot ⚠️');
    }

    if (hudCoreEnergy) hudCoreEnergy.textContent = `${ret}%`;
    if (hudDecayRate) {
      hudDecayRate.textContent = day <= 5 ? 'Normal consolidation' : (day <= 18 ? 'Steep Ebbinghaus drop' : 'Only 1/3 skill accessible');
    }
  }

  decaySlider?.addEventListener('input', (e) => {
    stopDecayAutoPlay();
    updateDecayDisplay(parseInt(e.target.value, 10));
  });

  btnPlayDecay?.addEventListener('click', () => {
    stopDecayAutoPlay();
    let d = 1;
    updateDecayDisplay(d);
    decayPlayInterval = setInterval(() => {
      d++;
      if (d > 30) {
        stopDecayAutoPlay();
      } else {
        updateDecayDisplay(d);
      }
    }, 120);
  });

  btnResetDecay?.addEventListener('click', () => {
    stopDecayAutoPlay();
    updateDecayDisplay(1);
  });

  function stopDecayAutoPlay() {
    if (decayPlayInterval) clearInterval(decayPlayInterval);
    decayPlayInterval = null;
  }

  // 3D Canvas for Memory Decay Orb
  if (canvasScene2) {
    const ctx = canvasScene2.getContext('2d');
    let w, h;

    function resizeS2() {
      const rect = canvasScene2.parentElement.getBoundingClientRect();
      w = canvasScene2.width = rect.width;
      h = canvasScene2.height = rect.height;
    }
    resizeS2();
    window.addEventListener('resize', resizeS2);

    const debris = [];
    for (let i = 0; i < 40; i++) {
      debris.push({
        x: (Math.random() - 0.5) * 200,
        y: (Math.random() - 0.5) * 200,
        z: Math.random() * 200,
        vx: (Math.random() - 0.5) * 1.5,
        vy: (Math.random() - 0.5) * 1.5,
        alpha: Math.random()
      });
    }

    function renderScene2() {
      ctx.clearRect(0, 0, w, h);
      const cx = w / 2;
      const cy = h / 2;

      const ret = calculateRetention(currentDecayDay) / 100; // 0.28 to 0.98

      // Determine Core Glow Color
      let coreColor = '#10b981';
      let shadowCol = '#10b981';
      if (ret < 0.55) {
        coreColor = '#ef4444';
        shadowCol = '#ef4444';
      } else if (ret < 0.75) {
        coreColor = '#f59e0b';
        shadowCol = '#f59e0b';
      }

      // 3D Dying Core Globe
      const baseRadius = 35 + 40 * ret;
      const grad = ctx.createRadialGradient(cx, cy, 5, cx, cy, baseRadius);
      grad.addColorStop(0, '#ffffff');
      grad.addColorStop(0.5, coreColor);
      grad.addColorStop(1, 'transparent');

      ctx.beginPath();
      ctx.arc(cx, cy, baseRadius, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.shadowBlur = 40 * ret;
      ctx.shadowColor = shadowCol;
      ctx.fill();

      // Debris particles flaking away as decay increases
      if (ret < 0.8) {
        const flakeCount = Math.floor((1 - ret) * 40);
        for (let i = 0; i < flakeCount; i++) {
          const d = debris[i];
          d.x += d.vx;
          d.y += d.vy;
          if (Math.abs(d.x) > 160 || Math.abs(d.y) > 160) {
            d.x = (Math.random() - 0.5) * 40;
            d.y = (Math.random() - 0.5) * 40;
          }

          ctx.beginPath();
          ctx.arc(cx + d.x, cy + d.y, 2.5, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(239, 68, 68, ${0.7 * (1 - ret)})`;
          ctx.shadowBlur = 8;
          ctx.shadowColor = '#ef4444';
          ctx.fill();
        }
      }

      // Forgetting Curve overlay on bottom
      ctx.beginPath();
      ctx.moveTo(40, h - 30);
      for (let x = 40; x < w - 40; x += 5) {
        const prog = (x - 40) / (w - 80); // 0 to 1
        const dayAtX = 1 + prog * 29;
        const retAtX = calculateRetention(dayAtX) / 100;
        const y = h - 30 - retAtX * 60;
        ctx.lineTo(x, y);
      }
      ctx.strokeStyle = `rgba(255, 255, 255, 0.25)`;
      ctx.lineWidth = 2;
      ctx.shadowBlur = 0;
      ctx.stroke();

      // Current point on curve
      const currentX = 40 + ((currentDecayDay - 1) / 29) * (w - 80);
      const currentY = h - 30 - ret * 60;

      ctx.beginPath();
      ctx.arc(currentX, currentY, 6, 0, Math.PI * 2);
      ctx.fillStyle = coreColor;
      ctx.shadowBlur = 15;
      ctx.shadowColor = coreColor;
      ctx.fill();

      requestAnimationFrame(renderScene2);
    }
    renderScene2();
  }


  // =========================================================================
  // 6. SCENE 4: SPACED REPETITION 3D REACTOR
  // =========================================================================
  const canvasScene4 = document.getElementById('canvasScene4');
  const btnTriggerPulse = document.getElementById('btnTriggerPulse');

  if (canvasScene4) {
    const ctx = canvasScene4.getContext('2d');
    let w, h;
    let pulseShockwave = 0;
    let reactorEnergy = 0.65;

    function resizeS4() {
      const rect = canvasScene4.parentElement.getBoundingClientRect();
      w = canvasScene4.width = rect.width;
      h = canvasScene4.height = rect.height;
    }
    resizeS4();
    window.addEventListener('resize', resizeS4);

    btnTriggerPulse?.addEventListener('click', () => {
      pulseShockwave = 1;
      reactorEnergy = 1.0;
      highlightEngineSteps();
    });

    function highlightEngineSteps() {
      const steps = [document.getElementById('engineStep1'), document.getElementById('engineStep2'), document.getElementById('engineStep3')];
      steps.forEach((s, idx) => {
        setTimeout(() => {
          s?.classList.add('highlight-card');
          setTimeout(() => s?.classList.remove('highlight-card'), 1800);
        }, idx * 400);
      });
    }

    let angle = 0;
    function renderReactor() {
      ctx.clearRect(0, 0, w, h);
      angle += 0.015;
      const cx = w / 2;
      const cy = h / 2;

      // Shockwave animation
      if (pulseShockwave > 0) {
        pulseShockwave += 0.02;
        const waveRadius = pulseShockwave * 180;
        const waveAlpha = Math.max(0, 1 - pulseShockwave);

        ctx.beginPath();
        ctx.arc(cx, cy, waveRadius, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(6, 182, 212, ${waveAlpha})`;
        ctx.lineWidth = 4 * waveAlpha;
        ctx.shadowBlur = 20;
        ctx.shadowColor = '#06b6d4';
        ctx.stroke();

        if (pulseShockwave >= 1) pulseShockwave = 0;
      }

      // Multi-Ring Gyroscope
      for (let i = 0; i < 4; i++) {
        ctx.beginPath();
        const r = 80 + i * 28;
        const tilt = angle * (i % 2 === 0 ? 1 : -1) + (i * Math.PI) / 4;
        ctx.ellipse(cx, cy, r, r * 0.45, tilt, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(6, 182, 212, ${0.3 + (i / 4) * 0.4})`;
        ctx.lineWidth = 2;
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#06b6d4';
        ctx.stroke();
      }

      // Glowing Center
      const coreR = 40 + reactorEnergy * 25 + Math.sin(Date.now() * 0.005) * 5;
      const grad = ctx.createRadialGradient(cx, cy, 5, cx, cy, coreR);
      grad.addColorStop(0, '#ffffff');
      grad.addColorStop(0.4, '#06b6d4');
      grad.addColorStop(0.8, '#6366f1');
      grad.addColorStop(1, 'transparent');

      ctx.beginPath();
      ctx.arc(cx, cy, coreR, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.shadowBlur = 35;
      ctx.shadowColor = '#06b6d4';
      ctx.fill();

      requestAnimationFrame(renderReactor);
    }
    renderReactor();
  }


  // =========================================================================
  // 7. SCENE 6: STUDENT 3D DRILL INTERACTION
  // =========================================================================
  const quizOpts = document.querySelectorAll('.quiz-opt');
  const drillToast = document.getElementById('drillToast');
  const phone3d = document.getElementById('phone3d');

  quizOpts.forEach((btn) => {
    btn.addEventListener('click', () => {
      const isCorrect = btn.dataset.correct === 'true';
      quizOpts.forEach((b) => b.classList.remove('correct', 'wrong'));

      if (isCorrect) {
        btn.classList.add('correct');
        if (drillToast) drillToast.classList.add('show');

        // Phone celebration tilt
        if (phone3d) {
          phone3d.style.transform = 'perspective(1000px) scale(1.04) rotateY(4deg)';
          setTimeout(() => {
            phone3d.style.transform = 'perspective(1000px) scale(1) rotateY(-6deg) rotateX(4deg)';
          }, 600);
        }
      } else {
        btn.classList.add('wrong');
      }
    });
  });


  // =========================================================================
  // 8. SCENE 8: LIVE 60-DAY CLASS SIMULATION PLAYGROUND
  // =========================================================================
  const btnRunSim = document.getElementById('btnRunSim');
  const simDayNumber = document.getElementById('simDayNumber');
  const simProgressFill = document.getElementById('simProgressFill');
  const tradFinalScore = document.getElementById('tradFinalScore');
  const eduFinalScore = document.getElementById('eduFinalScore');
  const canvasTrad = document.getElementById('canvasSimTraditional');
  const canvasEdu = document.getElementById('canvasSimEduNavika');

  let simInterval = null;
  let currentSimDay = 0;
  const TOTAL_SIM_DAYS = 60;

  // 30 Students Data Simulation
  const studentData = {
    traditional: [],
    edunavika: []
  };

  function initSimData() {
    studentData.traditional = [];
    studentData.edunavika = [];

    // Pre-calculate 60 days trajectory for 30 students
    for (let s = 0; s < 30; s++) {
      const baseLearn = 90 + Math.random() * 8; // 90-98%
      const decaySpeed = 0.03 + Math.random() * 0.015;

      const tradDays = [];
      const eduDays = [];

      let currentEdu = baseLearn;

      for (let d = 0; d <= TOTAL_SIM_DAYS; d++) {
        // Traditional: straight forgetting curve
        const tradVal = Math.max(25, Math.round(baseLearn * Math.exp(-decaySpeed * d)));
        tradDays.push(tradVal);

        // EduNavika: Boosted at Day 6, Day 18, Day 36
        if (d === 6 || d === 18 || d === 36) {
          currentEdu = Math.min(100, currentEdu + 28);
        } else {
          currentEdu = Math.max(70, currentEdu - (decaySpeed * 0.45 * 100) / 10);
        }
        eduDays.push(Math.round(currentEdu));
      }

      studentData.traditional.push(tradDays);
      studentData.edunavika.push(eduDays);
    }
  }
  initSimData();

  function drawSimChart(canvas, dataList, dayLimit, isEdu) {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);

    // Grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
    ctx.lineWidth = 1;
    for (let y = 30; y < h - 20; y += 40) {
      ctx.beginPath();
      ctx.moveTo(30, y);
      ctx.lineTo(w - 20, y);
      ctx.stroke();
    }

    // Draw individual student trajectory lines
    dataList.forEach((studentCurve) => {
      ctx.beginPath();
      const color = isEdu ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)';
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.2;

      for (let d = 0; d <= dayLimit; d++) {
        const x = 30 + (d / TOTAL_SIM_DAYS) * (w - 50);
        const y = h - 25 - (studentCurve[d] / 100) * (h - 50);
        if (d === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
    });

    // Draw Class Average Line
    ctx.beginPath();
    ctx.strokeStyle = isEdu ? '#10b981' : '#ef4444';
    ctx.lineWidth = 3;
    ctx.shadowBlur = 10;
    ctx.shadowColor = isEdu ? '#10b981' : '#ef4444';

    let currentAvg = 0;
    for (let d = 0; d <= dayLimit; d++) {
      let sum = 0;
      dataList.forEach((sc) => (sum += sc[d]));
      const avg = sum / dataList.length;
      if (d === dayLimit) currentAvg = Math.round(avg);

      const x = 30 + (d / TOTAL_SIM_DAYS) * (w - 50);
      const y = h - 25 - (avg / 100) * (h - 50);
      if (d === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.shadowBlur = 0;

    return currentAvg;
  }

  function runSimulation() {
    if (simInterval) clearInterval(simInterval);
    currentSimDay = 0;

    simInterval = setInterval(() => {
      currentSimDay++;
      if (simDayNumber) simDayNumber.textContent = `${currentSimDay} / ${TOTAL_SIM_DAYS}`;
      if (simProgressFill) simProgressFill.style.width = `${(currentSimDay / TOTAL_SIM_DAYS) * 100}%`;

      const tradAvg = drawSimChart(canvasTrad, studentData.traditional, currentSimDay, false);
      const eduAvg = drawSimChart(canvasEdu, studentData.edunavika, currentSimDay, true);

      if (tradFinalScore) tradFinalScore.textContent = `Avg Retention: ${tradAvg}%`;
      if (eduFinalScore) eduFinalScore.textContent = `Avg Retention: ${eduAvg}%`;

      if (currentSimDay >= TOTAL_SIM_DAYS) {
        clearInterval(simInterval);
        simInterval = null;
      }
    }, 50);
  }

  btnRunSim?.addEventListener('click', runSimulation);

  // Initial draw at day 0
  drawSimChart(canvasTrad, studentData.traditional, 0, false);
  drawSimChart(canvasEdu, studentData.edunavika, 0, true);

})();
