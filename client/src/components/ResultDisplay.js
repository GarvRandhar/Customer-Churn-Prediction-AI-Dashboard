import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, ArrowRight, RotateCcw, TrendingUp, Shield, Target } from 'lucide-react';

const GaugeChart = ({ value, isChurn }) => {
  const [animatedValue, setAnimatedValue] = useState(0);
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (animatedValue / 100) * circumference;

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedValue(value), 100);
    return () => clearTimeout(timer);
  }, [value]);

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="200" height="200" viewBox="0 0 200 200" className="-rotate-90">
        {/* Background track */}
        <circle
          cx="100" cy="100" r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth="12"
        />
        {/* Glow filter */}
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        {/* Progress arc */}
        <circle
          cx="100" cy="100" r={radius}
          fill="none"
          stroke={isChurn ? '#FB7185' : '#34D399'}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          filter="url(#glow)"
          className="transition-all duration-[1200ms] ease-out"
        />
      </svg>
      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-5xl font-bold ${isChurn ? 'text-status-danger' : 'text-status-success'}`}>
          {animatedValue}%
        </span>
        <span className="text-xs text-txt-muted mt-1 font-medium uppercase tracking-wider">
          Churn Risk
        </span>
      </div>
    </div>
  );
};

function ResultDisplay({ result, onNewPrediction }) {
  const isChurn = result.prediction === 'Churn';
  const probability = Math.round(result.probability * 100);
  const confidence = Math.round(result.confidence);

  const recommendations = isChurn
    ? [
        { icon: Target, text: 'Offer personalized retention incentives or loyalty programs' },
        { icon: Shield, text: 'Schedule a customer success review meeting' },
        { icon: TrendingUp, text: 'Provide premium support and dedicated account management' },
        { icon: ArrowRight, text: 'Consider special pricing or contract extensions' },
      ]
    : [
        { icon: TrendingUp, text: 'Focus on customer expansion opportunities' },
        { icon: Target, text: 'Implement referral and advocacy programs' },
        { icon: Shield, text: 'Provide proactive support to enhance satisfaction' },
        { icon: ArrowRight, text: 'Explore upsell and cross-sell opportunities' },
      ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-8 py-12 animate-fade-in">
      {/* Verdict */}
      <div className="text-center mb-8">
        <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold mb-6 ${
          isChurn
            ? 'bg-status-danger-bg border border-status-danger/30 text-status-danger'
            : 'bg-status-success-bg border border-status-success/30 text-status-success'
        }`}>
          {isChurn ? <AlertTriangle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
          {isChurn ? 'High Churn Risk' : 'Low Churn Risk'}
        </div>

        {/* Gauge */}
        <div className="mb-6">
          <GaugeChart value={probability} isChurn={isChurn} />
        </div>

        <p className="text-txt-secondary text-sm max-w-md mx-auto leading-relaxed">
          {isChurn
            ? 'This customer shows strong indicators of potential churn. Immediate retention action is recommended.'
            : 'This customer demonstrates strong satisfaction signals. Focus on loyalty enhancement strategies.'}
        </p>
      </div>

      {/* Metrics Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-2xl mb-10">
        <div className="bg-surface border border-surface-border rounded-xl p-5 text-center">
          <p className="text-[10px] text-txt-muted font-semibold uppercase tracking-widest mb-2">Churn Probability</p>
          <p className={`text-3xl font-bold ${isChurn ? 'text-status-danger' : 'text-status-success'}`}>{probability}%</p>
        </div>
        <div className="bg-surface border border-surface-border rounded-xl p-5 text-center">
          <p className="text-[10px] text-txt-muted font-semibold uppercase tracking-widest mb-2">Model Confidence</p>
          <p className="text-3xl font-bold text-accent-light">{confidence}%</p>
        </div>
        <div className="bg-surface border border-surface-border rounded-xl p-5 text-center">
          <p className="text-[10px] text-txt-muted font-semibold uppercase tracking-widest mb-2">Recommendation</p>
          <p className="text-xl font-bold text-txt-primary">{isChurn ? '🎯 Act Now' : '✓ Maintain'}</p>
        </div>
      </div>

      {/* Recommendations */}
      <div className="w-full max-w-2xl bg-surface border border-surface-border rounded-xl p-6 mb-8">
        <h3 className="text-sm font-semibold text-txt-primary mb-4 uppercase tracking-wider">Recommendations</h3>
        <div className="space-y-3">
          {recommendations.map((rec, i) => {
            const Icon = rec.icon;
            return (
              <div key={i} className="flex items-start gap-3">
                <div className="w-7 h-7 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Icon className="w-3.5 h-3.5 text-accent-light" />
                </div>
                <p className="text-sm text-txt-secondary leading-relaxed">{rec.text}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={onNewPrediction}
          className="flex items-center gap-2 px-8 py-3 rounded-xl text-sm font-semibold text-white bg-accent hover:bg-accent-dark shadow-glow hover:shadow-glow-lg transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98]"
        >
          <ArrowRight className="w-4 h-4" />
          New Prediction
        </button>
        <button
          onClick={() => window.location.reload()}
          className="flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-medium text-txt-secondary bg-surface border border-surface-border hover:border-surface-border-hover hover:text-txt-primary transition-all"
        >
          <RotateCcw className="w-4 h-4" />
          Reset
        </button>
      </div>
    </div>
  );
}

export default ResultDisplay;
