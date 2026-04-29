import { motion } from "framer-motion";
import { Crosshair, Rocket, SlidersHorizontal } from "lucide-react";

const cities = [
  "Ottawa",
  "Victoria",
  "Edmonton",
  "Winnipeg",
  "Toronto",
  "Halifax",
  "Charlottetown",
  "St. John's",
  "Whitehorse",
  "Yellowknife",
  "Iqaluit",
];

const userTypes = [
  { value: "kids", label: "Kid Explorer" },
  { value: "general", label: "General Public" },
  { value: "planner", label: "City / Weather Analyst" },
  { value: "researcher", label: "Researcher / Expert" },
];

export default function MissionControl({
  city,
  setCity,
  userType,
  setUserType,
  onScan,
  loading,
}) {
  return (
    <motion.aside
      className="mission-control glass"
      initial={{ opacity: 0, x: -24 }}
      animate={{ opacity: 1, x: 0 }}
    >
      <div className="panel-header">
        <SlidersHorizontal size={20} />
        <div>
          <span>Mission Control</span>
          <h2>Configure scan</h2>
        </div>
      </div>

      <label>Target city</label>
      <select value={city} onChange={(event) => setCity(event.target.value)}>
        {cities.map((item) => (
          <option key={item} value={item}>
            {item}
          </option>
        ))}
      </select>

      <label>Audience mode</label>
      <select value={userType} onChange={(event) => setUserType(event.target.value)}>
        {userTypes.map((item) => (
          <option key={item.value} value={item.value}>
            {item.label}
          </option>
        ))}
      </select>

      <div className="mission-stat">
        <Crosshair size={18} />
        <div>
          <b>Sentinel-2 scene source</b>
          <span>Canadian capital cities with mapped bounding boxes</span>
        </div>
      </div>

      <button className="primary-btn full" onClick={onScan} disabled={loading}>
        {loading ? "Contacting orbit..." : "Run intelligence scan"}
        <Rocket size={18} />
      </button>

      <div className="micro-note">
        Select a Canadian capital city to fetch a matching Sentinel-2 scene.
      </div>
    </motion.aside>
  );
}