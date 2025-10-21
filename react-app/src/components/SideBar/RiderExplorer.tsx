interface RiderExplorerProps {
  selectedRider: string;
  onSelectionChange: (rider: string) => void;
}

const riders = ["Rider A", "Rider B", "Rider C"];

function RiderExplorer({ selectedRider, onSelectionChange }: RiderExplorerProps) {
  return (
    <div className="mt-4">
      <h4>Select Rider</h4>
      <ul className="list-group list-group-flush">
        {riders.map((rider) => (
          <li key={rider} className="list-group-item p-0 border-0">
            <button
              type="button"
              className={`list-group-item list-group-item-action ${
                selectedRider === rider ? "active" : ""
              }`}
              onClick={() => onSelectionChange(rider)}
            >
              {rider}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default RiderExplorer;
