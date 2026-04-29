function makeMissionId(city = "EARTH") {
  const clean = city.slice(0, 3).toUpperCase();
  const stamp = new Date().getFullYear();
  return `EL-${clean}-${stamp}`;
}

function getSceneQuality(reliability) {
  if (reliability >= 85) return "High";
  if (reliability >= 65) return "Moderate";
  return "Review";
}

export default function OrbitalReceipt({ scanData }) {
  if (!scanData) return null;

  const city = scanData?.metadata?.city || "Selected city";
  const date = String(scanData?.metadata?.date || "").slice(0, 10);
  const cloud = scanData?.metadata?.cloud_cover ?? "N/A";
  const reliability = scanData?.metrics?.reliability_score ?? 0;
  const satellite = scanData?.metadata?.satellite || "Sentinel-2";
  const resolution = scanData?.metadata?.resolution || "10m / 20m";

  return (
    <section className="scan-passport">
      <div className="passport-main">
        <div className="passport-mark">EL</div>

        <div>
          <span>Scan Passport</span>
          <h2>{makeMissionId(city)}</h2>
          <p>
            Scene processed for {city}. Vegetation, water, built-surface,
            and heat-risk indicators are ready for review.
          </p>
        </div>
      </div>

      <div className="passport-grid">
        <div>
          <span>City</span>
          <b>{city}</b>
        </div>

        <div>
          <span>Scene date</span>
          <b>{date || "N/A"}</b>
        </div>

        <div>
          <span>Satellite</span>
          <b>{satellite}</b>
        </div>

        <div>
          <span>Resolution</span>
          <b>{resolution}</b>
        </div>

        <div>
          <span>Cloud cover</span>
          <b>{cloud}%</b>
        </div>

        <div>
          <span>Scene quality</span>
          <b>{getSceneQuality(reliability)}</b>
        </div>
      </div>
    </section>
  );
}