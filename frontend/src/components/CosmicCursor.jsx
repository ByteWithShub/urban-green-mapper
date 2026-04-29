import { useEffect, useState } from "react";

export default function CosmicCursor() {
  const [pos, setPos] = useState({ x: -100, y: -100 });

  useEffect(() => {
    function move(event) {
      setPos({ x: event.clientX, y: event.clientY });
      document.documentElement.style.setProperty("--cursor-x", `${event.clientX}px`);
      document.documentElement.style.setProperty("--cursor-y", `${event.clientY}px`);
    }

    window.addEventListener("mousemove", move);
    return () => window.removeEventListener("mousemove", move);
  }, []);

  return (
    <>
      <div className="cursor-glow" style={{ left: pos.x, top: pos.y }} />
      <div className="cursor-dot" style={{ left: pos.x, top: pos.y }} />
    </>
  );
}