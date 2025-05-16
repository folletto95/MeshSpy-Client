import Topbar from "./components/Topbar";
import Sidebar from "./components/Sidebar";
import Metrics from "./components/Metrics";
import MapView from "./components/MapView";
import LogViewer from "./components/LogViewer";

export default function App() {
  return (
    <div className="h-screen flex flex-col">
      {/* Barra superiore */}
      <Topbar />

      {/* Contenuto principale */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 bg-gray-50 dark:bg-gray-800 p-6 overflow-y-auto space-y-6">
          <Metrics />
          <MapView />
          <LogViewer />
        </main>
      </div>
    </div>
  );
}
