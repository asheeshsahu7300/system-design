/**
 * TinyURL Dashboard JavaScript
 * Handles:
 *  - Switching between Python (8000) and Go (8080) backend APIs
 *  - Real-time health polling
 *  - URL creation with custom slug support
 *  - Dynamic QR Code generation
 *  - Live analytics drawer
 */

const ENGINES = {
  python: {
    name: 'Python FastAPI',
    url: 'http://localhost:8000',
  },
  go: {
    name: 'Go HTTP',
    url: 'http://localhost:8080',
  }
};

let currentEngine = 'python';
let currentShortCode = '';
let qrcodeInstance = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  checkBackendHealth();
  fetchRecentLinks();
  // Poll health every 10 seconds
  setInterval(checkBackendHealth, 10000);
});

function switchEngine(engineKey) {
  currentEngine = engineKey;
  document.getElementById('engine-python').classList.toggle('active', engineKey === 'python');
  document.getElementById('engine-go').classList.toggle('active', engineKey === 'go');
  checkBackendHealth();
  fetchRecentLinks();
}

function getBaseUrl() {
  return ENGINES[currentEngine].url;
}

async function checkBackendHealth() {
  const statusEl = document.getElementById('status-text');
  const ringEl = document.querySelector('.pulse-ring');
  
  try {
    const res = await fetch(`${getBaseUrl()}/api/v1/health`, { method: 'GET' });
    if (res.ok) {
      const data = await res.json();
      statusEl.textContent = `${ENGINES[currentEngine].name} Online (Active)`;
      statusEl.style.color = '#10b981';
      ringEl.style.background = '#10b981';
      ringEl.style.boxShadow = '0 0 10px #10b981';
    } else {
      throw new Error('Non-200');
    }
  } catch (err) {
    statusEl.textContent = `${ENGINES[currentEngine].name} Offline (Start Server)`;
    statusEl.style.color = '#f43f5e';
    ringEl.style.background = '#f43f5e';
    ringEl.style.boxShadow = '0 0 10px #f43f5e';
  }
}

async function handleShorten(e) {
  e.preventDefault();
  const submitBtn = document.getElementById('submit-btn');
  const longUrl = document.getElementById('long-url').value.trim();
  const customAlias = document.getElementById('custom-alias').value.trim();
  const ttlDays = parseInt(document.getElementById('ttl-select').value, 10);

  if (!longUrl) return;

  submitBtn.disabled = true;
  submitBtn.innerHTML = `<span>Shortening...</span>`;

  try {
    const payload = {
      url: longUrl,
      ttl_days: ttlDays,
    };
    if (customAlias) {
      payload.custom_alias = customAlias;
    }

    const res = await fetch(`${getBaseUrl()}/api/v1/shorten`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: 'Request failed' }));
      alert(`Error: ${errData.detail || errData.error || 'Failed to shorten URL'}`);
      return;
    }

    const data = await res.json();
    currentShortCode = data.short_code;
    displayResult(data);
    fetchRecentLinks();

  } catch (err) {
    alert(`Backend is unreachable at ${getBaseUrl()}. Please ensure the server is running!`);
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `
      <span>Generate Short Link</span>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <line x1="5" y1="12" x2="19" y2="12"></line>
        <polyline points="12 5 19 12 12 19"></polyline>
      </svg>
    `;
  }
}

function displayResult(data) {
  const resultBox = document.getElementById('result-box');
  const outputInput = document.getElementById('short-url-output');
  const testLink = document.getElementById('test-redirect-link');
  const algoTag = document.getElementById('result-algo');

  outputInput.value = data.short_url;
  testLink.href = data.short_url;
  algoTag.textContent = data.custom_alias ? 'Custom Alias • Verified Unique' : 'Base62 7-Chars • KeyGen';

  // Render QR Code
  const qrContainer = document.getElementById('qrcode-container');
  qrContainer.innerHTML = '';
  qrcodeInstance = new QRCode(qrContainer, {
    text: data.short_url,
    width: 88,
    height: 88,
    colorDark: '#080c14',
    colorLight: '#ffffff',
    correctLevel: QRCode.CorrectLevel.M
  });

  resultBox.classList.remove('hidden');
}

function copyToClipboard() {
  const outputInput = document.getElementById('short-url-output');
  navigator.clipboard.writeText(outputInput.value).then(() => {
    showToast('Copied short link to clipboard!');
  });
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.remove('hidden');
  setTimeout(() => {
    toast.classList.add('hidden');
  }, 2400);
}

async function fetchRecentLinks() {
  try {
    const res = await fetch(`${getBaseUrl()}/api/v1/recent`);
    if (!res.ok) return;
    const items = await res.json();
    const tbody = document.getElementById('recent-tbody');

    if (!items || items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" class="empty-state">No links shortened yet. Try creating one!</td></tr>`;
      return;
    }

    tbody.innerHTML = items.map(item => `
      <tr>
        <td><code>/${item.short_code}</code></td>
        <td><span class="truncate" title="${item.original_url}">${item.original_url}</span></td>
        <td><strong>${item.clicks || 0}</strong></td>
        <td>
          <button class="btn btn-sm btn-outline" onclick="openAnalytics('${item.short_code}')">Analytics</button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    // Silent fail on background fetch
  }
}

function loadAnalyticsForCurrent() {
  if (currentShortCode) {
    openAnalytics(currentShortCode);
  }
}

async function openAnalytics(code) {
  try {
    const res = await fetch(`${getBaseUrl()}/api/v1/analytics/${code}`);
    if (!res.ok) {
      alert('Could not fetch analytics.');
      return;
    }

    const data = await res.json();
    document.getElementById('modal-title').textContent = `Analytics for /${data.short_code}`;
    document.getElementById('modal-orig').textContent = data.original_url;
    document.getElementById('modal-clicks').textContent = data.total_clicks;

    const logEl = document.getElementById('modal-log');
    if (data.recent_clicks && data.recent_clicks.length > 0) {
      logEl.innerHTML = data.recent_clicks.map(c => `
        <div style="padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.06);">
          <span>⏱️ ${new Date(c.timestamp).toLocaleTimeString()}</span> &bull; 
          <span>IP: ${c.ip}</span> &bull; 
          <span>Ref: ${c.referrer}</span>
        </div>
      `).join('');
    } else {
      logEl.innerHTML = `<p class="empty-log">No clicks recorded yet. Open the link to simulate traffic!</p>`;
    }

    document.getElementById('analytics-modal').classList.remove('hidden');

  } catch (err) {
    alert('Failed to connect to backend for analytics.');
  }
}

function closeAnalyticsModal() {
  document.getElementById('analytics-modal').classList.add('hidden');
}
