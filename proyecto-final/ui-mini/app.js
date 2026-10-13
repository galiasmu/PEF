// Dashboard: recibe un resumen por ventana desde el backend (WebSocket) y lo grafica.
const WS_URL = 'ws://127.0.0.1:8000/ws/metrics';
const MAX_POINTS = 30;  // solo se muestran las últimas 30 ventanas: la memoria no crece sin límite

// Colores legibles sobre fondo oscuro
Chart.defaults.color = '#c9d1d9';
Chart.defaults.borderColor = '#243044';

const countChart = new Chart(document.getElementById('chartCount'), {
  type: 'line',
  data: {labels: [], datasets: [{label: 'Comentarios', data: [], borderColor: '#58a6ff'}]},
  options: {animation: false, scales: {y: {beginAtZero: true}}},
});

const sentimentChart = new Chart(document.getElementById('chartSent'), {
  type: 'line',
  data: {labels: [], datasets: [
    {label: 'Positivo', data: [], borderColor: '#3fb950'},
    {label: 'Neutral', data: [], borderColor: '#8b949e'},
    {label: 'Negativo', data: [], borderColor: '#f85149'},
  ]},
  options: {animation: false, scales: {y: {min: 0, max: 1}}},
});

const trendChart = new Chart(document.getElementById('chartTrend'), {
  type: 'bar',
  data: {labels: [], datasets: [{label: 'Menciones', data: [], backgroundColor: '#a371f7'}]},
  options: {animation: false, indexAxis: 'y', plugins: {legend: {display: false}}},
});

// Agrega un punto al final del gráfico y descarta el más viejo si se pasa de MAX_POINTS.
function pushPoint(chart, label, values) {
  chart.data.labels.push(label);
  chart.data.datasets.forEach((dataset, i) => dataset.data.push(values[i]));
  if (chart.data.labels.length > MAX_POINTS) {
    chart.data.labels.shift();
    chart.data.datasets.forEach((dataset) => dataset.data.shift());
  }
  chart.update();
}

function showSummary(summary) {
  const label = new Date().toLocaleTimeString();
  const s = summary.avg_sentiment;
  pushPoint(countChart, label, [summary.total_comments]);
  pushPoint(sentimentChart, label, [s.positive, s.neutral, s.negative]);

  trendChart.data.labels = summary.trending.map(([tag]) => '#' + tag);
  trendChart.data.datasets[0].data = summary.trending.map(([, count]) => count);
  trendChart.update();

  const chips = summary.top_hashtags.map(([tag, count]) => {
    const span = document.createElement('span');
    span.textContent = `#${tag} (${count})`;  // textContent: el texto nunca se interpreta como HTML
    return span;
  });
  document.getElementById('chips').replaceChildren(...chips);
}

function connect() {
  const status = document.getElementById('status');
  const ws = new WebSocket(WS_URL);
  // El primer resumen llega recién cuando se cierra la primera ventana (WINDOW_SECONDS).
  ws.onopen = () => { status.textContent = 'Conectado, esperando la primera ventana...'; };
  ws.onmessage = (event) => {
    status.textContent = 'Conectado';
    showSummary(JSON.parse(event.data));
  };
  ws.onclose = () => {
    status.textContent = 'Sin conexión, reintentando...';
    setTimeout(connect, 3000);  // si el backend se reinicia, el dashboard se reconecta solo
  };
}

connect();
