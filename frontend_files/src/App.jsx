// src/App.jsx
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import Metrics from "./components/Metrics";
import MapView from "./components/MapView";
import LogViewer from "./components/LogViewer";

export default function App() {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Topbar />
        <main className="p-4 space-y-4 overflow-auto">
          <Metrics />
          <MapView />
          <LogViewer />
        </main>
      </div>
    </div>
  );
}
