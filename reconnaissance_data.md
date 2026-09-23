# بيانات الاستطلاع الأولي - المرحلة الأولى
## Raw Reconnaissance Data

| الأداة | الحالة | النتائج |
|--------|--------|---------|
| curl/wget | ✅ متاح | جميع الطلبات الأولية |
| Nmap | ✅ مثبت | فحص المنافذ والخدمات |
| Nikto | ✅ مثبت | فحص ثغرات الويب |
| SQLMap | ✅ مثبت | فحص SQL Injection |
| Dirb | ✅ مثبت | فحص المجلدات |
| Whatweb | ✅ مثبت | بصمة التقنيات |

---

# نتيجة Nmap - الفحص الشامل (الملف النصي)

```
Host: kuraimibank.com (78.141.224.28)
rDNS: 78.141.224.28.vultrusercontent.com (Vultr Hosting - Spain)
OS: Unix/Linux

PORT      STATE  SERVICE        VERSION
21/tcp    open   ftp            vsftpd 3.0.5
22/tcp    open   ssh            OpenSSH 8.9p1 Ubuntu 3ubuntu0.17
80/tcp    open   http           Cloudflare (redirect to HTTPS)
443/tcp   open   ssl/https      Cloudflare
3306/tcp  open   nagios-nsca    MySQL 8.0.42 (misidentified)
6379/tcp  open   redis?         Redis (Protected Mode: ON)
9000/tcp  open   cslistener     uvicorn (Python FastAPI)
11211/tcp open   memcached      Memcached 1.6.14

Not shown: 65528 filtered ports
```

### FTP Banner:
```
220 (vsFTPd 3.0.5)
```

### Redis Response (Protected Mode):
```
-DENIED Redis is running in protected mode because protected mode is enabled 
and no password is set for the default user. In this mode connections are only 
accepted from the loopback interface. If you want to connect from external computers 
to Redis you may adopt one of the following solutions:
1) Just disable protected mode sending the command 'CONFIG SET protected-mode no'
...
```

---

# نتيجة Nikto (الملف النصي)

```
Nikto v2.1.5
Target IP: 78.141.224.28
Target Port: 443
Server: cloudflare
Uncommon headers found:
  strict-transport-security: max-age=31536000; includeSubDomains
  x-content-type-options: nosniff
  permissions-policy: camera=(), microphone=(), geolocation=(), fullscreen=(self)
  cf-cache-status: DYNAMIC
  x-frame-options: SAMEORIGIN
  referrer-policy: no-referrer
  x-xss-protection: 1; mode=block
  cf-ray: [Ray ID]

No CGI Directories found
Allowed HTTP Methods: GET, HEAD
WARNING: HTTP error codes: 403 (Forbidden) - 1 times
CRITICAL: WAF/IPS detected (Cloudflare)
```

---

# نتيجة SQLMap (الملف النصي)

```
SQLMap 1.6.4
Target: https://kuraimibank.com/ar?search=test
WAF detected: Cloudflare (CRITICAL)
GET parameter 'search': NOT DYNAMIC
GET parameter 'search': NOT INJECTABLE

Tests performed:
  ✅ Boolean-based blind - Not injectable
  ✅ Error-based (MySQL, PostgreSQL, MSSQL, Oracle) - Not injectable  
  ✅ Time-based blind - Not injectable
  ✅ UNION query - Not injectable
  ✅ Stacked queries - Not injectable

Result: 0 vulnerabilities found
HTTP errors: 403 (WAF blocked some tests)
```

---

# نتيجة Dirb

### الصفحات المكتشفة (200 OK):
```
+/ar/about (CODE:200|SIZE:10531)
+/ar/blogs (CODE:200|SIZE:10546)
+/ar/contact-us (CODE:200|SIZE:10586)
+/ar/events (CODE:200|SIZE:10549)
+/ar/faqs (CODE:200|SIZE:10513)
```

### الصفحات المحمية (403):
```
/.htaccess: 403
/.git/HEAD: 403
/.git/config: 403
/.svn/entries: 403
/.DS_Store: 403
/config.php.bak: 403
/config.php.old: 403
/database.sql: 403
/dump.sql: 403
/error.log: 403
/access.log: 403
/web.config: 403
```

---

# ملخص الخدمات المكتشفة بالتفصيل

## FTP (21) - vsftpd 3.0.5
- **الحالة:** يعمل
- **البانر:** 220 (vsFTPd 3.0.5)
- **الخطورة:** متوسطة - FTP ينقل بيانات بدون تشفير
- **الإجراء:** الانتقال إلى SFTP

## SSH (22) - OpenSSH 8.9p1
- **الحالة:** يعمل
- **الإصدار:** Ubuntu 3ubuntu0.17
- **الخطورة:** منخفضة (إصدار محدث)
- **الإجراء:** التأكد من تعطيل root login

## HTTP (80) - Cloudflare
- **الحالة:** إعادة توجيه إلى HTTPS (301/302)
- **الإجراء:** جيد ✅

## HTTPS (443) - Cloudflare
- **الحالة:** يعمل
- **TLS:** 1.2, 1.3
- **شهادة:** Cloudflare proxy (ECC key)
- **صحة الشهادة:** 1 يوم فقط ⚠️

## MySQL (3306) - **CRITICAL**
- **الإصدار:** 8.0.42
- **الحالة:** مكشوف للإنترنت 🔴
- **Auth Plugin:** mysql_native_password
- **Capabilties:** SupportsTransactions, SupportsMultipleStatments, SupportsAuthPlugins
- **الإجراء العاجل:** حظر المنفذ من الإنترنت فوراً

## Redis (6379)
- **الحالة:** Protected Mode مفعل ✅
- **ملاحظة:** يرفض الاتصالات من خارج localhost
- **الإجراء:** إضافة قاعدة firewall للتأكيد

## uvicorn (9000)
- **الحالة:** يعمل
- **النوع:** Python FastAPI/Starlette
- **الاستجابة:** {"detail":"Not Found"} (HTTP/1.1)
- **الإجراء:** حظر المنفذ أو وضع خلف reverse proxy

## Memcached (11211) - **CRITICAL**
- **الإصدار:** 1.6.14
- **الحالة:** مكشوف 🔴
- **الخطورة:** DDoS Amplification (حتى 51,000x)
- **الإجراء العاجل:** حظر المنفذ UDP/TCP فوراً

---

# ملاحظات إضافية من التحليل اليدوي

### Whatweb:
- Laravel ✅ مكتشف
- Cloudflare ✅ مكتشف
- HSTS ✅ موجود
- Cookies: XSRF-TOKEN, laravel_session (HttpOnly, Secure)
- Country: Spain (ES)
- IP: 78.141.224.28

### تحليل الشهادة (OpenSSL):
```
Issuer: CN = Cloudflare TLS proxy-everything Intercept CA
Subject: CN = kuraimibank.com
Public Key: id-ecPublicKey (ECC)
Not Before: Sep 23 14:13:27 2026 GMT
Not After: Sep 24 15:13:27 2026 GMT (24h)
```

### Hidden Paths:
جميع المسارات الإدارية والملفات الحساسة محمية (403/404)

---

*بيانات خام من أدوات المسح الأمني*
*تاريخ التوثيق: 2026-09-23*
