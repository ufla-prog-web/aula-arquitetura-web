const $ = (sel) => document.querySelector(sel);
const output = $('#output');
const badge = $('#response-badge');
const meta = $('#response-meta');

for (const btn of document.querySelectorAll('.nav-btn')) {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active-panel'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.target).classList.add('active-panel');
  });
}

const statusPresets = [
  [200,'OK'], [201,'Created'], [204,'No Content'], [301,'Moved'], [302,'Found'],
  [400,'Bad Request'], [401,'Unauthorized'], [403,'Forbidden'], [404,'Not Found'], [418,"I'm a teapot"],
  [429,'Too Many'], [500,'Server Error'], [502,'Bad Gateway'], [503,'Unavailable']
];
const statusButtons = $('#status-buttons');
statusPresets.forEach(([code, label]) => {
  const b = document.createElement('button');
  b.className = 'status-btn';
  b.innerHTML = `<strong>${code}</strong><small>${label}</small>`;
  b.onclick = () => testStatus(code);
  statusButtons.appendChild(b);
});

function parseHeaders(text) {
  const h = {};
  text.split('\n').forEach(line => {
    const i = line.indexOf(':');
    if (i > 0) h[line.slice(0,i).trim()] = line.slice(i+1).trim();
  });
  return h;
}

function show(status, statusText, headers, data, duration) {
  badge.textContent = `${status} ${statusText || ''}`.trim();
  badge.className = 'response-badge ' + (status < 300 ? 'ok' : status < 500 ? 'warn' : 'err');
  meta.innerHTML = '';
  const values = [
    `tempo: ${duration} ms`,
    `content-type: ${headers.get('content-type') || '—'}`,
    `content-length: ${headers.get('content-length') || '—'}`,
  ];
  values.forEach(v => {
    const s = document.createElement('span'); s.className='meta-chip'; s.textContent=v; meta.appendChild(s);
  });
  output.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
}

async function request(url, options={}) {
  const start = performance.now();
  try {
    const res = await fetch(url, options);
    const text = await res.text();
    let data;
    try { data = JSON.parse(text); } catch { data = text || '(corpo vazio)'; }
    show(res.status, res.statusText, res.headers, data, Math.round(performance.now()-start));
    return {res, data};
  } catch (err) {
    badge.textContent='erro de rede'; badge.className='response-badge err';
    output.textContent=String(err); meta.innerHTML='';
    throw err;
  }
}

$('#send-request').onclick = async () => {
  const method = $('#method').value;
  const q = $('#query').value.trim();
  const url = '/api/inspect' + (q ? '?' + q : '');
  const headers = parseHeaders($('#headers').value);
  const options = { method, headers };
  if (!['GET','HEAD'].includes(method)) {
    options.body = $('#body').value;
    if (!Object.keys(headers).some(k => k.toLowerCase()==='content-type')) {
      options.headers['Content-Type'] = 'application/json';
    }
  }
  await request(url, options);
};

$('#clear-output').onclick = () => {
  output.textContent='Console limpo. Execute um novo experimento.';
  badge.textContent='aguardando'; badge.className='response-badge idle'; meta.innerHTML='';
};

async function testStatus(code) { await request(`/api/status/${code}`); }
$('#send-status').onclick = () => testStatus($('#custom-status').value);

$('#set-cookie').onclick = async () => {
  const name = encodeURIComponent($('#cookie-name').value);
  const value = encodeURIComponent($('#cookie-value').value);
  const result = await request(`/api/cookies/set?name=${name}&value=${value}`);
  $('#cookie-view').textContent = `Cookie solicitado: ${decodeURIComponent(name)}=${decodeURIComponent(value)}. Agora clique em “Ler cookies enviados”.`;
};
$('#read-cookie').onclick = async () => {
  const {data} = await request('/api/cookies/read');
  $('#cookie-view').textContent = 'Cookies que o navegador enviou: ' + JSON.stringify(data.cookies || {});
};
$('#delete-cookie').onclick = async () => {
  const name = encodeURIComponent($('#cookie-name').value);
  await request(`/api/cookies/delete?name=${name}`);
  $('#cookie-view').textContent = `Exclusão solicitada para o cookie ${decodeURIComponent(name)}.`;
};

$('#test-redirect').onclick = async () => {
  const code = $('#redirect-code').value;
  const to = encodeURIComponent($('#redirect-to').value);
  await request(`/api/redirect?code=${code}&to=${to}`, {redirect:'manual'});
};

$('#test-header').onclick = async () => {
  const value = encodeURIComponent($('#demo-header').value);
  const {res, data} = await request(`/api/headers?x_demo=${value}`);
  const extra = { body:data, observed_headers:{} };
  for (const [k,v] of res.headers.entries()) extra.observed_headers[k]=v;
  output.textContent = JSON.stringify(extra, null, 2);
};
