import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, Satellite } from "lucide-react";

export default function EarthViewer({
  scanData,
  activeLayer,
  setActiveLayer,
  layerOptions,
  selectedLayer,
  loading,
}) {
  const [compareMode, setCompareMode] = useState(false);
  const [sliderValue, setSliderValue] = useState(55);

  const imageSrc = scanData?.layers?.[activeLayer];
  const canCompare = Boolean(imageSrc);

  return (
    <motion.section
      className="earth-viewer glass"
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="viewer-header">
        <div>
          <span className="eyebrow small">Earth Viewer</span>
          <h2>{selectedLayer?.label || "Satellite Layer"}</h2>
          <p>{selectedLayer?.description}</p>
        </div>

        <div className="layer-switcher">
          {layerOptions.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.key}
                className={activeLayer === item.key ? "active" : ""}
                onClick={() => setActiveLayer(item.key)}
              >
                <Icon size={16} />
                {item.label}
              </button>
            );
          })}
        </div>
      </div>

      {canCompare && (
        <div className="viewer-tools">
          <button
            type="button"
            className={compareMode ? "active" : ""}
            onClick={() => setCompareMode((current) => !current)}
          >
            {compareMode ? "Exit before / after" : "Before / after"}
          </button>

          {compareMode && (
            <span>
              Simulated improvement preview based on the active layer.
            </span>
          )}
        </div>
      )}

      <div className="map-frame">
        {!compareMode && (
          <>
            <div className="map-hud top-left">ORBITAL TILE 07-A</div>
            <div className="map-hud top-right">SENTINEL-2 L2A</div>
            <div className="map-hud bottom-left">{selectedLayer?.description}</div>
          </>
        )}

        {activeLayer === "heat" && !compareMode && (
          <div className="heat-legend">
            <span>Cooler</span>
            <div className="heat-gradient" />
            <span>Hotter</span>
          </div>
        )}

        {loading && (
          <div className="loading-layer">
            <Loader2 className="spin" size={36} />
            <span>Rendering intelligence layer...</span>
          </div>
        )}

        <AnimatePresence mode="wait">
          {imageSrc ? (
            compareMode ? (
              <motion.div
                key={`${activeLayer}-compare`}
                className="compare-frame"
                initial={{ opacity: 0, scale: 1.02 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{ duration: 0.35 }}
              >
                <img
                  src={imageSrc}
                  alt={`${selectedLayer?.label} before`}
                  className="satellite-layer-image compare-base"
                />

                <div
                  className="compare-after"
                  style={{ width: `${sliderValue}%` }}
                >
                  <img
                    src={imageSrc}
                    alt={`${selectedLayer?.label} after`}
                    className={`satellite-layer-image compare-enhanced ${activeLayer}`}
                  />
                </div>

                <div
                  className="compare-divider"
                  style={{ left: `${sliderValue}%` }}
                >
                  <span />
                </div>

                <div className="compare-label before">Current</div>
                <div className="compare-label after">Improved</div>

                <input
                  className="compare-slider"
                  type="range"
                  min="5"
                  max="95"
                  value={sliderValue}
                  onChange={(event) => setSliderValue(event.target.value)}
                  aria-label="Before and after comparison slider"
                />
              </motion.div>
            ) : (
              <motion.img
                key={activeLayer}
                src={imageSrc}
                alt={selectedLayer?.label}
                className="satellite-layer-image"
                initial={{ opacity: 0, scale: 1.03, filter: "blur(8px)" }}
                animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                exit={{ opacity: 0, scale: 0.98, filter: "blur(8px)" }}
                transition={{ duration: 0.35 }}
              />
            )
          ) : (
            <motion.div
              className="empty-orbit"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <Satellite size={54} />
              <h3>Awaiting orbital scan</h3>
              <p>Choose a city and launch a scan to light up the layer stack.</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.section>
  );
}