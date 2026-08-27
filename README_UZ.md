# TARIX360 — FIRST10

Maktab o‘qituvchisi uchun tarix darsini xarita, timeline, voqea, marshrut, rasm va darslik beti bilan bitta sinxron scene sifatida ko‘rsatadigan frontend.

## Lokal ishga tushirish

`START_LOCAL.bat` yoki `START_LOCAL.ps1` ni ishga tushiring va `http://localhost:8081` ni oching. Frontend localhost’da `data/` va `assets/` ichidagi tayyor static snapshotdan foydalanadi. Browser Google Drive’dan loyiha ZIP’ini yuklamaydi.

## Asosiy bog‘lanish

```text
topic_config_10.json
  → topics[].showFeatureIds
  → master_all_features.geojson
  → yil bo‘yicha active feature filtri
  → davlat / shahar / voqea / route / thematic map layerlari
```

Rasmlar `media_manifest.json` orqali mavzuga ulanadi. `web_content_manifest.json` esa har bir lokal runtime yo‘lini authoritative Google Drive file ID bilan bog‘laydi.

## Runtime rejimlari

- `localhost`: `local-static`; tayyor dataset va media shu papkadan ochiladi.
- `Vercel/public host`: `drive-api`; frontend `/api/content?path=...` orqali faqat kerakli bitta faylni oladi.
- Drive OAuth ma’lumotlari frontendga yozilmaydi. Ular faqat Vercel environment variables’da turadi.

Vercel uchun kerakli server secretlari:

```text
GOOGLE_DRIVE_CLIENT_ID
GOOGLE_DRIVE_CLIENT_SECRET
GOOGLE_DRIVE_REFRESH_TOKEN
```

Vaqtinchalik server sessiyasi uchun `GOOGLE_DRIVE_ACCESS_TOKEN` ham qo‘llanadi, lekin production’da refresh token usuli barqarorroq.

## Drive tuzilmasi

- Dataset: `TARIX360/08_WEB_DATA_FIRST10`
- Media: `TARIX360/09_WEB_MEDIA_FIRST10`
- Media ichida: `generated/`, `source/topic_01...topic_10`, `manifests/`
- Runtime manifest: `data/web_content_manifest.json`

ZIP faqat arxiv/backup. U web runtime ro‘yxatiga kiritilmagan.

Yangi lokal muhitda Drive snapshotni tiklash:

```powershell
python scripts/sync_drive_assets.py
```

Utilita faqat yetishmayotgan fayllarni yaratadi va mavjud faylni almashtirmaydi. Avval ro‘yxatni ko‘rish uchun `--dry-run` ishlatiladi.

## PDF va yengil sahifa viewer

192 betlik sifatli original PDF Drive’da saqlanadi. FIRST10 uchun 8–93-betlar 1440 px WebP sahifalarga ajratilgan va `web_pages_first10` papkasiga yuklangan.

- Browser 145 MB PDF’ni avtomatik yuklamaydi.
- Mavzu tanlanganda faqat uning birinchi sahifasi ochiladi.
- Faqat oldingi va keyingi sahifa oldindan keshlanadi.
- To‘liq original alohida `To‘liq PDF` havolasi bilan ochiladi.
- Sahifa ↔ Drive file ID bog‘lanishi `data/book_pages_manifest.json`da saqlanadi.

## GitHub tarkibi

GitHub/Vercel’da frontend kodi, Leaflet vendor fayllari, serverless gateway va Drive manifest saqlanadi. Katta PDF, rasm va GeoJSON snapshotlar `.gitignore` orqali repoga kiritilmaydi; ularning authoritative nusxasi Drive’da qoladi.

## Tekshiruv qoidasi

Bu loyihada avtomatik test yozilmaydi va agent browser regression testini bajarmaydi. Real tekshiruvni loyiha egasi localhost’da o‘zi bajaradi.
