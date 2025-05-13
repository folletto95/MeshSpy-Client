import React from "react";
import Sidebar from "./components/Sidebar";
import MapView from "./components/MapView";
import Topbar from "./components/Topbar";
import Metrics from "./components/Metrics";
import LogViewer from "./components/LogViewer";

export default function App() {
  return (
    <div className="h-screen flex flex-col">
      <Topbar />
      <div className="flex flex-1">
        <Sidebar />
        <div className="flex flex-col flex-1">
          <Metrics />
          <MapView />
        </div>
      </div>
      <LogViewer />
    </div>
  );
}
