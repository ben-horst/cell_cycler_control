const startBtn = document.getElementById('startBtn');
const pollBtn = document.getElementById('pollBtn');
const logsBox = document.getElementById('logsBox');
const msBox = document.getElementById('msBox');

async function startTest() {
  const banks = document.getElementById('banks').value.trim();
  const specimens_to_skip = document.getElementById('specimens_to_skip_7526').value.trim();
  if (!banks) {
    console.warn('Banks is required');
    alert('Banks is required (use ALL or comma-separated list)');
    return;
  }
  console.log('Starting test with:', { banks, specimens_to_skip });
  logsBox.textContent = 'Running (streaming)... this may take a while.\n';
  // Use SSE for streaming logs
  const url = `/api/run_7526_rpt_stream?banks=${encodeURIComponent(banks)}&specimens_to_skip=${encodeURIComponent(specimens_to_skip)}`;
  const es = new EventSource(url);
  es.onmessage = (e) => {
    console.log('SSE:', e.data);
    logsBox.textContent += e.data + '\n';
    logsBox.scrollTop = logsBox.scrollHeight;
  };
  es.addEventListener('done', () => {
    console.log('SSE done');
    es.close();
  });
  es.onerror = (e) => {
    console.error('SSE error', e);
    es.close();
  };
}

let pollTimer = null;
async function pollMiddleServer() {
  try {
    const resp = await fetch('/api/middle_server_events');
    const data = await resp.json();
    console.log('Middle server events:', data);
    const events = (data && data.events) ? data.events : [];
    msBox.textContent = events.join('\n');
  } catch (e) {
    console.error('Poll error:', e);
  }
}

if (startBtn) {
  startBtn.addEventListener('click', () => {
    if (!pollTimer) {
      pollTimer = setInterval(pollMiddleServer, 2000);
    }
    startTest();
  });
}

if (pollBtn) {
  pollBtn.addEventListener('click', () => {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    } else {
      pollTimer = setInterval(pollMiddleServer, 2000);
      pollMiddleServer();
    }
  });
}

