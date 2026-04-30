const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
export async function runScan(payload) {
  const response = await fetch(`${API_BASE}/api/scan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("EarthLens scan failed");
  }

  return response.json();
}

export async function askEarthLens(payload) {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("EarthLens chat failed");
  }

  return response.json();
}