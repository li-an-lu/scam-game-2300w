// 私人統計：需 Authorization: Bearer <STATS_TOKEN>（Netlify 環境變數）
import { getStore } from '@netlify/blobs';
import { timingSafeEqual } from 'node:crypto';
const eq = (a, b) => { const x = Buffer.from(a), y = Buffer.from(b); return x.length === y.length && timingSafeEqual(x, y); };
export default async (req) => {
  const want = process.env.STATS_TOKEN || '', got = (req.headers.get('authorization') || '').replace(/^Bearer\s+/i, '');
  if (!want || !eq(got, want)) return new Response('unauthorized', { status: 401 });
  const st = getStore('stats'), out = { total: {}, days: {} };
  const { blobs } = await st.list({ prefix: 'total/' });
  for (const b of blobs) out.total[b.key.slice(6)] = await st.get(b.key, { type: 'json' });
  const d = await st.list({ prefix: 'day/' });
  for (const b of d.blobs) { const [, day, k] = b.key.split('/'); (out.days[day] ||= {})[k] = await st.get(b.key, { type: 'json' }); }
  return Response.json(out, { headers: { 'cache-control': 'no-store' } });
};
export const config = { path: '/api/stats' };
