import PhoneFrame from "./components/PhoneFrame";
import Dashboard from "./screens/Dashboard";

export default function App() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#d7e4e0] p-6">
      <PhoneFrame>
        <Dashboard />
      </PhoneFrame>
    </div>
  );
}
