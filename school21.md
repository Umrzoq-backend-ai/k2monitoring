# School21 API Endpoints

**Base URL:** `https://platform.21-school.ru/services/21-school/api/v1`

**Auth URL:** `https://auth.21-school.ru/auth/realms/EduPowerKeycloak/protocol/openid-connect/token`

**Auth:** OAuth2 (client_id: `s21-open-api`, grant_type: `password`)

---

## Participants (Foydalanuvchilar)

| # | Endpoint | Tavsif |
|---|----------|--------|
| 1 | `GET /participants/{login}` | Foydalanuvchi haqida asosiy ma'lumot: sinf, level, XP, status |
| 2 | `GET /participants/{login}/logtime` | Kunlik/haftalik logtime — necha soat o'tirganini |
| 3 | `GET /participants/{login}/points` | Ballar: PRP (peer review points), coins |
| 4 | `GET /participants/{login}/coalition` | Qaysi tribe/coalitsiyaga tegishli |
| 5 | `GET /participants/{login}/projects` | Foydalanuvchining loyihalari va ularning holati |
| 6 | `GET /participants/{login}/feedbacks` | Peer review feedback lari |
| 7 | `GET /participants/{login}/achievements` | Erishgan yutuqlari (badgelar) |
| 8 | `GET /participants/{login}/skills` | Skill darajalari (algorithms, unix, web va h.k.) |

---

## Clusters (Klasterlar)

| # | Endpoint | Tavsif |
|---|----------|--------|
| 9 | `GET /clusters` | Barcha klasterlar ro'yxati |
| 10 | `GET /clusters/{id}` | Bitta klaster haqida ma'lumot |
| 11 | `GET /clusters/{id}/map` | Klaster xaritasi — har bir kompyuterda kim o'tirganini ko'rsatadi |

---

## Campuses (Kampuslar)

| # | Endpoint | Tavsif |
|---|----------|--------|
| 12 | `GET /campuses` | Barcha kampuslar ro'yxati (Toshkent, Moskva va h.k.) |
| 13 | `GET /campuses/{id}` | Bitta kampus haqida batafsil |
| 14 | `GET /campuses/{id}/clusters` | Kampusdagi klasterlar |
| 15 | `GET /campuses/{id}/participants` | Kampusdagi barcha foydalanuvchilar |

---

## Projects (Loyihalar)

| # | Endpoint | Tavsif |
|---|----------|--------|
| 16 | `GET /projects` | Barcha mavjud loyihalar ro'yxati |
| 17 | `GET /projects/{id}` | Bitta loyiha haqida: nomi, tavsifi, level talabi |
| 18 | `GET /projects/{id}/participants` | Loyihada ishtirok etayotganlar |

---

## Coalitions (Tribe lar)

| # | Endpoint | Tavsif |
|---|----------|--------|
| 19 | `GET /coalitions` | Barcha coalitionslar ro'yxati |
| 20 | `GET /coalitions/{id}` | Bitta coalition haqida: nomi, score, rangi |
| 21 | `GET /coalitions/{id}/members` | Coalition a'zolari |

---

## Events (Tadbirlar)

| # | Endpoint | Tavsif |
|---|----------|--------|
| 22 | `GET /events` | Kelgusi va o'tgan eventlar ro'yxati |
| 23 | `GET /events/{id}` | Bitta event haqida: vaqti, joyi, tavsifi |
| 24 | `GET /events/{id}/participants` | Eventga yozilganlar |

---

## Feedbacks (Peer Review)

| # | Endpoint | Tavsif |
|---|----------|--------|
| 25 | `GET /feedbacks` | Barcha feedbacklar |
| 26 | `GET /feedbacks/{id}` | Bitta feedback batafsil |

---

## Notifications (Bildirishnomalar)

| # | Endpoint | Tavsif |
|---|----------|--------|
| 27 | `GET /notifications` | Joriy foydalanuvchining bildirshnomalari |

---

## Eslatma

> Bu ro'yxat to'liq rasmiy hujjatga asoslanmagan. School21 platformasi 42 Network asosida qurilgan va API yopiq hisoblanadi. Ba'zi endpointlar mavjud bo'lmasligi yoki boshqacha ishlashi mumkin. To'liq ro'yxatni bilish uchun browser DevTools → Network tab orqali platformani ishlatib, so'rovlarni kuzatish tavsiya etiladi.
