import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { clearAdminToken } from "../../services/adminApi";

const navItems = [
  { label: "Dashboard", to: "/admin", enabled: true },
  { label: "Leads", to: "/admin/leads", enabled: true },
  { label: "Applications", enabled: false },
  { label: "Quotes", enabled: false },
  { label: "Underwriting", enabled: false },
  { label: "Clients", enabled: false },
  { label: "Reports", enabled: false },
  { label: "Settings", enabled: false },
];

function AdminLayout() {
  const navigate = useNavigate();

  const logout = () => {
    clearAdminToken();
    navigate("/admin/login", { replace: true });
  };

  return (
    <div className="min-h-screen bg-[#070809] text-white">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-white/[0.08] bg-[#0c0d0f] p-5 shadow-[18px_0_60px_rgba(0,0,0,0.22)] lg:block">
        <div className="mb-8 border-b border-white/[0.08] pb-5">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-[#d7ad55]/25 bg-[#d7ad55]/10 text-sm font-semibold text-[#f2d28c]">
            IA
          </div>
          <p className="mt-4 text-[11px] uppercase tracking-[0.2em] text-[#d7ad55]">InsuranceAI</p>
          <h1 className="mt-1 text-lg font-semibold tracking-[-0.01em]">Underwriting Console</h1>
          <p className="mt-1 text-xs leading-5 text-white/42">Operational lead and quote review</p>
        </div>

        <nav className="space-y-1">
          {navItems.map((item) => (
            item.enabled ? (
              <NavLink
                key={item.label}
                to={item.to}
                end={item.to === "/admin"}
                className={({ isActive }) =>
                  `flex items-center justify-between rounded-md px-3 py-2.5 text-sm transition ${
                    isActive
                      ? "border border-[#d7ad55]/20 bg-[#d7ad55]/10 text-[#f2d28c]"
                      : "text-white/62 hover:bg-white/[0.04] hover:text-white"
                  }`
                }
              >
                <span>{item.label}</span>
              </NavLink>
            ) : (
              <div
                key={item.label}
                className="flex cursor-not-allowed items-center justify-between rounded-md px-3 py-2.5 text-sm text-white/28"
              >
                <span>{item.label}</span>
                <span className="text-[10px] uppercase tracking-[0.12em]">Soon</span>
              </div>
            )
          ))}
        </nav>

        <button
          type="button"
          onClick={logout}
          className="absolute bottom-5 left-5 right-5 rounded-md border border-white/[0.08] px-3 py-2.5 text-sm text-white/55 transition hover:border-white/15 hover:bg-white/[0.04] hover:text-white"
        >
          Log out
        </button>
      </aside>

      <main className="min-h-screen lg:pl-72">
        <div className="border-b border-white/[0.08] bg-[#0c0d0f] px-4 py-4 lg:hidden">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold">InsuranceAI Console</span>
            <button
              type="button"
              onClick={logout}
              className="rounded-md border border-white/[0.1] px-3 py-1.5 text-sm text-white/65"
            >
              Log out
            </button>
          </div>
          <div className="mt-3 flex gap-2">
            {navItems.filter((item) => item.enabled).map((item) => (
              <NavLink
                key={item.label}
                to={item.to}
                end={item.to === "/admin"}
                className={({ isActive }) =>
                  `rounded-md px-3 py-1.5 text-sm ${
                    isActive ? "bg-[#d7ad55]/12 text-[#f2d28c]" : "bg-white/[0.04] text-white/60"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>

        <div className="mx-auto max-w-[1500px] p-4 sm:p-6 lg:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export default AdminLayout;
