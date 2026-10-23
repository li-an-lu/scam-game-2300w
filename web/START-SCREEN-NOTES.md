# 開始頁整合筆記（2026-10-24）

完整預覽：`start-preview-combined.html`

## 建議的 `ui.js` start() 結構參考

```javascript
$('#screen').innerHTML = `
  <div class="start-hero">
    <div class="meta">台灣人生模擬 · 取材自真實資料</div>
    <h1>2300萬<span style="font-size:.55em;color:#a89a94">分之</span><span class="one">1</span></h1>
    <p class="sub">你是其中一個。<br>大多數謊言很小，但有些會變成轉機。</p>
  </div>
  <div class="live-row">
    <div class="live-card">
      <div class="num" id="live-lies">—</div>
      <div class="lbl">打開這個頁面後<br>被說出的小謊</div>
    </div>
    <div class="live-card">
      <div class="num" id="live-cases">—</div>
      <div class="lbl">今天全台約受理<br>的詐騙案件</div>
    </div>
  </div>
  <div class="fact-ticker" id="fact-ticker">多數人一天說 0～2 個謊，其中約 90% 是無傷大雅的小謊。</div>
  <div class="card">
    <!-- 原本的四個數值、勾選、按鈕放這裡 -->
    <button class="primary" id="go">開始這一生 →</button>
  </div>
  <p class="footer">上當的人不笨，往往只是太真誠。</p>
  <div class="shared-section">
    <h2>他們分享的經驗</h2>
    <p class="sub">走完一生的人，留下一句話。</p>
    <div class="carousel" id="exp-carousel"></div>
    <div class="shared-note">目前為預設示範。結局時可留下一句想說的話。</div>
  </div>
`;
```

動態數字與輪播邏輯可參考 `start-preview-combined.html` 內的 script。
