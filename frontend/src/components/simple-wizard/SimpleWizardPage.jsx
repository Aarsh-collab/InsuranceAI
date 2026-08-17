import { Link } from "react-router-dom";
import { SimpleWizard } from "./SimpleWizard";

export default function SimpleWizardPage() {
  const handleComplete = (payload) => {
    console.info("[simple-wizard] intake complete", payload);
  };

  return (
    <main className="min-h-screen bg-black px-4 py-10 text-zinc-100">
      <div className="mx-auto flex w-full max-w-xl flex-col gap-6">
        <div className="space-y-3">
          <h1 className="text-3xl font-semibold tracking-tight text-white">
            Simple financial snapshot
          </h1>
          <p className="text-sm leading-relaxed text-zinc-400">
            Answer a few questions for preliminary life-insurance context. Not a
            quote or advice.
          </p>
          <Link
            to="/"
            className="inline-block text-sm text-zinc-500 underline-offset-4 hover:text-zinc-300 hover:underline"
          >
            Back to home
          </Link>
        </div>
        <SimpleWizard onComplete={handleComplete} />
      </div>
    </main>
  );
}
