# 🚀 دليل نشر البوت على DigitalOcean

## 📋 الخطوات الكاملة (15 دقيقة)

---

## 1️⃣ إنشاء Droplet

### في موقع DigitalOcean:

1. اذهب إلى [DigitalOcean Console](https://cloud.digitalocean.com)
2. اضغط **Create** → **Droplets**
3. **اختر المواصفات:**
   ```
   Image: Ubuntu 22.04 LTS (أو أحدث)
   Plan: Basic
   CPU Options: Regular (Shared CPU)
   Size: $6/month (1GB RAM, 1 vCPU) ← كافي جداً!
   Datacenter: اختر الأقرب لك
   Authentication: SSH Key (أفضل) أو Password
   Hostname: crypto-killer-bot
   ```
4. اضغط **Create Droplet**
5. انتظر 1-2 دقيقة حتى يصبح جاهزاً
6. **احفظ IP Address** (مثال: 159.89.123.45)

---

## 2️⃣ الاتصال بالسيرفر

### من جهازك (Terminal):

```bash
# استبدل YOUR_IP بالـ IP الفعلي
ssh root@YOUR_IP

# إذا طلب تأكيد، اكتب yes
# ثم أدخل الـ Password إذا لم تستخدم SSH Key
```

---

## 3️⃣ تثبيت Python والمتطلبات

### نسخ هذه الأوامر في السيرفر:

```bash
# تحديث النظام
apt update && apt upgrade -y

# تثبيت Python و pip و git
apt install -y python3 python3-pip git screen

# التأكد من الإصدار
python3 --version  # يجب أن يكون 3.9+
```

---

## 4️⃣ رفع ملفات البوت

### لديك 3 خيارات:

#### **الخيار A: باستخدام Git (الأسهل):**

```bash
# في السيرفر
cd /root
git clone https://github.com/saleemoov/try4.git
cd try4
```

#### **الخيار B: باستخدام scp (من جهازك):**

```bash
# في جهازك (ليس السيرفر)
cd /workspaces/try4
scp crypto_killer_bot.py trading_config.json requirements.txt root@YOUR_IP:/root/
```

#### **الخيار C: نسخ يدوي:**

```bash
# في السيرفر - إنشاء المجلد
mkdir -p /root/crypto_killer
cd /root/crypto_killer

# ثم انسخ المحتوى يدوياً باستخدام nano
nano crypto_killer_bot.py
# (الصق الكود، Ctrl+X, Y, Enter)

nano trading_config.json
# (الصق الإعدادات، Ctrl+X, Y, Enter)
```

---

## 5️⃣ تثبيت المكتبات المطلوبة

```bash
# في السيرفر
cd /root/try4  # أو /root/crypto_killer

# تثبيت المكتبات
pip3 install ccxt pandas numpy requests python-dotenv
```

---

## 6️⃣ اختبار البوت

```bash
# تشغيل تجريبي للتأكد
python3 crypto_killer_bot.py

# إذا ظهرت رسائل مثل:
# "💀 Crypto Killer Bot initialized!"
# "🚀 Starting main loop..."
# "✅ Found 22 symbols"
# 
# معناها: يعمل! ✅
# 
# اضغط Ctrl+C لإيقافه
```

---

## 7️⃣ إنشاء Systemd Service (تشغيل دائم)

### هذا يضمن:
- ✅ البوت يعمل دائماً
- ✅ يعيد التشغيل تلقائياً عند السقوط
- ✅ يبدأ تلقائياً عند إعادة تشغيل السيرفر

```bash
# في السيرفر - إنشاء ملف الخدمة
nano /etc/systemd/system/crypto-killer.service
```

### الصق هذا المحتوى:

```ini
[Unit]
Description=Crypto Killer Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/try4
ExecStart=/usr/bin/python3 -u /root/try4/crypto_killer_bot.py
Restart=always
RestartSec=10
StandardOutput=append:/root/try4/crypto_killer.log
StandardError=append:/root/try4/crypto_killer.log

[Install]
WantedBy=multi-user.target
```

**احفظ:** `Ctrl+X` → `Y` → `Enter`

---

## 8️⃣ تفعيل وبدء الخدمة

```bash
# تحديث systemd
systemctl daemon-reload

# تفعيل البوت (يبدأ تلقائياً عند الإقلاع)
systemctl enable crypto-killer

# بدء البوت الآن
systemctl start crypto-killer

# التحقق من الحالة
systemctl status crypto-killer
```

### يجب أن ترى:
```
● crypto-killer.service - Crypto Killer Trading Bot
   Loaded: loaded (/etc/systemd/system/crypto-killer.service)
   Active: active (running) ✅
   ...
```

---

## 9️⃣ المراقبة والإدارة

### أوامر مهمة:

```bash
# مراقبة السجل مباشرة (live)
tail -f /root/try4/crypto_killer.log

# إيقاف البوت
systemctl stop crypto-killer

# إعادة تشغيل البوت
systemctl restart crypto-killer

# التحقق من الحالة
systemctl status crypto-killer

# عرض آخر 50 سطر من السجل
tail -50 /root/try4/crypto_killer.log
```

---

## 🔟 اختبار التشغيل المستمر

```bash
# 1. تأكد أن البوت يعمل
systemctl status crypto-killer

# 2. اخرج من السيرفر
exit

# 3. بعد 5 دقائق، عد للسيرفر
ssh root@YOUR_IP

# 4. تحقق من السجل
tail -20 /root/try4/crypto_killer.log

# يجب أن ترى رسائل جديدة ✅
```

---

## 🎯 نصائح مهمة

### 1. **الأمان:**

```bash
# إنشاء مستخدم غير root (أفضل)
adduser cryptobot
usermod -aG sudo cryptobot

# تعديل ملف الخدمة لاستخدام المستخدم الجديد
nano /etc/systemd/system/crypto-killer.service
# غيّر: User=root إلى User=cryptobot
# غيّر: WorkingDirectory=/root/try4 إلى /home/cryptobot/try4
```

### 2. **Firewall:**

```bash
# تفعيل Firewall
ufw allow OpenSSH
ufw enable
```

### 3. **التحديثات:**

```bash
# تحديث الكود
cd /root/try4
git pull  # إذا استخدمت git
systemctl restart crypto-killer
```

### 4. **Backup:**

```bash
# نسخ احتياطي للإعدادات
cp trading_config.json trading_config.json.backup
```

---

## 🔥 استكشاف الأخطاء

### البوت لا يعمل؟

```bash
# 1. تحقق من السجلات
journalctl -u crypto-killer -n 50

# 2. تحقق من الأخطاء
tail -50 /root/try4/crypto_killer.log

# 3. اختبر يدوياً
cd /root/try4
python3 crypto_killer_bot.py
```

### أخطاء شائعة:

#### ❌ ModuleNotFoundError: No module named 'ccxt'
```bash
# الحل:
pip3 install ccxt pandas numpy requests
```

#### ❌ trading_config.json not found
```bash
# الحل:
cd /root/try4
ls -la  # تحقق من وجود الملف
```

#### ❌ Permission denied
```bash
# الحل:
chmod +x /root/try4/crypto_killer_bot.py
```

---

## 📊 المراقبة المتقدمة (اختياري)

### إنشاء سكربت مراقبة:

```bash
nano /root/monitor.sh
```

```bash
#!/bin/bash
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💀 Crypto Killer Bot Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
systemctl status crypto-killer | head -10
echo ""
echo "📊 Last 10 log lines:"
tail -10 /root/try4/crypto_killer.log
echo ""
echo "💾 Disk Usage:"
df -h | grep -E '^/dev/'
echo ""
echo "🧠 Memory Usage:"
free -h
```

```bash
chmod +x /root/monitor.sh
./monitor.sh  # لعرض حالة البوت
```

---

## ✅ Checklist النهائي

قبل أن تغلق:

- [ ] البوت يعمل: `systemctl status crypto-killer`
- [ ] السجل ينمو: `tail -f /root/try4/crypto_killer.log`
- [ ] التنبيهات تصل على Telegram ✅
- [ ] البوت يعيد التشغيل تلقائياً: `systemctl restart crypto-killer`
- [ ] يبدأ بعد إعادة تشغيل السيرفر: `systemctl is-enabled crypto-killer`

---

## 🎉 تم!

البوت الآن يعمل 24/7 على DigitalOcean!

**للدعم:**
- السجلات: `/root/try4/crypto_killer.log`
- الحالة: `systemctl status crypto-killer`
- إعادة تشغيل: `systemctl restart crypto-killer`

💀 **Crypto Killer is Alive!**
