import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, Orbit, Satellite, Sparkles, X } from "lucide-react";

const ORBIT_NOTES = [
  "Sentinel-2 revisits the same area about every 5 days with its twin satellites.",
  "Healthy vegetation reflects near-infrared light strongly, which is why satellites can detect plant health.",
  "Urban heat islands often appear where vegetation is low and hard surfaces are high.",
  "A single satellite scene can contain millions of pixels, each holding spectral information.",
  "Water, vegetation, and concrete each reflect light differently across satellite bands.",
];

export default function Hero({ onLaunch, loading, secretMode, onLogoClick }) {
  const note = ORBIT_NOTES[Math.floor(Math.random() * ORBIT_NOTES.length)];

  return (
    <section className="hero">
      <nav className="top-nav">
        <button className="brand" onClick={onLogoClick} title="Orbit note">
          <span className="brand-mark">
            <Satellite size={18} />
          </span>
          EARTHLENS
        </button>

        <div className="nav-pills">
          <span>Sentinel-2</span>
          <span>Urban Canopy</span>
          <span>Climate Signals</span>
        </div>
      </nav>

      <AnimatePresence>
        {secretMode && (
          <motion.div
            className="orbit-note"
            initial={{ opacity: 0, y: -12, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -12, scale: 0.96 }}
          >
            <div>
              <b>Orbit Note</b>
              <p>{note}</p>
            </div>
            <X size={16} onClick={onLogoClick} />
          </motion.div>
        )}
      </AnimatePresence>

      <div className="hero-grid">
        <motion.div
          className="hero-copy"
          initial={{ opacity: 0, y: 26 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="eyebrow">
            <Sparkles size={16} />
            Urban Green Space Intelligence
          </div>

          <h1>
            See how cities breathe,
            <span> pixel by pixel.</span>
          </h1>

          <p>
            EarthLens turns Sentinel-2 imagery into vegetation, water, built-surface,
            and heat-risk intelligence for clearer environmental decisions.
          </p>

          <div className="hero-actions">
            <button className="primary-btn" onClick={onLaunch}>
              {loading ? "Processing satellite scene..." : "Run city scan"}
              <ArrowRight size={18} />
            </button>

            <div className="status-chip">
              <span />
              Satellite pipeline active
            </div>
          </div>
        </motion.div>

        <motion.div
          className="orbital-card"
          initial={{ opacity: 0, scale: 0.92, rotate: -4 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          transition={{ delay: 0.12 }}
        >
          <div className="planet">
            <div className="planet-shine" />
            <div className="scan-line" />
          </div>

          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="mini-satellite">
            <Orbit size={24} />
          </div>

          <div className="floating-label top">
            <b>NDVI</b>
            <span>Vegetation health</span>
          </div>

          <div className="floating-label bottom">
            <b>10m</b>
            <span>Target spatial resolution</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}