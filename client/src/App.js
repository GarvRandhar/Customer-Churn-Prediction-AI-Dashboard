import React, { useState, useRef } from 'react';
import { AlertCircle, Loader, Activity, Cpu, Zap } from 'lucide-react';
import PredictionForm from './components/PredictionForm';
import ResultDisplay from './components/ResultDisplay';

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const formRef = useRef(null);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      let data;
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        throw new Error(`Server returned ${response.status}. Make sure the Flask backend is running on port 5000.`);
      }

      if (!response.ok) {
        throw new Error(data.error || 'Prediction failed');
      }

      if (data.success) {
        setResult(data);
      } else {
        setError(data.error || 'An error occurred');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-dark-900 flex flex-col">
      {/* Top Bar */}
      <header className="flex items-center justify-between px-8 py-4 border-b border-surface-border bg-dark-900/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center">
            <Activity className="w-4 h-4 text-accent-light" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-txt-primary tracking-tight leading-none">
              Churn Prediction
            </h1>
            <p className="text-xs text-txt-muted mt-0.5">AI-Powered Analytics</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface border border-surface-border">
            <Cpu className="w-3.5 h-3.5 text-accent-light" />
            <span className="text-xs font-medium text-txt-secondary">XGBoost</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-accent/10 text-accent-light font-medium">v1.0</span>
          </div>
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-status-success-bg border border-status-success/20">
            <div className="w-1.5 h-1.5 rounded-full bg-status-success animate-pulse-slow" />
            <span className="text-xs font-medium text-status-success">Online</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        {/* Error Banner */}
        {error && (
          <div className="mx-8 mt-6 p-4 bg-status-danger-bg border border-status-danger/20 rounded-xl flex gap-3 animate-slide-down">
            <AlertCircle className="w-5 h-5 text-status-danger flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-semibold text-status-danger text-sm">Prediction Failed</p>
              <p className="text-sm text-status-danger/80 mt-1">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-status-danger/60 hover:text-status-danger text-lg leading-none px-1"
            >
              ×
            </button>
          </div>
        )}

        {/* Loading Overlay — keeps form mounted underneath */}
        {loading && (
          <div className="fixed inset-0 z-40 bg-dark-900/80 backdrop-blur-sm flex flex-col items-center justify-center gap-6 animate-fade-in">
            <div className="relative">
              <div className="w-20 h-20 rounded-full border-2 border-surface-border flex items-center justify-center">
                <Loader className="w-8 h-8 text-accent-light animate-spin" />
              </div>
              <div className="absolute -inset-3 rounded-full border border-accent/10 animate-pulse-slow" />
            </div>
            <div className="text-center">
              <p className="text-txt-primary font-medium text-lg">Analyzing Customer Profile</p>
              <p className="text-txt-muted text-sm mt-1">Running prediction model…</p>
            </div>
          </div>
        )}

        {/* Form — always mounted when no result, so state is preserved on error */}
        {!result && (
          <div ref={formRef}>
            <PredictionForm onSubmit={handleSubmit} />
          </div>
        )}

        {/* Result */}
        {result && !loading && (
          <ResultDisplay result={result} onNewPrediction={() => setResult(null)} />
        )}
      </main>

      {/* Footer */}
      <footer className="px-8 py-4 border-t border-surface-border flex items-center justify-between">
        <div className="flex items-center gap-2 text-txt-muted text-xs">
          <Zap className="w-3 h-3" />
          <span>Powered by Machine Learning</span>
        </div>
        <p className="text-xs text-txt-muted/60">© 2026 Churn Prediction</p>
      </footer>
    </div>
  );
}

export default App;
