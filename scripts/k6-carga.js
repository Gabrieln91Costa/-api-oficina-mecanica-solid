import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '60s', target: 40 },
    { duration: '60s', target: 80 },
    { duration: '30s', target: 0 },
  ],
  thresholds: { http_req_failed: ['rate<0.05'], http_req_duration: ['p(95)<1500'] },
};

export default function () {
  const base = __ENV.BASE_URL || 'http://localhost:8000';
  const response = http.get(`${base}/api/v1/ordens-servico`);
  check(response, { 'listagem operacional 200': (r) => r.status === 200 });
  sleep(0.2);
}
