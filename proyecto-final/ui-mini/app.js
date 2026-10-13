const WS_URL = 'ws://127.0.0.1:8000/ws/metrics';

const ws = new WebSocket(WS_URL);
const countCtx = document.getElementById('chartCount').getContext('2d');
const sentCtx = document.getElementById('chartSent').getContext('2d');

const countData = {labels: [], datasets: [{label: 'Comentarios', data: []}]};
const sentData = {labels: [], datasets: [
  {label:'Positivo', data: []},
  {label:'Neutral', data: []},
  {label:'Negativo', data: []}
]};

const countChart = new Chart(countCtx, {type: 'line', data: countData});
const sentChart = new Chart(sentCtx, {type: 'line', data: sentData});

function addPoint(label, payload){
  countData.labels.push(label);
  countData.datasets[0].data.push(payload.total_comments || 0);
  countChart.update();

  sentData.labels.push(label);
  const s = payload.avg_sentiment || {};
  sentData.datasets[0].data.push(s.positive || 0);
  sentData.datasets[1].data.push(s.neutral || 0);
  sentData.datasets[2].data.push(s.negative || 0);
  sentChart.update();

  const chips = document.getElementById('chips');
  chips.innerHTML = '';
  (payload.top_hashtags || []).forEach(([tag, cnt])=>{
    const span = document.createElement('span');
    span.textContent = `#${tag} (${cnt})`;
    chips.appendChild(span);
  });
}

ws.onmessage = (ev)=>{
  const payload = JSON.parse(ev.data);
  const label = new Date().toLocaleTimeString();
  addPoint(label, payload);
}
ws.onopen = ()=>console.log('WS conectado');
ws.onerror = (e)=>console.error('WS error', e);
