import React from "react";
import { AbsoluteFill } from "remotion";
import { CycleDiagram } from "../components/CycleDiagram";
import { MiniDashboard } from "../components/MiniDashboard";
import { RtlText } from "../components/RtlText";
import { useLayout } from "../layout";
import { C } from "../theme";

export const Scene7Cycle: React.FC = () => {
  const { v } = useLayout();
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <div style={{ position: "absolute", top: v ? 90 : 70, left: v ? 56 : 80, right: v ? 56 : 80 }}>
        <RtlText size="title" delay={5} color={C.brand}>
          یک سرویس کامل، نه فقط یک دستگاه
        </RtlText>
      </div>
      <CycleDiagram />
      <MiniDashboard delay={70} box={v ? { left: 56, top: 1270, width: 968, height: 590 } : { left: 80, top: 270, width: 600, height: 570 }} />
    </AbsoluteFill>
  );
};
