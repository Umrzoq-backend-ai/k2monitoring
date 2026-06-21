# School21 Monitoring & Analytics Platform

## Maqsad

School21 (42 Network) platformasi uchun **to'liq monitoring va analitika tizimi** yaratish.
Barcha ma'lumotlar **shajara daraxti** ko'rinishida — klasterlar, peerlar, loyihalar, 
coalitions, logtime — hammasini real-time'da ko'rish va tahlil qilish imkoniyati.

Bu tizim School21 jamoasiga quyidagilarni beradi:
- Klaster bandligini real-time monitoring
- Peer'larni qidirish va ularning to'liq profilini ko'rish
- Loyihalar statistikasi va tahlili
- Skills reytingi va taqqoslash
- Campus bo'ylab umumiy ko'rsatkichlar

---

## Arxitektura

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐   ┌──────────────────────────────────┐   │
│  │  Tree Panel  │   │         Detail Panel              │   │
│  │  (shajara)   │   │  Profile | Skills | Projects     │   │
│  │             │   │  Cluster Map | Stats | Compare    │   │
│  └─────────────┘   └──────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    API LAYER (Next.js API Routes)            │
│  - OAuth2 token management (auto-refresh)                   │
│  - Request caching (1 min TTL)                              │
│  - Error handling & retry                                   │
├─────────────────────────────────────────────────────────────┤
│                    SCHOOL21 API                              │
│  platform.21-school.ru/services/21-school/api/v1            │
└─────────────────────────────────────────────────────────────┘
```

---

## Fazalar

### Faza 1: Core Infrastructure ✅
- [x] Next.js + TypeScript + Tailwind
- [x] API auth (OAuth2 token caching)
- [x] API proxy route
- [x] Project structure & conventions

### Faza 2: Tree Explorer ✅
- [x] Recursive tree component (lazy loading)
- [x] Tashkent & Samarkand kampuslar
- [x] Klasterlar → Cluster Map → Peerlar hierarchy
- [x] Peer search
- [x] Detail panel with specialized views

### Faza 3: Enhanced Detail Views 🔄
- [ ] Cluster Map vizual grid (haqiqiy joy joylashuvi)
- [ ] Peer comparison (2+ peer skill/xp taqqoslash)
- [ ] Logtime haftalik grafik (chart)
- [ ] Projects timeline view
- [ ] Coalition leaderboard

### Faza 4: Dashboard & Analytics
- [ ] Dashboard page (umumiy statistika)
  - Kampuslardagi jami peerlar soni
  - Hozirgi paytda klasterlardagi band joylar
  - Top 10 peer by XP
  - Skills distribution chart
- [ ] Real-time cluster occupancy monitor
- [ ] Heatmap (qaysi soatlarda klaster band)

### Faza 5: Advanced Features
- [ ] Notifications system (peer keldi/ketdi)
- [ ] Favorites (sevimli peerlar)
- [ ] Export (PDF/CSV reports)
- [ ] Multi-language (uz/ru/en)
- [ ] Mobile responsive (PWA)
- [ ] Dark/Light theme

---

## Ishlayotgan API Endpoints

| Endpoint | Status | Tavsif |
|----------|--------|--------|
| `participants/{login}` | ✅ | Profil (level, XP, class, status) |
| `participants/{login}/logtime` | ✅ | Logtime (soat raqami) |
| `participants/{login}/points` | ✅ | PRP, coins, code review points |
| `participants/{login}/projects` | ✅ | Loyihalar ro'yxati |
| `participants/{login}/skills` | ✅ | Skills + points |
| `participants/{login}/coalition` | ✅ | Coalition nomi, rank |
| `campuses` | ✅ | Barcha kampuslar |
| `campuses/{id}` | ✅ | Kampus detali |
| `campuses/{id}/clusters` | ✅ | Kampus klasterlari |
| `campuses/{id}/participants` | ✅ | Kampus peerlari |
| `clusters/{id}` | ✅ | Klaster info |
| `clusters/{id}/map` | ✅ | Kim qayerda o'tirgan |
| `coalitions` | ❌ 404 | |
| `events` | ❌ 400 | |
| `notifications` | ❌ 404 | |
| `participants/{login}/achievements` | ❌ 404 | |
| `participants/{login}/feedbacks` | ❌ 404 | |

---

## Fayl strukturasi

```
app/
├── api/
│   ├── auth/route.ts              — Token management
│   └── school21/route.ts          — API proxy
├── components/
│   ├── tree/
│   │   ├── tree-node.tsx          — Recursive node
│   │   └── tree-panel.tsx         — Left panel + search
│   ├── detail/
│   │   ├── detail-panel.tsx       — Right panel router
│   │   └── views/
│   │       ├── profile-card.tsx   — User profile
│   │       ├── skills-chart.tsx   — Skills bars
│   │       ├── projects-list.tsx  — Projects filter
│   │       ├── points-card.tsx    — Points stats
│   │       └── generic-view.tsx   — Fallback
│   └── ui/
│       └── spinner.tsx
├── lib/
│   ├── types.ts                   — Interfaces
│   ├── constants.ts               — IDs, config
│   ├── api.ts                     — Fetch + cache
│   ├── tree-builder.ts            — Static tree
│   └── tree-resolver.ts           — Dynamic loading
├── globals.css
├── layout.tsx
└── page.tsx
```

---

## Texnik qarorlar

| Savol | Javob |
|-------|-------|
| Nima uchun Next.js? | Server-side token, API routes, production-ready |
| Nima uchun shajara? | Eng qulay navigation — VS Code style |
| State management? | React hooks (useState/useCallback) — oddiy, yetarli |
| Styling? | Tailwind — tez, consistent, dark-theme qulay |
| Caching? | In-memory Map (client) + token cache (server) |
