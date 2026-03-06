APP_CSS = """
<style>
:root {
  --bg-1: #2a0b10;
  --bg-2: #14070a;
  --bg-3: #090304;
  --surface: rgba(255, 255, 255, 0.05);
  --surface-2: rgba(255, 255, 255, 0.08);
  --border: rgba(255, 255, 255, 0.12);
  --muted: rgba(255, 255, 255, 0.65);
  --accent: #ef4444;
  --accent-soft: rgba(248, 113, 113, 0.16);
}

.stApp {
  background: radial-gradient(circle at top, var(--bg-1) 0%, var(--bg-2) 45%, var(--bg-3) 100%);
  color: #fff;
}

.block-container {
  max-width: 1200px;
  padding-top: 2rem;
  padding-bottom: 2rem;
}

.vz-panel {
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: 20px;
  padding: 1rem 1.2rem;
  backdrop-filter: blur(12px);
}

.vz-kicker {
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 0.75rem;
  color: rgba(252, 165, 165, 0.9);
  margin-bottom: 0.35rem;
}

.vz-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
}

.vz-subtitle {
  color: var(--muted);
  font-size: 0.95rem;
}

.vz-card {
  border: 1px solid var(--border);
  background: linear-gradient(180deg, rgba(18, 24, 44, 0.92), rgba(9, 12, 24, 0.95));
  border-radius: 20px;
  padding: 1rem;
  margin-bottom: 0.8rem;
}

.vz-badge {
  display: inline-block;
  border: 1px solid rgba(252, 165, 165, 0.35);
  background: rgba(252, 165, 165, 0.14);
  color: #fecaca;
  border-radius: 999px;
  font-size: 0.72rem;
  padding: 0.2rem 0.6rem;
  margin-bottom: 0.6rem;
}

.vz-spec {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0.45rem 0.6rem;
  background: var(--surface-2);
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.86);
  margin-bottom: 0.45rem;
}

.vz-answer {
  border-left: 4px solid var(--accent);
  background: var(--accent-soft);
  border-radius: 8px;
  padding: 0.8rem 1rem;
  white-space: pre-wrap;
}

.stTextInput > div > div > input {
  border-radius: 12px;
  border: 1px solid var(--border);
  background: rgba(12, 19, 36, 0.9);
  color: white;
}

.stButton > button {
  border-radius: 12px;
  border: none;
  color: white;
  font-weight: 600;
  background: linear-gradient(90deg, #ef4444, #f43f5e);
}
</style>
"""
