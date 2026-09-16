// Chart and visualization helpers from Final Design/final desgin.html

export function sparkline(values: number[], w = 640, h = 130, color = '#243B6B', fill = true): string {
  if (!values.length) return '';
  const max = Math.max(...values);
  const min = Math.min(...values);
  const rng = (max - min) || 1;
  const step = w / (values.length - 1 || 1);
  const pts = values.map((v, i) => [i * step, h - ((v - min) / rng) * (h - 30) - 15]);
  const d = pts.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' ');
  const area = `${d} L ${w} ${h} L 0 ${h} Z`;
  const uid = 'g' + Math.random().toString(36).slice(2, 7);
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" style="width:100%;height:${h}px;display:block">
    <defs><linearGradient id="${uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${color}" stop-opacity=".18"/>
      <stop offset="100%" stop-color="${color}" stop-opacity="0"/>
    </linearGradient></defs>
    ${fill ? `<path d="${area}" fill="url(#${uid})"/>` : ''}
    <path d="${d}" fill="none" stroke="${color}" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>
    ${pts.map((p, i) => `<circle cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="${i === pts.length - 1 ? 4 : 2.5}" fill="#fff" stroke="${color}" stroke-width="2"/>`).join('')}
  </svg>`;
}

export function barChart(values: number[], labels: string[] = [], w = 640, h = 180, color = '#243B6B'): string {
  if (!values.length) return '';
  const max = Math.max(...values, 1);
  const bw = w / values.length;
  const pad = bw * 0.18;
  const uid = 'b' + Math.random().toString(36).slice(2, 7);
  return `<svg viewBox="0 0 ${w} ${h + 24}" preserveAspectRatio="none" style="width:100%;height:${h + 24}px;display:block">
    <defs><linearGradient id="${uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${color}" stop-opacity=".95"/>
      <stop offset="100%" stop-color="${color}" stop-opacity=".65"/>
    </linearGradient></defs>
    ${[0, 0.25, 0.5, 0.75, 1].map(p => `<line x1="0" y1="${(h - (h - 30) * p).toFixed(1)}" x2="${w}" y2="${(h - (h - 30) * p).toFixed(1)}" stroke="#EEF1F6" stroke-width="1"/>`).join('')}
    ${values.map((v, i) => {
      const bh = ((v / max) * (h - 30)).toFixed(1);
      const x = (i * bw + pad / 2).toFixed(1);
      return `<rect class="chart-bar" x="${x}" y="${(h - Number(bh)).toFixed(1)}" width="${(bw - pad).toFixed(1)}" height="${bh}" rx="4" fill="url(#${uid})"/>`;
    }).join('')}
    ${labels.map((l, i) => {
      const x = (i * bw + bw / 2).toFixed(1);
      return `<text x="${x}" y="${h + 18}" text-anchor="middle" font-size="10.5" font-weight="600" fill="#98A2B3" font-family="Inter">${l}</text>`;
    }).join('')}
  </svg>`;
}

export function donut(pct: number, size = 110, stroke = 10, color = '#243B6B', label = '', sub = ''): string {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  return `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
    <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="#EDF0F5" stroke-width="${stroke}"/>
    <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="${color}" stroke-width="${stroke}"
      stroke-linecap="round" stroke-dasharray="${c}" stroke-dashoffset="${c * (1 - pct / 100)}"
      transform="rotate(-90 ${size / 2} ${size / 2})" style="transition:stroke-dashoffset 1s cubic-bezier(.2,.9,.3,1)"/>
    <text x="50%" y="${sub ? '46%' : '50%'}" text-anchor="middle" dominant-baseline="middle"
      font-family="Manrope,sans-serif" font-size="${size * 0.22}" font-weight="800" fill="#172033">${label || pct + '%'}</text>
    ${sub ? `<text x="50%" y="64%" text-anchor="middle" font-size="${size * 0.09}" font-weight="600" fill="#667085" font-family="Inter">${sub}</text>` : ''}
  </svg>`;
}

export function heatmap(weeks = 20): string {
  let out = '';
  for (let i = 0; i < weeks * 7; i++) {
    const lvl = Math.random() < 0.15 ? 0 : Math.random() < 0.3 ? 1 : Math.random() < 0.5 ? 2 : Math.random() < 0.8 ? 3 : 4;
    out += `<div class="hm-c ${lvl ? 'l' + lvl : ''}"></div>`;
  }
  return `<div class="hm">${out}</div>`;
}
