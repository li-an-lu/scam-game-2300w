// 匿名統計：只收事件種類與 localStorage 隨機 ID（不存 IP、不做指紋）
import { getStore } from '@netlify/blobs';
const OK = new Set(['start', 'share']);
export default async (req) => {
  if (req.method !== 'POST') return new Response('', { status: 405 });
  try {
    const b = await req.json().catch(() => ({}));
    const ev = String(b.e || ''), id = String(b.id || '').replace(/[^a-z0-9]/gi, '').slice(0, 32);
    if (!OK.has(ev)) return new Response('', { status: 400 });
    const st = getStore('stats'), day = new Date(Date.now() + 8 * 3600e3).toISOString().slice(0, 10);   // 台北日期
    const inc = async k => { const v = (await st.get(k, { type: 'json' })) || 0; await st.setJSON(k, v + 1); };
    await inc(`total/${ev}`); await inc(`day/${day}/${ev}`);
    if (ev === 'start' && id && +b.n >= 2) {   // 開第 2 局以上的匿名裝置（同一 ID 只算一次）
      if (!(await st.get(`repeat/${id}`))) { await st.set(`repeat/${id}`, '1'); await inc('total/repeat_devices'); await inc(`day/${day}/repeat_devices`); }
    }
    if (ev === 'start' && id && +b.n === 1) { await inc('total/devices'); await inc(`day/${day}/devices`); }
    return new Response(null, { status: 204 });
  } catch (e) { return new Response(null, { status: 204 }); }
};
export const config = { path: '/api/track' };
