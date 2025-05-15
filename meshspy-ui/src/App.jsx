import Topbar from "./components/Topbar";
import Sidebar from "./components/Sidebar";
import Metrics from "./components/Metrics";
import MapView from "./components/MapView";
import LogViewer from "./components/LogViewer";

export default function App() {
  return (
    <div className="h-screen flex flex-col">
      <Topbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 bg-gray-50 p-6 overflow-y-auto space-y-6">
          <Metrics />
          <MapView />
          <LogViewer />
        </main>
      </div>
    </div>
  );
}
