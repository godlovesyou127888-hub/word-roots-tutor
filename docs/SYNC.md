# Word Roots Tutor — 資料與同步說明

## 1. 主要資料集中地

```
C:\Users\salek\word-roots-tutor\
  data\
    roots.json          ← 主要字根資料，含 100 個字根
    progress.json       ← CLI 模式的進度記錄
  src\
    main.py             ← CLI 互動式練習程式
  web\
    index.html          ← 瀏覽器大字版畫面
    roots.json          ← 供網頁版使用的字根資料副本
```

---

## 2. roots.json 的角色

### 目的
記載所有字根的結構化內容，供 CLI 與網頁版共同讀取。

### 必要欄位

| 欄位 | 說明 | 範例 |
|------|------|------|
| `id` | 字根唯一編號 | `"ac-"` |
| `root` | 字根本身 | `"ac"` |
| `pronunciation` | 音標 | `"/æk/"` |
| `meaning` | 字根本義 | `"sharp, bitter"` |
| `origin` | 來源語言或備註 | `"Latin"` |
| `derived` | 衍生詞彙清單 | `["acute", "acrid"]` |
| `example_sentence` | 英文例句 | `"The pain was acute."` |
| `mnemonic` | 英文記憶法 | `"AC → acute"` |
| `quiz` | 練習題目 | `"ac- means what?"` |

### 補充（中英對照版）

| 欄位 | 說明 |
|------|------|
| `example_zh` | 例句中文翻譯 |
| `mnemonic_zh` | 記憶法中譯 |

網頁 UI 會優先顯示英文，再顯示中文；若中文欄位遺失，則自動退回純英文。

---

## 3. data/roots.json vs web/roots.json

### 關係
- `data/roots.json` 是**主要來源**（source of truth）
- `web/roots.json` 是**方便上網時攜帶的副本**
- 兩者資料內容相同，但存放位置不同

### 何時同步

推薦的同步方法：

```bash
# 把 data/roots.json 複製到 web/roots.json
cd C:\Users\salek\word-roots-tutor
cp data/roots.json web/roots.json
```

何時應該執行一次同步：

- 新增、修改或刪除任何字根欄位
- 調整 `example_zh` / `mnemonic_zh`
- 更新衍伸詞或例句
- 每次要上傳到 GitHub 前

### 常見錯誤

- 只改了 `data/roots.json` 卻忘了同步 `web/roots.json`，導致網頁版內容落後。
- 直接改 `web/roots.json` 卻忘了回寫 `data/roots.json`，導致 CLI 與網頁版長期待不同步。

---

## 4. progress.json vs 瀏覽器 localStorage

### 為何分成兩邊

| 位置 | 用途 | 適用場景 |
|------|------|------|
| `data/progress.json` | 記錄 CLI 互動式練習的題目與答題狀態 | 使用 `python src/main.py` |
| 瀏覽器 `localStorage` | 記錄網頁大字版的練習狀態 | 使用 http://localhost:8080 或 GitHub Pages 線上版 |

### 共通格式概念

兩種格式觀念上會記錄：

- 曾經問過的題目 ID
- 最近一次更新時間
- 答對/答錯標記

但兩邊的存取程式碼完全不同：
- `data/progress.json` 由 Python CLI 讀寫
- web 版由 `index.html` 的 JavaScript 讀寫 `localStorage`

### 不會自動同步

這點務必注意：

- CLI 版答題**不會**更新 web 版的進度
- web 版答題**不會**寫入 `data/progress.json`

如果你兩個介面都會用到，建議：
- 先專注用同一種模式一段時間
- 或每次切換模式時執行一次 reset，確保進度基準一致

---

## 5. GitHub Pages 版本注意事項

推上 GitHub Pages 的網頁版只會包含：

```
web/
  index.html
  roots.json
```

所以：

- 它們只會讀到 `web/roots.json`，**不會**讀 `data/roots.json`
- 使用者的進度全存在**自己的瀏覽器** `localStorage`
- 你身為作者無法讀取或重置一般使用者的進度（除非你直接在 repo 內更新 `web/roots.json` 內容）

---

## 6. 例行維護檢查表

建議每一個月或每次內容修改後檢查：

1. `data/roots.json` 與 `web/roots.json` 檔案大小是否一致：
   ```bash
   wc -c C:\Users\salek\word-roots-tutor\data\roots.json
   wc -c C:\Users\salek\word-roots-tutor\web\roots.json
   ```
2. 任一字根內容修改後，立刻執行一次複製同步：
   ```bash
   cp C:\Users\salek\word-roots-tutor\data\roots.json C:\Users\salek\word-roots-tutor\web\roots.json
   ```
3. 網頁版改壞時，可刪除瀏覽器 `localStorage` 從頭 reset

---

## 7. 常見問題快解

**Q：我在 CLI 答了幾題，開網頁版卻像是沒答過？**  
A：正常。兩邊進度分開儲存。

**Q：我改了一個字根的解釋，忘記同步 web 版怎麼辦？**  
A：重新複製一次：`cp data/roots.json web/roots.json`。

**Q：網頁版 localhost 跟 GitHub Pages 的進度會互通嗎？**  
A：不會，它們是**同一台瀏覽器在不同網域**（`localhost` vs `github.io`）各自會產生獨立的 `localStorage`。

**Q：`test` 指令可以跑嗎？**  
A：目前 `src/main.py` 的介面是 Ask / Quiz / Review / List / progress / export / reset，沒有 built-in pytest 或 unit test 框架。`test` 不會被識別。要跑自動化測試需要另外寫測試腳本或接入 pytest。
