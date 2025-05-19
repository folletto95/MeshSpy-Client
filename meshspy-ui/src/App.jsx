import Topbar from "./components/Topbar";
import Sidebar from "./components/Sidebar";
import Metrics from "./components/Metrics";
import MapView from "./components/MapView";
import LogViewer from "./components/LogViewer";
import StatusBanner from "./components/StatusBanner";
import Dashboard from "./components/Dashboard";

export default function App() {
  return (
    <div className="h-screen flex flex-col">
      <Topbar />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar: altezza piena */}
        <Sidebar />

        {/* Contenuto principale con scroll se necessario */}
        <main className="flex-1 bg-gray-50 dark:bg-gray-900 p-6 overflow-y-auto flex flex-col gap-6">
          <StatusBanner />
          <Dashboard />
          <MapView />
          <LogViewer />
                  </main>
      </div>
    </div>
  );
}
