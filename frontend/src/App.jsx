import { useMemo, useState } from "react";
import {
  Activity,
  Droplets,
  Flame,
  Leaf,
  Map,
  Radar,
  Satellite,
  ShieldCheck,
  Trees,
  Waves,
} from "lucide-react";

import { runScan } from "./api";
import CosmicCursor from "./components/CosmicCursor";
import Hero from "./components/Hero";
import MissionControl from "./components/MissionControl";
import EarthViewer from "./components/EarthViewer";
import MetricCard from "./components/MetricCard";
import InsightPanel from "./components/InsightPanel";
import ChatPanel from "./components/ChatPanel";
import DataConstellation from "./components/DataConstellation";
import Footer from "./components/Footer";
import OrbitalReceipt from "./components/OrbitalReceipt";
import ProductContextPanel from "./components/ProductContextPanel";
import AudienceModePanel from "./components/AudienceModePanel";
import ImprovementPanel from "./components/ImprovementPanel";
import CityComparisonPanel from "./components/CityComparisonPanel";

const layerOptions = [
  { key: "rgb", label: "RGB", icon: Satellite, description: "Natural satellite view" },
  { key: "ndvi", label: "NDVI", icon: Leaf, description: "Vegetation health" },
  { key: "ndwi", label: "NDWI", icon: Waves, description: "Water signal" },
  { key: "ndbi", label: "NDBI", icon: Map, description: "Built-up surface" },
  { key: "savi", label: "SAVI", icon: Trees, description: "Soil-adjusted vegetation" },
  { key: "classification", label: "Class", icon: Radar, description: "Land categories" },
  { key: "heat", label: "Heat", icon: Flame, description: "Urban heat signals" },
];

export default function App() {
  const [city, setCity] = useState("Ottawa");
  const [userType, setUserType] = useState("researcher");
  const [activeLayer, setActiveLayer] = useState("rgb");
  const [scanData, setScanData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [secretMode, setSecretMode] = useState(false);

  const selectedLayer = useMemo(
    () => layerOptions.find((item) => item.key === activeLayer),
    [activeLayer]
  );

  async function handleScan() {
    alert("API URL: " + import.meta.env.VITE_API_BASE_URL); // ADD THIS
  setLoading(true);
  
  async function handleScan() {
    setLoading(true);

    try {
      const data = await runScan({
        city,
        user_type: userType,
        layer_focus: activeLayer,
      });

      setScanData(data);
    } catch (error) {
      console.error(error);
      alert("EarthLens scan failed. Make sure FastAPI is running on port 8000.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className={`app ${secretMode ? "secret-mode" : ""}`}>
      <CosmicCursor />
      <DataConstellation />

      <Hero
        onLaunch={handleScan}
        loading={loading}
        secretMode={secretMode}
        onLogoClick={() => setSecretMode((current) => !current)}
      />

      <section className="mission-layout">
        <MissionControl
          city={city}
          setCity={setCity}
          userType={userType}
          setUserType={setUserType}
          onScan={handleScan}
          loading={loading}
        />

        <EarthViewer
          scanData={scanData}
          activeLayer={activeLayer}
          setActiveLayer={setActiveLayer}
          layerOptions={layerOptions}
          selectedLayer={selectedLayer}
          loading={loading}
        />

        <InsightPanel scanData={scanData} userType={userType} />
      </section>

      <section className="metrics-grid">
        <MetricCard icon={Leaf} label="Green Coverage" value={scanData ? `${scanData.metrics.green_pct}%` : "Awaiting scan"} tone="green" />
        <MetricCard icon={Trees} label="Dense Canopy" value={scanData ? `${scanData.metrics.dense_pct}%` : "Awaiting scan"} tone="mint" />
        <MetricCard icon={Droplets} label="Water Signal" value={scanData ? `${scanData.metrics.water_pct}%` : "Awaiting scan"} tone="blue" />
        <MetricCard icon={Flame} label="Heat Risk" value={scanData ? `${scanData.metrics.heat_risk_score}/100` : "Awaiting scan"} tone="orange" />
        <MetricCard icon={Activity} label="Temperature" value={scanData?.metrics?.temperature_c == null ? "Unavailable" : `${scanData.metrics.temperature_c}°C`} tone="blue" />
        <MetricCard icon={ShieldCheck} label="Reliability" value={scanData ? `${scanData.metrics.reliability_score}/100` : "Awaiting scan"} tone="violet" />
      </section>
      <OrbitalReceipt scanData={scanData} />
      <ProductContextPanel scanData={scanData} userType={userType} />
      <ImprovementPanel scanData={scanData} />
      <ChatPanel scanData={scanData} userType={userType} city={city} />
      <AudienceModePanel userType={userType} scanData={scanData} />
      <section className="section">
        <CityComparisonPanel />
      </section>

      <section className="section">
        <Footer />
      </section>
    </main>
  );
}