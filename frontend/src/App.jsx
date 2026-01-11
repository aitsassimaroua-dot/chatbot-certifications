import { Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import Register from "./pages/Register";
import Dashboard from "./components/Dashboard";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/chat" element={<Dashboard />} />
    </Routes>
  );
}

export default App;
