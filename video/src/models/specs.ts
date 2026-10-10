// مشخصات سه مدل RTH برای ویدیوهای معرفی. اندازه‌ها میلی‌متر و مطابق مدل‌های سه‌بعدی (product/cad/concepts.py).
// مختصات: x از مرکز (راست مثبت)، y از پایین بدنه (بالا مثبت).

export type Rect = { x0: number; x1: number; y0: number; y1: number; r?: number };

export type ModelKey = "A" | "B" | "C";

export type ModelSpec = {
  key: ModelKey;
  id: string; // نام مدل
  render: string; // پیشوند تصاویر سه‌بعدی در public/renders
  H: number; // ارتفاع کل برای جاگذاری
  kind: "panel" | "slats";
  body: Rect; // بدنهٔ اصلی (برای A: بدنهٔ پشت پنل)
  shield?: Rect; // فقط A: پنل جلو
  window?: Rect; // B و C: پنجرهٔ تیغه‌دار
  slatPitch?: number;
  ledBar?: Rect; // نوار LED جلو (C)
  uvStrips?: Rect[]; // نوارهای UV کناری (B) یا داخلی (C)
  film: Rect;
  supplyY: number;
  takeupY: number;
  rollLen: number;
  cassette: Rect;
  knob: { x: number; y: number; r: number; out: number };
  logo: { x: number; y: number; w: number; h: number };
  status: { x: number; y: number };
  // متن‌ها
  title: string;
  tagline: string;
  callouts: { text: string; x: number; y: number; side: "left" | "right" }[];
  attract: string[];
  capture: string[];
  specs: string[];
  places: string;
};

export const COMPANY_FULL = "شرکت دانش‌بنیان رایا طب هگمتانه نوین";
export const BISMILLAH = "بسم الله الرحمن الرحیم";

export const MODELS: Record<ModelKey, ModelSpec> = {
  A: {
    key: "A",
    id: "RTH-A",
    render: "a",
    H: 560,
    kind: "panel",
    body: { x0: -180, x1: 180, y0: 0, y1: 540, r: 70 },
    shield: { x0: -200, x1: 200, y0: -10, y1: 550, r: 110 },
    film: { x0: -140, x1: 140, y0: 120, y1: 445 },
    supplyY: 470,
    takeupY: 62,
    rollLen: 280,
    cassette: { x0: -148, x1: 148, y0: 8, y1: 112, r: 18 },
    knob: { x: 180, y: 62, r: 24, out: 34 },
    logo: { x: 0, y: 75, w: 120, h: 68 },
    status: { x: 150, y: 40 },
    title: "تلهٔ حشرهٔ دیواری با پنل نوری",
    tagline: "حشره‌ها پشت پنل پنهان می‌شوند؛ از روبه‌رو هیچ حشره‌ای دیده نمی‌شود",
    callouts: [
      { text: "لبهٔ نورانی UV-A", x: -200, y: 420, side: "left" },
      { text: "پنل جلوی خمیده", x: -60, y: 300, side: "left" },
      { text: "کاست دربسته (داخل)", x: -100, y: 60, side: "left" },
      { text: "دستگیرهٔ پیشروی فیلم", x: 214, y: 62, side: "right" },
    ],
    attract: [
      "نور LED یووی-A از دورتادور پنل بیرون می‌تابد",
      "حشره از هر چهار لبه وارد کانال پشت پنل می‌شود",
    ],
    capture: [
      "داخل کانال، حشره روی فیلم چسبی می‌نشیند و می‌چسبد",
      "بدون برق‌گرفتگی، بدون سوختن، بدون پخش ذرات",
    ],
    specs: [
      "ابعاد: ۴۰ × ۵۶ × ۱۰ سانتی‌متر",
      "سطح چسبی: ۲۸ × ۳۲ سانتی‌متر",
      "دوام هر رول ۱۰ متری: ۳ تا ۷ ماه",
      "نسخهٔ دستی (دستگیره) و برقی (موتور خودکار)",
    ],
    places: "مناسب: اتاق بیمار، لابی، اتاق انتظار، فضاهای اداری",
  },
  B: {
    key: "B",
    id: "RTH-B",
    render: "b",
    H: 900,
    kind: "slats",
    body: { x0: -100, x1: 100, y0: 0, y1: 900, r: 100 },
    window: { x0: -66, x1: 66, y0: 145, y1: 765, r: 30 },
    slatPitch: 19,
    uvStrips: [
      { x0: -66, x1: -61, y0: 160, y1: 750 },
      { x0: 61, x1: 66, y0: 160, y1: 750 },
    ],
    film: { x0: -62, x1: 62, y0: 150, y1: 760 },
    supplyY: 795,
    takeupY: 100,
    rollLen: 124,
    cassette: { x0: -79, x1: 79, y0: 5, y1: 139, r: 30 },
    knob: { x: 100, y: 108, r: 24, out: 32 },
    logo: { x: 0, y: 72, w: 104, h: 59 },
    status: { x: 0, y: 830 },
    title: "تلهٔ حشرهٔ ستونی باریک",
    tagline: "باریک و بلند؛ مناسب راهرو، ورودی بخش‌ها و کنار در",
    callouts: [
      { text: "نوارهای نور UV-A", x: -66, y: 600, side: "left" },
      { text: "تیغه‌های مایل", x: -40, y: 400, side: "left" },
      { text: "کاست دربسته", x: -79, y: 70, side: "left" },
      { text: "دستگیرهٔ پیشروی فیلم", x: 132, y: 108, side: "right" },
    ],
    attract: [
      "دو نوار LED یووی-A دو طرف کانال، حشره را از دور جذب می‌کنند",
      "حشره از بین تیغه‌های مایل وارد می‌شود؛ تیغه‌ها سطح چسبی را از دید پنهان می‌کنند",
    ],
    capture: [
      "پشت تیغه‌ها، حشره روی فیلم چسبی می‌نشیند و می‌چسبد",
      "بدون برق‌گرفتگی، بدون سوختن، بدون پخش ذرات",
    ],
    specs: [
      "ابعاد: ۲۰ × ۹۰ × ۸.۵ سانتی‌متر",
      "سطح چسبی: ۱۲ × ۶۱ سانتی‌متر",
      "دوام هر رول: ۳ تا ۷ ماه",
      "نسخهٔ دستی (دستگیره) و برقی (موتور خودکار)",
    ],
    places: "مناسب: راهرو، ورودی بخش‌ها، کنار در، فضاهای کم‌عرض",
  },
  C: {
    key: "C",
    id: "RTH-C",
    render: "c",
    H: 560,
    kind: "slats",
    body: { x0: -170, x1: 170, y0: 0, y1: 560, r: 72 },
    window: { x0: -136, x1: 136, y0: 160, y1: 450, r: 24 },
    slatPitch: 17,
    ledBar: { x0: -118, x1: 118, y0: 496, y1: 504, r: 4 },
    uvStrips: [{ x0: -125, x1: 125, y0: 438, y1: 446 }],
    film: { x0: -132, x1: 132, y0: 162, y1: 448 },
    supplyY: 488,
    takeupY: 70,
    rollLen: 264,
    cassette: { x0: -148, x1: 148, y0: 6, y1: 134, r: 40 },
    knob: { x: 170, y: 70, r: 26, out: 33 },
    logo: { x: 0, y: 72, w: 120, h: 68 },
    status: { x: 140, y: 500 },
    title: "تلهٔ حشرهٔ پرقدرت",
    tagline: "نور مستقیم و قدرت جذب بالا؛ مناسب آشپزخانه، انبار و اورژانس",
    callouts: [
      { text: "نوار LED یووی-A", x: -118, y: 500, side: "left" },
      { text: "تیغه‌های مایل", x: -136, y: 300, side: "left" },
      { text: "کاست دربسته", x: -148, y: 70, side: "left" },
      { text: "دستگیرهٔ پیشروی فیلم", x: 203, y: 70, side: "right" },
    ],
    attract: [
      "نوار LED جلو مستقیم دیده می‌شود؛ جذب حشره از فاصلهٔ دور",
      "حشره از بین تیغه‌های مایل وارد می‌شود",
    ],
    capture: [
      "پشت تیغه‌ها، حشره روی فیلم چسبی می‌نشیند و می‌چسبد",
      "بدون برق‌گرفتگی، بدون سوختن، بدون پخش ذرات",
    ],
    specs: [
      "ابعاد: ۳۴ × ۵۶ × ۸ سانتی‌متر",
      "سطح چسبی: ۲۶ × ۲۹ سانتی‌متر",
      "دوام هر رول ۱۰ متری: ۳ تا ۷ ماه",
      "نسخهٔ دستی (دستگیره) و برقی (موتور خودکار)",
    ],
    places: "مناسب: آشپزخانه، انبار، اورژانس، رختشوی‌خانه",
  },
};

// زمان‌بندی صحنه‌ها (فریم، ۳۰fps) — هر متن دست‌کم ۳ ثانیه پس از ظاهر شدن روی صفحه می‌ماند
export const MSCENES = [
  { key: "bismillah", dur: 120 },
  { key: "intro", dur: 240 },
  { key: "parts", dur: 330 },
  { key: "attract", dur: 360 },
  { key: "capture", dur: 330 },
  { key: "roll", dur: 420 },
  { key: "replace", dur: 420 },
  { key: "specs", dur: 330 },
  { key: "outro", dur: 240 },
] as const;

export const MTOTAL = MSCENES.reduce((a, s) => a + s.dur, 0);
