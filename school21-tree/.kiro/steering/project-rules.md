---
inclusion: auto
---

# School21 Explorer — Loyiha Qoidalari

## Loyiha haqida

Bu **School21 Analytics Platform** — School21 (42 Network) platformasining barcha ma'lumotlarini
**shajara daraxti (tree view)** ko'rinishida interaktiv ko'rsatadigan Next.js veb-ilovasi.

## Arxitektura

- **Framework**: Next.js 16 (App Router, TypeScript, Tailwind CSS)
- **Backend**: Next.js API Routes (proxy — School21 API ga so'rov yuboradi)
- **Auth**: OAuth2 token caching (server-side)
- **UI Pattern**: File Explorer / Tree View (VS Code, Figma Layers panel kabi)

## UI Konseptsiya — SHAJARA DARAXTI

Sayt **chap panelda shajara (tree)**, **o'ng panelda tanlangan element ma'lumoti** ko'rinishida ishlaydi.
Huddi **VS Code file explorer** yoki **Figma layers panel** kabi:

```
┌─────────────────────┬──────────────────────────────────┐
│  🌳 SHAJARA         │  📋 TANLANGAN ELEMENT            │
│                     │                                  │
│  ▼ 🏫 Kampuslar    │  Login: rrangesi                 │
│    ▼ Tashkent      │  Level: 7                        │
│      ▼ Klasterlar  │  XP: 12,450                      │
│        ▼ Tillakori │  Status: Active                  │
│          🧑‍💻 peer1 │  ...                             │
│          🧑‍💻 peer2 │                                  │
│        ▶ Samarkand │                                  │
│    ▶ Moskva        │                                  │
│  ▼ ⚔️ Coalitions   │                                  │
│    ▶ Red Hawks     │                                  │
│    ▶ Blue Foxes    │                                  │
│  ▼ 👤 Profilim     │                                  │
│    📋 Info          │                                  │
│    ⏱️ Logtime       │                                  │
│    🎯 Skills       │                                  │
└─────────────────────┴──────────────────────────────────┘
```

### Shajara qoidalari:
1. **Lazy loading** — node ochilganda API dan bolalar yuklanadi
2. **Infinite depth** — cheksiz chuqurlikda ochilishi mumkin
3. **Click = tanlash** — leaf node bosilganda o'ng panelda ma'lumot chiqadi
4. **Expand/Collapse** — branch node bosilganda bolalari ochiladi/yopiladi
5. **Animatsiya** — smooth open/close transitions
6. **Vertical lines** — daraxt shoxlari ko'rsatiladi (indentation + line)

### Shajara strukturasi:
```
🌳 School 21
├── 👤 Mening Profilim
│   ├── 📋 Asosiy ma'lumot (leaf → detail)
│   ├── ⏱️ Logtime (leaf → detail)
│   ├── 💰 Ballar (leaf → detail)
│   ├── 📁 Loyihalar (leaf → detail)
│   ├── 🎯 Skills (leaf → detail)
│   ├── 🏆 Achievements (leaf → detail)
│   ├── 🏛️ Coalition (leaf → detail)
│   └── 💬 Feedbacks (leaf → detail)
├── 🏫 Kampuslar (API dan yuklanadi)
│   ├── Tashkent (campus)
│   │   ├── 📋 Ma'lumot (leaf)
│   │   ├── 🖥️ Klasterlar (API dan yuklanadi)
│   │   │   ├── Tillakori
│   │   │   │   ├── 📋 Ma'lumot (leaf)
│   │   │   │   └── 🗺️ Cluster Map (API → peerlar ro'yxati)
│   │   │   │       ├── 🧑‍💻 J3-rrangesi (peer node)
│   │   │   │       │   ├── 📋 Info
│   │   │   │       │   ├── 🎯 Skills
│   │   │   │       │   └── ...
│   │   │   │       └── 🧑‍💻 A1-someone
│   │   │   └── Samarkand
│   │   └── 👥 Peerlar (API → peer ro'yxati)
│   └── Moskva
├── ⚔️ Coalitions (API dan yuklanadi)
│   ├── Red Hawks
│   │   ├── 📋 Ma'lumot (leaf)
│   │   └── 👥 A'zolari (peer ro'yxati)
│   └── Blue Foxes
├── 📅 Eventlar (leaf → detail)
├── 📚 Barcha Loyihalar (leaf → detail)
└── 🔔 Bildirishnomalar (leaf → detail)
```

## Kod standartlari

1. **TypeScript strict** — barcha turlar aniq bo'lishi kerak
2. **Komponentlar kichik va focused** — bitta komponent bitta ish qiladi
3. **Server Components vs Client Components** — faqat interaktiv qismlarga 'use client'
4. **Error handling** — har bir API chaqiruv try/catch bilan
5. **Loading states** — har bir yuklanish skeleton/spinner bilan
6. **Responsive** — mobile'da ham ishlashi kerak (tree collapse)
7. **Accessibility** — keyboard navigation, aria-labels
8. **Performance** — React.memo, lazy loading, no unnecessary re-renders

## Fayl strukturasi

```
app/
├── api/
│   ├── auth/route.ts          — Token olish va caching
│   └── school21/route.ts      — API proxy (GET ?endpoint=...)
├── components/
│   ├── Tree/
│   │   ├── TreeView.tsx       — Asosiy tree container
│   │   ├── TreeNode.tsx       — Bitta tree node (recursive)
│   │   └── TreeLine.tsx       — Vertical/horizontal connecting lines
│   ├── Detail/
│   │   ├── DetailPanel.tsx    — O'ng panel container
│   │   ├── KeyValueView.tsx   — Object display
│   │   ├── TableView.tsx      — Array/table display
│   │   └── StatCard.tsx       — Stat card (level, XP, etc)
│   ├── Layout/
│   │   ├── AppShell.tsx       — Main layout (tree + detail)
│   │   ├── TopBar.tsx         — Search, user info
│   │   └── SearchInput.tsx    — Peer search
│   └── ui/
│       ├── Spinner.tsx
│       ├── ErrorState.tsx
│       └── EmptyState.tsx
├── lib/
│   ├── api.ts                 — Client-side fetch helper
│   └── tree-nodes.ts          — Node type definitions & builders
├── globals.css
├── layout.tsx
└── page.tsx
```

## API Endpoints (School21)

Base: `https://platform.21-school.ru/services/21-school/api/v1`

- `GET /participants/{login}` — profil
- `GET /participants/{login}/logtime` — logtime
- `GET /participants/{login}/points` — ballar
- `GET /participants/{login}/coalition` — coalition
- `GET /participants/{login}/projects` — loyihalar
- `GET /participants/{login}/skills` — skills
- `GET /participants/{login}/achievements` — yutuqlar
- `GET /participants/{login}/feedbacks` — feedbacks
- `GET /campuses` — kampuslar ro'yxati
- `GET /campuses/{id}` — bitta kampus
- `GET /campuses/{id}/clusters` — kampus klasterlari
- `GET /campuses/{id}/participants` — kampus peerlari
- `GET /clusters/{id}` — bitta klaster
- `GET /clusters/{id}/map` — klaster xaritasi (kim qayerda)
- `GET /coalitions` — coalitions ro'yxati
- `GET /coalitions/{id}` — bitta coalition
- `GET /coalitions/{id}/members` — coalition a'zolari
- `GET /events` — eventlar
- `GET /notifications` — bildirishnomalar
- `GET /projects` — barcha loyihalar

## Rang sxemasi

- Background: `#0a0e1a` (dark navy)
- Surface: `#111827` (gray-900)
- Primary: `emerald-400` (#34d399)
- Text: `gray-200`, `gray-400`
- Tree lines: `gray-700`
- Hover: `white/5`
- Selected: `emerald-500/15` border-left emerald

## Xavfsizlik

- API credentials faqat server-side (.env.local)
- Client hech qachon to'g'ridan-to'g'ri School21 API ga murojaat qilmaydi
- Token caching server-side
