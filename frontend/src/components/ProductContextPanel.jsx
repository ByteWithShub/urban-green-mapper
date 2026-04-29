export default function ProductContextPanel({ scanData, userType }) {
  if (!scanData) return null;

  const city = scanData?.metadata?.city || "Selected city";
  const metrics = scanData?.metrics || {};

  const temp = metrics.temperature_c;
  const heat = metrics.heat_risk_score ?? "N/A";
  const reliability = metrics.reliability_score ?? "N/A";
  const green = metrics.green_pct ?? "N/A";
  const dense = metrics.dense_pct ?? "N/A";

  const copy = {
    kids: {
      title: "Explore the city from space",
      text: "Switch between layers to see where plants, water, and city surfaces appear strongest.",
    },
    general: {
      title: "City overview",
      text: `${city} is assessed for vegetation coverage, dense canopy, water signal, built surfaces, and scene reliability.`,
    },
    planner: {
      title: "Planning signals",
      text: "Use this scan to identify where vegetation is limited, built surfaces are stronger, and heat exposure may need closer review.",
    },
    researcher: {
      title: "Methods context",
      text: "EarthLens derives NDVI, NDWI, NDBI, SAVI, vegetation classes, and reliability-aware indicators from Sentinel-2 L2A bands.",
    },
  };

  const content = copy[userType] || copy.general;

  return (
    <section className="product-context glass">
      <div className="context-main">
        <div className="context-icon">⌁</div>

        <div>
          <span className="section-kicker">Scene Context</span>
          <h2>{content.title}</h2>
          <p>{content.text}</p>
        </div>
      </div>

      <div className="context-grid">
        <div>
          <span>Current temperature</span>
          <b>{temp == null ? "Unavailable" : `${temp}°C`}</b>
        </div>

        <div>
          <span>Heat risk score</span>
          <b>{heat}/100</b>
        </div>

        <div>
          <span>Scene reliability</span>
          <b>{reliability}/100</b>
        </div>

        <div>
          <span>Vegetation profile</span>
          <b>{green}% green / {dense}% dense</b>
        </div>
      </div>
    </section>
  );
}