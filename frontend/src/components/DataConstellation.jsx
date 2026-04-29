export default function DataConstellation() {
  return (
    <div className="constellation" aria-hidden="true">
      {Array.from({ length: 34 }).map((_, index) => (
        <span
          key={index}
          style={{
            "--x": `${Math.random() * 100}%`,
            "--y": `${Math.random() * 100}%`,
            "--delay": `${Math.random() * 6}s`,
          }}
        />
      ))}
    </div>
  );
}