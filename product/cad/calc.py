"""محاسبات مهندسی رول فیلم، قرقره و موتور (همهٔ اعداد تقریبی و قابل تنظیم)"""
import math

core_d = 25.0          # قطر هستهٔ مقوایی (mm)
t_film = 0.13          # ضخامت فیلم + چسب (mm): PET 50µm + چسب ~80µm
t_dirty = 0.20         # ضخامت مؤثر لایه‌های کثیف (با حشره) در قرقرهٔ جمع‌کننده
advance = 320.0        # طول هر پیشروی = ارتفاع سطح دیده‌شده (mm)
tension = 20.0         # کشش لازم برای جدا کردن فیلم از رول + اصطکاک (N) – باید با نمونهٔ واقعی اندازه‌گیری شود


def roll_d(length_mm, t):
    return math.sqrt(core_d**2 + 4 * length_mm * t / math.pi)


print("طول رول | قطر رول نو | قطر قرقرهٔ پر | تعداد پیشروی | دوام با پیشروی هر ۳ روز | هر ۷ روز")
for L_m in (5, 10, 15, 20):
    L = L_m * 1000
    n = int(L // advance)
    print(f"{L_m:>3} m | {roll_d(L, t_film):5.1f} mm | {roll_d(L, t_dirty):5.1f} mm | {n:3d} | {n*3/30:4.1f} ماه | {n*7/30:4.1f} ماه")

D_full = roll_d(10000, t_dirty)
torque = tension * (D_full / 2) / 1000  # N·m
print(f"\nگشتاور لازم روی محور جمع‌کننده (رول ۱۰ متری پر): {torque:.2f} N·m = {torque*10.2:.1f} kg·cm")

# نسخهٔ برقی: موتور N20 با گیربکس 1:298 (~3.5 kg·cm، ~100rpm در 6V) + چرخ‌دندهٔ 1:3
motor_kgcm, motor_rpm, extra = 3.5, 100, 3
print(f"موتور N20 1:298 + چرخ‌دندهٔ 1:{extra}: {motor_kgcm*extra:.1f} kg·cm، {motor_rpm/extra:.0f} rpm")
for D in (core_d + 2, D_full):
    revs = advance / (math.pi * D)
    print(f"  قطر {D:4.1f} mm: {revs:.2f} دور برای هر پیشروی، ~{revs/(motor_rpm/extra)*60:.1f} ثانیه")

# نسخهٔ دستی: دستگیرهٔ ۴۸ میلی‌متری با چرخ‌دندهٔ 1.5:1
knob_d, ratio = 48.0, 1.5
force = torque / ratio / (knob_d / 2 / 1000)
print(f"\nنیروی دست روی لبهٔ دستگیره (Ø{knob_d:.0f}، نسبت {ratio}:1): ~{force:.0f} N")
for D in (core_d + 2, D_full):
    print(f"  قطر {D:4.1f} mm: {advance/(math.pi*D)*ratio:.1f} دور دستگیره برای هر پیشروی")

# انکودر: غلتک Ø14 با ۴ آهنربا و سنسور هال
enc_d, mags = 14.0, 4
print(f"\nدقت اندازه‌گیری طول با غلتک Ø{enc_d:.0f} و {mags} آهنربا: {math.pi*enc_d/mags:.1f} mm به ازای هر پالس")
print(f"پالس لازم برای هر پیشروی: {advance/(math.pi*enc_d/mags):.0f}")
