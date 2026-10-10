export const C = {
  bg: "#F7F9FA",
  text: "#1F2A30",
  muted: "#55656D",
  brand: "#0F6E56",
  uv: "#7F77DD",
  uvHalo: "#AFA9EC",
  film: "#FAEEDA",
  filmEdge: "#BA7517",
  body: "#FFFFFF",
  bodyEdge: "#C9D1D6",
  cassette: "#5F5E5A",
  cassetteDark: "#3E3D3A",
  warn: "#D85A30",
  insect: "#1F2A30",
  ok: "#1D9E75",
  glove: "#4A90D9",
  gloveDark: "#2F6FB0",
  sleeve: "#9CC9BD",
  wall: "#F7F9FA",
  floor: "#E3E9EC",
  rail: "#DCE3E7",
};

export const FPS = 30;

// زمان‌بندی صحنه‌ها (فریم، ۳۰fps)
export const SCENES = {
  s1: { from: 0, dur: 240 },
  s2: { from: 240, dur: 240 },
  s3: { from: 480, dur: 300 },
  s4: { from: 780, dur: 300 },
  s5: { from: 1080, dur: 360 },
  s6: { from: 1440, dur: 300 },
  s7: { from: 1740, dur: 300 },
  s8: { from: 2040, dur: 210 },
} as const;

export const TOTAL_FRAMES = 2250;
