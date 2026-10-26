const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  return (
    <main className="app-shell">
      <section className="hero-card">
        <p className="eyebrow">FastAPI + React</p>
        <h1>Your app starts here.</h1>
        <p className="intro">
          This Vite frontend is connected to the blueprint backend at
          <code>{apiUrl}</code>.
        </p>
        <a className="button" href={`${apiUrl}/api/v1/health`} target="_blank" rel="noreferrer">
          Check API health
        </a>
      </section>
    </main>
  );
}
