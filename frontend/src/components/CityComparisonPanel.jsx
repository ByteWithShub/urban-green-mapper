import { useState } from "react";
import {
  ArrowLeftRight,
  ChevronDown,
  ChevronUp,
  Loader2,
  Sparkles,
  BarChart3,
  Map,
} from "lucide-react";
import { runScan } from "../api";

const cities = [
  "Ottawa",
  "Toronto",
  "Victoria",
  "Edmonton",
  "Winnipeg",
  "Halifax",
  "Charlottetown",
  "St. John's",
  "Whitehorse",
  "Yellowknife",
  "Iqaluit",
];

const layers = [
  { key: "rgb", label: "RGB", hint: "Natural view" },
  { key: "ndvi", label: "NDVI", hint: "Vegetation" },
  { key: "ndwi", label: "NDWI", hint: "Water signal" },
  { key: "ndbi", label: "NDBI", hint: "Built surface" },
  { key: "savi", label: "SAVI", hint: "Soil-adjusted" },
  { key: "heat", label: "Heat", hint: "Heat signal" },
];

export default function CityComparisonPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [leftCity, setLeftCity] = useState("Ottawa");
  const [rightCity, setRightCity] = useState("Toronto");
  const [layer, setLayer] = useState("rgb");
  const [leftScan, setLeftScan] = useState(null);
  const [rightScan, setRightScan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const selectedLayer = layers.find((item) => item.key === layer);

  async function runComparison() {
    setLoading(true);
    setError("");

    try {
      const [leftData, rightData] = await Promise.all([
        runScan({ city: leftCity, user_type: "researcher", layer_focus: layer }),
        runScan({ city: rightCity, user_type: "researcher", layer_focus: layer }),
      ]);

      setLeftScan(leftData);
      setRightScan(rightData);
    } catch (err) {
      console.error(err);
      setError("Comparison failed. Try another validated city pair.");
    } finally {
      setLoading(false);
    }
  }

  function metric(label, leftValue, rightValue, suffix = "") {
    return (
      <div className="comparison-metric">
        <span>{label}</span>
        <b>{leftValue}{suffix}</b>
        <b>{rightValue}{suffix}</b>
      </div>
    );
  }

  return (
    <section className={`city-comparison glass ${isOpen ? "open" : ""}`}>
      <button className="comparison-launch" onClick={() => setIsOpen((v) => !v)}>
        <div className="comparison-launch-icon">
          <ArrowLeftRight size={22} />
        </div>

        <div>
          <span className="eyebrow small">City Comparison</span>
          <h2>Compare urban green signals</h2>
          <p>
            Side-by-side satellite intelligence for vegetation, water, built surface,
            and heat-risk patterns.
          </p>
        </div>

        <div className="comparison-launch-action">
          <Sparkles size={18} />
          {isOpen ? <ChevronUp size={22} /> : <ChevronDown size={22} />}
        </div>
      </button>

      {isOpen && (
        <div className="comparison-body">
          <div className="comparison-topbar">
            <div className="comparison-controls">
              <label>
                City A
                <select value={leftCity} onChange={(e) => setLeftCity(e.target.value)}>
                  {cities.map((city) => <option key={city}>{city}</option>)}
                </select>
              </label>

              <label>
                City B
                <select value={rightCity} onChange={(e) => setRightCity(e.target.value)}>
                  {cities.map((city) => <option key={city}>{city}</option>)}
                </select>
              </label>

              <label>
                Layer
                <select value={layer} onChange={(e) => setLayer(e.target.value)}>
                  {layers.map((item) => (
                    <option key={item.key} value={item.key}>{item.label}</option>
                  ))}
                </select>
              </label>
            </div>

            <button className="primary-btn comparison-btn" onClick={runComparison} disabled={loading}>
              {loading ? (
                <>
                  Comparing <Loader2 className="spin" size={16} />
                </>
              ) : (
                "Run comparison"
              )}
            </button>
          </div>

          <div className="comparison-context">
            <div>
              <Map size={18} />
              <span>Layer focus</span>
              <b>{selectedLayer?.label} · {selectedLayer?.hint}</b>
            </div>

            <div>
              <BarChart3 size={18} />
              <span>Comparison type</span>
              <b>Same-layer city benchmark</b>
            </div>
          </div>

          {error && <div className="comparison-error">{error}</div>}

          <div className="comparison-grid">
            <ComparisonCard
              city={leftScan?.metadata?.city || leftCity}
              layer={layer}
              scan={leftScan}
              loading={loading}
              side="A"
            />

            <ComparisonCard
              city={rightScan?.metadata?.city || rightCity}
              layer={layer}
              scan={rightScan}
              loading={loading}
              side="B"
            />
          </div>

          {leftScan && rightScan ? (
            <div className="comparison-table">
              <div className="comparison-metric comparison-table-head">
                <span>Metric</span>
                <b>{leftScan.metadata.city}</b>
                <b>{rightScan.metadata.city}</b>
              </div>

              {metric("Green coverage", leftScan.metrics.green_pct, rightScan.metrics.green_pct, "%")}
              {metric("Dense canopy", leftScan.metrics.dense_pct, rightScan.metrics.dense_pct, "%")}
              {metric("Built-up signal", leftScan.metrics.built_up_pct, rightScan.metrics.built_up_pct, "%")}
              {metric("Heat risk", leftScan.metrics.heat_risk_score, rightScan.metrics.heat_risk_score, "/100")}
              {metric("Reliability", leftScan.metrics.reliability_score, rightScan.metrics.reliability_score, "/100")}
            </div>
          ) : (
            <div className="comparison-preview-strip">
              <span>What you’ll compare</span>
              <b>Green coverage</b>
              <b>Dense canopy</b>
              <b>Built surface</b>
              <b>Heat risk</b>
              <b>Reliability</b>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

function ComparisonCard({ city, layer, scan, loading, side }) {
  return (
    <div className="comparison-card">
      <div className="comparison-card-header">
        <div>
          <span>City {side}</span>
          <h3>{city}</h3>
        </div>
        <b>{layer.toUpperCase()}</b>
      </div>

      {loading ? (
        <div className="comparison-empty active">
          <Loader2 className="spin" size={24} />
          <span>Fetching Sentinel-2 scene...</span>
        </div>
      ) : scan ? (
        <img src={scan.layers[layer]} alt={`${city} ${layer}`} />
      ) : (
        <div className="comparison-placeholder">
          <div className="placeholder-orbit" />
          <h4>Ready for scan</h4>
          <p>Run comparison to load this city’s satellite layer.</p>
        </div>
      )}
    </div>
  );
}

