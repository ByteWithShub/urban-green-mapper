import { motion } from "framer-motion";

export default function MetricCard({ icon: Icon, label, value, tone }) {
  return (
    <motion.div
      className={`metric-card glass ${tone}`}
      whileHover={{ y: -6, scale: 1.02 }}
      transition={{ type: "spring", stiffness: 260, damping: 18 }}
    >
      <div className="metric-icon">
        <Icon size={22} />
      </div>
      <span>{label}</span>
      <strong>{value}</strong>
    </motion.div>
  );
}