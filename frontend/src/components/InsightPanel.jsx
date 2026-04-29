import { BrainCircuit, Cloud, Database, Microscope } from "lucide-react";

export default function InsightPanel({ scanData, userType }) {
  return (
    <aside className="insight-panel glass">
      <div className="panel-header">
        <BrainCircuit size={20} />
        <div>
          <span>AI Mission Brief</span>
          <h2>{userType === "kids" ? "Green Detective Notes" : "Intelligence brief"}</h2>
        </div>
      </div>

      {scanData ? (
        <>
          <p className="brief-text">{scanData.brief}</p>

          <div className="mini-metadata">
            <div>
              <Cloud size={16} />
              <span>Cloud cover</span>
              <b>{scanData.metadata.cloud_cover}%</b>
            </div>
            <div>
              <Database size={16} />
              <span>Satellite</span>
              <b>{scanData.metadata.satellite}</b>
            </div>
            <div>
              <Microscope size={16} />
              <span>Resolution</span>
              <b>{scanData.metadata.resolution}</b>
            </div>
          </div>

          <div className="research-notes">
            <h3>Research caveats</h3>
            {scanData.research_notes.map((note, index) => (
              <p key={index}>{note}</p>
            ))}
          </div>
        </>
      ) : (
        <p className="muted">
          Scan results will appear here with audience-aware explanation depth.
        </p>
      )}
    </aside>
  );
}