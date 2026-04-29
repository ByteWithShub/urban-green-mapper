function level(value, good, watch) {
  if (value >= good) return "Good";
  if (value >= watch) return "Watch";
  return "Review";
}

export default function AudienceModePanel({ userType, scanData }) {
  if (!scanData) return null;

  const city = scanData?.metadata?.city || "Selected city";
  const metrics = scanData?.metrics || {};

  const green = metrics.green_pct ?? 0;
  const dense = metrics.dense_pct ?? 0;
  const water = metrics.water_pct ?? 0;
  const built = metrics.built_up_pct ?? 0;
  const ndvi = metrics.mean_ndvi ?? 0;
  const ndwi = metrics.mean_ndwi ?? 0;
  const ndbi = metrics.mean_ndbi ?? 0;
  const heat = metrics.heat_risk_score ?? 0;
  const reliability = metrics.reliability_score ?? 0;

  if (userType === "kids") {
    return (
      <section className="audience-panel glass kid-mode-card">
        <div className="audience-header">
          <div className="context-icon">✦</div>
          <div>
            <span>Explorer View</span>
            <h2>Satellite Explorer</h2>
          </div>
        </div>

        <p className="mode-summary">
          This scan shows where {city} has stronger plant signals, possible water
          areas, and harder city surfaces.
        </p>

        <div className="explorer-card">
          <h3>Explorer Challenge</h3>
          <p>
            Switch between NDVI, NDWI, and NDBI. Notice how each layer reveals
            a different part of the city.
          </p>

          <div className="explorer-steps">
            <span>NDVI → Plants</span>
            <span>NDWI → Water</span>
            <span>NDBI → Built surfaces</span>
          </div>
        </div>

        <p className="friendly-score">
          Green signal: <b>{green >= 50 ? "Strong" : green >= 25 ? "Moderate" : "Limited"}</b>
        </p>
      </section>
    );
  }

  if (userType === "general") {
    return (
      <section className="audience-panel glass">
        <div className="audience-header">
          <div className="context-icon">◎</div>
          <div>
            <span>Public View</span>
            <h2>City Overview</h2>
          </div>
        </div>

        <p className="mode-summary">
          {city} shows {green}% green coverage and {dense}% dense canopy in this
          scene. These signals help explain how vegetation may support cooling,
          livability, and stormwater absorption.
        </p>

        <div className="status-grid">
          <div><span>Green coverage</span><b>{level(green, 45, 25)}</b></div>
          <div><span>Dense canopy</span><b>{level(dense, 25, 12)}</b></div>
          <div><span>Heat risk</span><b>{heat >= 70 ? "High" : heat >= 40 ? "Moderate" : "Low"}</b></div>
        </div>
      </section>
    );
  }

  if (userType === "planner") {
    return (
      <section className="audience-panel glass">
        <div className="audience-header">
          <div className="context-icon">⌬</div>
          <div>
            <span>Planning View</span>
            <h2>Urban Signals</h2>
          </div>
        </div>

        <p className="mode-summary">
          {city} shows {dense}% dense canopy and {built}% built-surface signal.
          Areas with lower vegetation and stronger built signal may deserve
          closer review for heat adaptation planning.
        </p>

        <div className="status-grid">
          <div><span>Heat risk score</span><b>{heat}/100</b></div>
          <div><span>Water signal</span><b>{water}%</b></div>
          <div><span>Reliability</span><b>{reliability}/100</b></div>
        </div>

        <p className="caveat">
          Use this as screening intelligence. Scene date, cloud cover, seasonality,
          and local validation should guide final planning decisions.
        </p>
      </section>
    );
  }

  return (
    <section className="audience-panel glass">
      <div className="audience-header">
        <div className="context-icon">∑</div>
        <div>
          <span>Research View</span>
          <h2>Methods & Confidence</h2>
        </div>
      </div>

      <div className="research-grid">
        <div>
          <h3>Indices</h3>
          <p>NDVI: {ndvi}</p>
          <p>NDWI: {ndwi}</p>
          <p>NDBI: {ndbi}</p>
        </div>

        <div>
          <h3>Thresholds</h3>
          <p>Green: NDVI &gt; 0.20</p>
          <p>Dense: NDVI &gt; 0.60</p>
          <p>Water: NDWI &gt; 0.05</p>
        </div>

        <div>
          <h3>Reliability</h3>
          <p>Score: {reliability}/100</p>
          <p>Satellite: {scanData?.metadata?.satellite}</p>
          <p>Resolution: {scanData?.metadata?.resolution}</p>
        </div>
      </div>
    </section>
  );
}