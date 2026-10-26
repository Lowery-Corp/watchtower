const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  return (
    <main className="grid min-h-screen place-items-center bg-[radial-gradient(circle_at_top,_#1e293b,_#020617_60%)] p-8 text-slate-200">
      <section className="w-full max-w-2xl rounded-3xl border border-slate-700 bg-slate-900/80 p-[clamp(2rem,6vw,5rem)] shadow-[0_2rem_6rem_rgba(0,0,0,0.35)]">
        <p className="mb-4 font-bold uppercase tracking-[0.12em] text-sky-400">FastAPI + React + Tailwind</p>
        <h1 className="m-0 max-w-[12ch] text-[clamp(2.75rem,8vw,5rem)] font-bold leading-[0.95] tracking-[-0.05em]">Your app starts here.</h1>
        <p className="text-lg leading-relaxed text-slate-400">
          This Vite frontend is connected to the blueprint backend at
          <code className="ml-1 text-sky-200">{apiUrl}</code>.
        </p>
        <a className="mt-4 inline-block rounded-xl bg-sky-400 px-5 py-3 font-bold text-sky-950 no-underline transition hover:bg-sky-300" href={`${apiUrl}/api/v1/health`} target="_blank" rel="noreferrer">
          Check API health
        </a>
      </section>
    </main>
  );
}
