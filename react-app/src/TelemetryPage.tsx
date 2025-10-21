import { useState } from "react";
import RunExplorer from "./components/SideBar/RunExplorer";
import RiderExplorer from "./components/SideBar/RiderExplorer";
import Dashboard from "./components/GraphDashboard";
import NavBar from "./components/NavBar";

function TelemetryPage() {
  const [selectedRuns, setSelectedRuns] = useState<string[]>([]);
  const [selectedRider, setSelectedRider] = useState<string>("");

  return (
    <div className="container-fluid d-flex flex-column vh-100 p-0">
      {/* Navbar */}
      <NavBar />

      {/* Main content: sidebar + dashboard */}
      <div className="row flex-grow-1 m-0">
        {/* Sidebar */}
        <div className="col-3 border-end overflow-auto p-3">
          <RunExplorer
            selectedItems={selectedRuns}
            onSelectionChange={setSelectedRuns}
          />
          <RiderExplorer
            selectedRider={selectedRider}
            onSelectionChange={setSelectedRider}
          />
        </div>

        {/* Dashboard */}
        <div className="col-9 overflow-auto p-3">
          <Dashboard
            selectedRuns={selectedRuns}
            selectedRider={selectedRider}
          />
        </div>
      </div>
    </div>
  );
}

export default TelemetryPage;
