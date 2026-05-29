import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { clearAdminToken, fetchLeads, setAdminToken } from "../../services/adminApi";

function AdminLogin() {
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const [isChecking, setIsChecking] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    const trimmed = token.trim();
    if (!trimmed) {
      return;
    }

    setError("");
    setIsChecking(true);

    try {
      setAdminToken(trimmed);
      await fetchLeads();
      navigate("/admin", { replace: true });
    } catch {
      clearAdminToken();
      setError("Invalid admin token or admin service unavailable.");
    } finally {
      setIsChecking(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#070809] px-4 text-white">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-xl border border-white/[0.08] bg-[#0f1012] p-7 shadow-[0_24px_80px_rgba(0,0,0,0.42)]"
      >
        <div className="flex h-11 w-11 items-center justify-center rounded-lg border border-[#d7ad55]/25 bg-[#d7ad55]/10 text-sm font-semibold text-[#f2d28c]">
          IA
        </div>
        <p className="mt-5 text-[11px] uppercase tracking-[0.22em] text-[#d7ad55]">
          InsuranceAI
        </p>
        <h1 className="mt-2 text-2xl font-semibold tracking-[-0.02em]">Underwriting Console</h1>
        <p className="mt-2 text-sm leading-6 text-white/50">
          Enter the deployment admin token to review leads, quotes, applications, and conversation history.
        </p>

        <label className="mt-6 block text-sm font-medium text-white/68" htmlFor="admin-token">
          Admin token
        </label>
        <input
          id="admin-token"
          type="password"
          value={token}
          onChange={(event) => setToken(event.target.value)}
          className="mt-2 h-11 w-full rounded-md border border-white/[0.09] bg-[#151618] px-3 text-sm text-white outline-none transition placeholder:text-white/30 focus:border-[#d7ad55]/60"
        />

        {error && (
          <div className="mt-4 rounded-md border border-red-400/20 bg-red-500/10 px-3 py-2 text-sm text-red-100">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isChecking}
          className="mt-5 h-11 w-full rounded-md bg-[#d7ad55] text-sm font-semibold text-[#111111] transition hover:bg-[#e1bd6a] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isChecking ? "Checking access..." : "Continue"}
        </button>
      </form>
    </main>
  );
}

export default AdminLogin;
