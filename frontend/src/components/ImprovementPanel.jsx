function generateInsights(metrics) {
  const insights = [];

  if (!metrics) return insights;

  const {
    green_pct,
    dense_pct,
    water_pct,
    built_up_pct,
    heat_risk_score,
  } = metrics;

  if (green_pct < 30) {
    insights.push({
      type: "warning",
      title: "Low vegetation coverage",
      desc: "Overall green coverage is limited. Increasing vegetation can improve cooling and livability.",
    });
  }

  if (dense_pct < 15) {
    insights.push({
      type: "warning",
      title: "Low dense canopy",
      desc: "Tree canopy is sparse. Dense canopy plays a key role in reducing urban heat.",
    });
  }

  if (heat_risk_score > 65) {
    insights.push({
      type: "risk",
      title: "Elevated heat risk",
      desc: "Built surfaces and limited vegetation may contribute to higher localized temperatures.",
    });
  }

  if (built_up_pct > 50) {
    insights.push({
      type: "info",
      title: "High built-surface presence",
      desc: "Urban surfaces dominate. Consider integrating green infrastructure where possible.",
    });
  }

  if (water_pct < 10) {
    insights.push({
      type: "info",
      title: "Limited water signal",
      desc: "Low presence of water bodies may reduce natural cooling effects.",
    });
  }

  return insights;
}

export default function ImprovementPanel({ scanData }) {
  if (!scanData) return null;

  const insights = generateInsights(scanData.metrics);

  if (insights.length === 0) return null;

  return (
    <section className="improvement-panel glass">
      <div className="panel-header">
        <span>Where to Improve</span>
        <h2>Priority Signals</h2>
      </div>

      <div className="improvement-grid">
        {insights.map((item, index) => (
          <div key={index} className={`improvement-card ${item.type}`}>
            <h3>{item.title}</h3>
            <p>{item.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}