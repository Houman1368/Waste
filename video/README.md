# ویدیوی معرفی تلهٔ حشرهٔ بیمارستانی (مدل قرقره‌ای)

انیمیشن دوبعدی ۷۵ ثانیه‌ای (۲۲۵۰ فریم، 30fps) با Remotion؛ همهٔ گرافیک‌ها SVG و کدنویسی‌شده‌اند.

## اجرا

```bash
npm install
npm run dev              # پیش‌نمایش در Remotion Studio
npm run render:wide      # out/video-16x9.mp4  (1920×1080)
npm run render:vertical  # out/video-9x16.mp4  (1080×1920)
npm run stills           # اسکرین‌شات فریم‌های 150، 600، 1200، 1600، 2100 در out/stills
```

## ویدیوهای معرفی مدل‌ها (RTH-A، RTH-B، RTH-C)

```bash
npm run render:rth-a     # out/RTH-A.mp4
npm run render:rth-b     # out/RTH-B.mp4
npm run render:rth-c     # out/RTH-C.mp4
npm run render:rth       # هر سه
```

هر ویدیو ۹۳ ثانیه (1920×1080): بسم الله ← معرفی با لوگو و نام شرکت ← اجزا ← جذب ← گیر افتادن ← پیچیدن فیلم (دستی/برقی) ← تعویض کارتریج ← مشخصات ← پایان.
متن‌ها و ابعاد هر مدل در `src/models/specs.ts`؛ تصاویر سه‌بعدی در `public/renders/`.

## جای‌خالی‌ها

نام محصول، نام شرکت و شمارهٔ تماس/وب‌سایت فقط در `src/config.ts` هستند.

## لوگو

فایل لوگو را با نام `public/logo.svg`، `public/logo.png` یا `public/logo.jpg` بگذارید؛ در پایان‌بندی روی کارت سفید نمایش داده می‌شود.

## صدا (اختیاری)

- `public/voiceover.mp3` اگر وجود داشته باشد روی ویدیو قرار می‌گیرد.
- `public/music.mp3` اگر وجود داشته باشد با صدای ۲۰٪ پخش می‌شود.
- اگر نباشند، ویدیو بی‌صدا ساخته می‌شود.

## فونت

Vazirmatn (OFL) با `@remotion/google-fonts/Vazirmatn` لود می‌شود. اگر مرورگر رندر به
Google Fonts دسترسی نداشت (شبکهٔ محدود یا پراکسی):

```bash
npm run fonts:download                 # فایل‌ها را در public/fonts می‌گذارد
npm run render:wide:local-fonts
npm run render:vertical:local-fonts
```

## ساختار

```
src/
  Root.tsx            دو Composition: Video16x9 و Video9x16
  Video.tsx           چیدمان صحنه‌ها با <Sequence> و صدای اختیاری
  config.ts           جای‌خالی‌ها
  theme.ts            پالت رنگ و زمان‌بندی صحنه‌ها
  layout.ts           چیدمان افقی/عمودی
  components/         Device, Fly, Hand, RtlText, CycleDiagram, MiniDashboard, ...
  scenes/             Scene1Problem … Scene8Outro
```
