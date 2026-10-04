# BIP-39 Wallet Security & Entropy Simulator

مستودع يحتوي على مشاريع Android مع **بناء APK تلقائي بالكامل عبر GitHub Actions** —
كل `push` يُنتج debug APK، وكل `tag` يُنتج **إصدارًا موقّعًا** (APK + AAB).

## التحميل المباشر

| الإصدار | الملف | الرابط |
|---|---|---|
| v1.2.4 (موقّع) | APK | https://github.com/aboodalso54-dev/BIP-39-Wallet-Security/releases/download/v1.2.4/app-release.apk |
| v1.2.4 (موقّع) | AAB (Play Store) | https://github.com/aboodalso54-dev/BIP-39-Wallet-Security/releases/download/v1.2.4/app-release.aab |
| أحدث إصدار | — | https://github.com/aboodalso54-dev/BIP-39-Wallet-Security/releases/latest |

## كيف يعمل البناء التلقائي

### 1) `Android CI` — `.github/workflows/android.yml`
- **المُشغِّل:** كل push أو PR على `main` / `develop` (+ تشغيل يدوي)
- **ي��مل:** JDK 17 + Android SDK 34 + Gradle (مع cache)
- **يبني:** `AndroidAPKProjects/MyApp`، `AndroidAPKProjects/SimpleApp`، `MyApp`
- **المخرجات:** artifact واحد `debug-apks` (كل ملفات debug APK)
- رابط постоянный للأحدث: صفحة Actions → آخر run → Artifacts → `debug-apks`

### 2) `Android Release Build` — `.github/workflows/release.yml`
- **المُشغِّل:** `git push origin v*` أو تشغيل يدوي
- **الإصدار (versioning):** من الـ tag — `v1.2.3` ⟵ `versionName=1.2.3`, `versionCode=10203`
- **التوقيع:** مفتاح إصدار دائم (تفاصيله أدناه) — يتحقق بـ `apksigner` ويُفشل البناء إذا كان APK موقّعًا بمفتاح debug
- **المخرجات:** `app-release.apk` + `app-release.aab` داخل GitHub Release + artifacts

## مفتاح التوقيع

| البند | القيمة |
|---|---|
| alias | `my-key-alias` |
| store/key password | `android` |
| SHA-256 | `00:FF:CB:21:7F:7C:75:62:1B:C1:F9:FA:16:7D:FD:15:FB:54:DD:8A:69:8D:D9:4F:F8:A2:7A:83:B2:77:85:E6` |

يدير الـ workflow المفتاح بنفسه بالترتيب التالي:
1. سرّ المستودع `KEYSTORE_BASE64` إن كان صالحًا (يُفضَّل).
2. **مسودة release داخلية باسم `signing-key`** تحمل `keystore.b64` — لا تُنشر، غير مرئية للعامة.
3. عند أول تشغيل: يولّد المفتاح مرة واحدة ويحفظه في (2) لإعادة استخدامه.

⚠️ **لا تحذف المسودة `signing-key`** — بدونها يتغير المفتاح ولا يمكن تحديث أي إصدار مُثبَّت.

## إصدار جديد

```bash
git tag -f v1.3.0 -m v1.3.0
git push --force origin v1.3.0
```
يُنشر تلقائيًا APK + AAB مع ملاحظات الإصدار.

## بناء محلي

```bash
cd AndroidAPKProjects/MyApp
./gradlew assembleDebug        # debug
./gradlew assembleRelease      # release (يتوقّع متغيرات MYAPP_UPLOAD_* للتوقيع)
```

## الحفاظ على التحديثات

- `.github/dependabot.yml` يفتح PRs أسبوعية لتحديث Actions وGradle dependencies.
- راجع سجل البناء بعد كل تحديث قبل النشر.