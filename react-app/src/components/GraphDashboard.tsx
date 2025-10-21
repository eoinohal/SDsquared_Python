interface GraphDashboardProps {
  selectedRuns: string[];
  selectedRider: string;
}

function GraphDashboard({ selectedRuns, selectedRider }: GraphDashboardProps) {
  const hasRuns = selectedRuns.length > 0;
  const hasRider = selectedRider !== "";

  return (
    <div className="p-3">
      <h4>Dashboard</h4>

      {!hasRuns && !hasRider ? (
        <p className="text-muted">No runs or riders selected.</p>
      ) : (
        <>
          {hasRuns && (
            <>
              <h5>Selected Runs</h5>
              <ul>
                {selectedRuns.map((run) => (
                  <li key={run}>{run}</li>
                ))}
              </ul>
            </>
          )}

          {hasRider && (
            <>
              <h5>Selected Rider</h5>
              <ul>
                <li>{selectedRider}</li>
              </ul>
            </>
          )}
        </>
      )}

      <b>Graphs will be shown here when linked</b>
    </div>
  );
}

export default GraphDashboard;
