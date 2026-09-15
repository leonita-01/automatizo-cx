import { useState } from "react";

import Shell from "./components/Shell";
import OperationsDashboard from "./pages/OperationsDashboard";


export default function App() {
  const [activeView, setActiveView] = useState("overview");

  return (
    <Shell activeView={activeView} onNavigate={setActiveView}>
      <OperationsDashboard
        activeView={activeView}
        onNavigate={setActiveView}
      />
    </Shell>
  );
}
