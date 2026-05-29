const styles = {
  high: "bg-emerald-500/10 text-emerald-200 border-emerald-400/20",
  medium: "bg-amber-400/10 text-amber-200 border-amber-300/20",
  low: "bg-red-500/10 text-red-200 border-red-400/20",
  gold: "bg-[#d7ad55]/10 text-[#f2d28c] border-[#d7ad55]/25",
  neutral: "bg-white/[0.04] text-white/60 border-white/10",
};

function StatusBadge({ children, tone = "neutral" }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-medium uppercase tracking-[0.08em] ${styles[tone] || styles.neutral}`}
    >
      {children}
    </span>
  );
}

export default StatusBadge;
