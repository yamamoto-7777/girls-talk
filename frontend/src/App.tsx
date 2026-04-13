import { VTuberView } from "./components/VTuberView";
import "./App.css";

function App() {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">アイ の配信</h1>
      </header>
      <main className="app-panel">
        <VTuberView />
      </main>
    </div>
  );
}

export default App;
