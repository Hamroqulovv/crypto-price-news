# Crypto Bot — Joylashtirish bo'yicha qo'llanma (O'zbek)

Bu fayl loyihani serverga joylashtirish uchun qadam-baqadam koʻrsatmalarni o'z ichiga oladi. Docker yordamida ishga tushirish tavsiya etiladi (kodga o'zgartirishsiz).

---

## 🔰 Talablar
- Server (Ubuntu 20.04+ tavsiya etiladi)
- Docker va Docker Compose plagin yoki `docker-compose` (docker compose plugin)
- Loyihaning ildizida `.env` fayli mavjud bo'lishi kerak ( `.env.example` dan nusxa olib to'ldiring )

---

## ⚙️ Docker o'rnatish (Ubuntu - tavsiya qilingan usul)
1) Asosiy paketlarni o'rnating:
```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release
```

2) Docker GPG kaliti va ruxsatnomani qo'shing:
```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

3) Docker paketlarini o'rnating:
```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

4) Docker xizmatini ishga tushiring va avtomatik yoqing:
```bash
sudo systemctl enable --now docker
```

5) Docker-ni parolsiz ishlatish uchun foydalanuvchini `docker` guruhiga qo'shing (ixtiyoriy):
```bash
sudo usermod -aG docker $USER
# Keyin qayta login qiling yoki yangi sessiyani boshlang:
newgrp docker
```

6) Tekshirish:
```bash
docker --version
docker run --rm hello-world
docker compose version
```

---

## 🟡 Tez va oddiy (agar rasmiy yo'l murakkab bo'lsa)
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
newgrp docker
```

---

## ✅ Loyihani Docker bilan ishga tushirish
1) `.env.example` dan nusxa olib `.env` faylini toʻldiring:
```bash
cp .env.example .env
# .env faylini tahrirlab qiymatlarni kiriting: BOT_TOKEN, PRIMARY_ADMIN, ADMINS
```

2) Docker Compose (tavsiya):
```bash
# Loyihaning ildizida (crypto_bot/):
docker compose up -d --build
```

3) Agar compose ishlamayotgan bo'lsa yoki siz faqat Docker ishlatmoqchi bo'lsangiz:
```bash
docker build -t crypto-bot:latest .
docker run -d --name crypto-bot --env-file .env \
  -v "$(pwd)/main.db:/app/main.db" \
  -v "$(pwd)/data:/app/data" \
  --restart unless-stopped \
  crypto-bot:latest
```

> Eslatma: `main.db` fayli hostga mount qilinganligi sababli ma'lumotlar konteyner qayta ishga tushirilganda ham saqlanadi.

---

## 🔍 Xizmat va loglarni tekshirish
- Docker xizmat holatini tekshirish (agar systemd bilan o'rnatilgan bo'lsa):
```bash
sudo systemctl status docker
```

- Docker daemon haqida ma'lumot:
```bash
docker info
```

- Ishlayotgan konteynerlar:
```bash
docker ps -a
```

- Docker Compose konteynerlari:
```bash
docker compose ps
```

- Live logs:
```bash
docker compose logs -f
# yoki
docker logs -f crypto-bot
```

---

## 🧾 Systemd orqali xizmat sifatida ishga tushirish (opsional)
Agar siz VMda systemd bilan doimiy xost qilishni xohlasangiz, `deploy/crypto-bot.service` namunaviy faylni `/etc/systemd/system/crypto-bot.service` ga joylashtiring va kerakli yoʻllarni yangilang. Keyin:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now crypto-bot
sudo systemctl status crypto-bot
# Loglarni ko'rish
journalctl -u crypto-bot -f
```

---

## 💾 SQLite va zaxira
- Agar siz Docker yoki systemd yordamida botni joylashtirsangiz, `main.db` faylini doimiy host katalogiga mount qiling (yuqoridagi `-v` opsiyasi). Bu SQLite faylni konteyner o'chirilganda yo'qolishidan saqlaydi.
- Zaxira qilish: cron yordamida muntazam nusxa oling, masalan:
```bash
0 3 * * * cp /path/to/crypto_bot/main.db /path/to/backups/main.db_$(date +\%F)
```

---

## ℹ️ Muhim eslatmalar
- Cloud Run yoki Heroku kabi platformalarda fayl tizimi ephemeraldir — SQLite mos emas. Agar siz bulut xizmatida barqaror ishlashni xohlasangiz, tashqi DB (Postgres) ga o'tish va kodni moslashtirish tavsiya etiladi.
- Doimiy monitoring va loglarni saqlashni tashkil qiling.

---

Agar xohlasangiz, men:
- `DEPLOY_UZ.md` ni qo'shdim — kerak bo'lsa uni kengaytirib, qo'shimcha ssenariylar (firewall, reverse proxy, SSL, webhook) ham yozib beraman.
- Serverga Docker o'rnatish yoki `docker compose up` buyruqlarini men bilan bosqichma-bosqich bajarishingiz mumkin — xatolik yuz bersa, chiqishini bu yerga yuboring, men tahlil qilib yordam beraman.

