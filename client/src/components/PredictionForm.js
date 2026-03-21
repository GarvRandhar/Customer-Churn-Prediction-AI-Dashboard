import React, { useState } from 'react';
import { ChevronRight, ChevronLeft, Send, RotateCcw, User, Phone, Globe, FileText, DollarSign } from 'lucide-react';

const STEPS = [
  { id: 0, title: 'Demographics', icon: User, fields: ['gender', 'SeniorCitizen', 'Partner', 'Dependents'] },
  { id: 1, title: 'Services', icon: Phone, fields: ['tenure', 'PhoneService', 'MultipleLines', 'InternetService'] },
  { id: 2, title: 'Online Features', icon: Globe, fields: ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies'] },
  { id: 3, title: 'Contract & Billing', icon: FileText, fields: ['Contract', 'PaperlessBilling', 'PaymentMethod'] },
  { id: 4, title: 'Financials', icon: DollarSign, fields: ['MonthlyCharges', 'TotalCharges'] },
];

const FIELD_CONFIG = {
  gender: { label: 'Gender', options: [{ value: 'Male', label: 'Male' }, { value: 'Female', label: 'Female' }] },
  SeniorCitizen: { label: 'Senior Citizen', options: [{ value: '0', label: 'No' }, { value: '1', label: 'Yes' }] },
  Partner: { label: 'Partner', options: [{ value: 'Yes', label: 'Yes' }, { value: 'No', label: 'No' }] },
  Dependents: { label: 'Dependents', options: [{ value: 'Yes', label: 'Yes' }, { value: 'No', label: 'No' }] },
  tenure: { label: 'Tenure (months)', type: 'number' },
  PhoneService: { label: 'Phone Service', options: [{ value: 'Yes', label: 'Yes' }, { value: 'No', label: 'No' }] },
  MultipleLines: { label: 'Multiple Lines', options: [{ value: 'Yes', label: 'Yes' }, { value: 'No', label: 'No' }, { value: 'No phone service', label: 'No phone service' }] },
  InternetService: { label: 'Internet Service', options: [{ value: 'DSL', label: 'DSL' }, { value: 'Fiber optic', label: 'Fiber optic' }, { value: 'No', label: 'No' }] },
  OnlineSecurity: { label: 'Online Security', options: [{ value: 'Yes', label: 'Yes' }, { value: 'No', label: 'No' }, { value: 'No internet service', label: 'No internet service' }] },
  OnlineBackup: { label: 'Online Backup', options: [{ value: 'Yes', label: 'Yes' }, { value: 'No', label: 'No' }, { value: 'No internet service', label: 'No internet service' }] },
  DeviceProtection: { label: 'Device Protection', options: [{ value: 'Yes', label: 'Yes' }, { value: 'No', label: 'No' }, { value: 'No internet service', label: 'No internet service' }] },
  TechSupport: { label: 'Tech Support', options: [{ value: 'Yes', label: 'Yes' }, { value: 'No', label: 'No' }, { value: 'No internet service', label: 'No internet service' }] },
  StreamingTV: { label: 'Streaming TV', options: [{ value: 'Yes', label: 'Yes' }, { value: 'No', label: 'No' }, { value: 'No internet service', label: 'No internet service' }] },
  StreamingMovies: { label: 'Streaming Movies', options: [{ value: 'Yes', label: 'Yes' }, { value: 'No', label: 'No' }, { value: 'No internet service', label: 'No internet service' }] },
  Contract: { label: 'Contract', options: [{ value: 'Month-to-month', label: 'Month-to-month' }, { value: 'One year', label: 'One year' }, { value: 'Two year', label: 'Two year' }] },
  PaperlessBilling: { label: 'Paperless Billing', options: [{ value: 'Yes', label: 'Yes' }, { value: 'No', label: 'No' }] },
  PaymentMethod: { label: 'Payment Method', options: [{ value: 'Electronic check', label: 'Electronic check' }, { value: 'Mailed check', label: 'Mailed check' }, { value: 'Bank transfer (automatic)', label: 'Bank transfer' }, { value: 'Credit card (automatic)', label: 'Credit card' }] },
  MonthlyCharges: { label: 'Monthly Charges ($)', type: 'number' },
  TotalCharges: { label: 'Total Charges ($)', type: 'number' },
};

const FormField = ({ fieldKey, value, onChange }) => {
  const config = FIELD_CONFIG[fieldKey];
  if (!config) return null;
  const isSelect = config.options && config.options.length > 0;

  return (
    <div className="flex flex-col gap-2">
      <label className="text-xs font-semibold text-txt-secondary uppercase tracking-wider">
        {config.label}
      </label>
      {isSelect ? (
        <select
          name={fieldKey}
          value={value}
          onChange={onChange}
          className="w-full px-4 py-3 bg-dark-700 border border-surface-border rounded-xl text-txt-primary text-sm font-medium focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent hover:border-surface-border-hover transition-all cursor-pointer appearance-none"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23818CF8' d='M6 9L1 4h10z'/%3E%3C/svg%3E")`,
            backgroundRepeat: 'no-repeat',
            backgroundPosition: 'right 1rem center',
            paddingRight: '2.5rem',
          }}
        >
          <option value="">Select…</option>
          {config.options.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      ) : (
        <input
          type={config.type || 'text'}
          name={fieldKey}
          value={value}
          onChange={onChange}
          step={config.type === 'number' ? '0.01' : undefined}
          min={config.type === 'number' ? '0' : undefined}
          placeholder={`Enter ${config.label.toLowerCase()}`}
          className="w-full px-4 py-3 bg-dark-700 border border-surface-border rounded-xl text-txt-primary placeholder-txt-muted text-sm font-medium focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent hover:border-surface-border-hover transition-all"
        />
      )}
    </div>
  );
};

function PredictionForm({ onSubmit }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    gender: '', SeniorCitizen: '', Partner: '', Dependents: '',
    tenure: '', PhoneService: '', MultipleLines: '', InternetService: '',
    OnlineSecurity: '', OnlineBackup: '', DeviceProtection: '', TechSupport: '',
    StreamingTV: '', StreamingMovies: '', Contract: '', PaperlessBilling: '',
    PaymentMethod: '', MonthlyCharges: '', TotalCharges: '',
  });
  const [stepErrors, setStepErrors] = useState([]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setStepErrors((prev) => prev.filter((f) => f !== name));
  };

  const validateStep = (stepIndex) => {
    const step = STEPS[stepIndex];
    const missing = step.fields.filter((f) => !formData[f]);
    setStepErrors(missing);
    return missing.length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((s) => Math.min(s + 1, STEPS.length - 1));
    }
  };

  const handleBack = () => {
    setStepErrors([]);
    setCurrentStep((s) => Math.max(s - 1, 0));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validateStep(currentStep)) return;

    const processedData = {
      ...formData,
      SeniorCitizen: parseInt(formData.SeniorCitizen),
      tenure: parseInt(formData.tenure),
      MonthlyCharges: parseFloat(formData.MonthlyCharges),
      TotalCharges: parseFloat(formData.TotalCharges),
    };
    onSubmit(processedData);
  };

  const handleReset = () => {
    setFormData(Object.fromEntries(Object.keys(formData).map((k) => [k, ''])));
    setStepErrors([]);
    setCurrentStep(0);
  };

  const step = STEPS[currentStep];
  const isLastStep = currentStep === STEPS.length - 1;
  const filledCount = Object.values(formData).filter(Boolean).length;
  const totalFields = Object.keys(formData).length;
  const progressPercent = Math.round((filledCount / totalFields) * 100);

  return (
    <div className="flex-1 flex flex-col">
      {/* Progress Bar */}
      <div className="px-8 pt-6 pb-2">
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs text-txt-muted font-medium">
            Step {currentStep + 1} of {STEPS.length}
          </p>
          <p className="text-xs text-txt-muted font-medium">
            {filledCount}/{totalFields} fields completed
          </p>
        </div>
        <div className="w-full h-1 bg-dark-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-accent to-accent-light rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Step Indicators */}
      <div className="px-8 py-4 flex gap-2 overflow-x-auto">
        {STEPS.map((s, i) => {
          const StepIcon = s.icon;
          const isActive = i === currentStep;
          const isDone = i < currentStep;
          const stepFieldsFilled = s.fields.every((f) => formData[f]);

          return (
            <button
              key={s.id}
              type="button"
              onClick={() => {
                if (i < currentStep || (i === currentStep + 1 && validateStep(currentStep))) {
                  setStepErrors([]);
                  setCurrentStep(i);
                }
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium whitespace-nowrap transition-all duration-200 border ${
                isActive
                  ? 'bg-accent/15 border-accent/40 text-accent-light shadow-glow'
                  : isDone || stepFieldsFilled
                  ? 'bg-surface border-surface-border text-status-success hover:border-surface-border-hover'
                  : 'bg-surface border-surface-border text-txt-muted hover:border-surface-border-hover'
              }`}
            >
              <StepIcon className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">{s.title}</span>
              {(isDone || stepFieldsFilled) && !isActive && (
                <span className="text-status-success">✓</span>
              )}
            </button>
          );
        })}
      </div>

      {/* Step Content */}
      <form onSubmit={handleSubmit} className="flex-1 flex flex-col px-8 pb-8">
        <div className="flex-1">
          {/* Step Header */}
          <div className="mb-6 animate-fade-in" key={currentStep}>
            <h2 className="text-2xl font-semibold text-txt-primary tracking-tight">
              {step.title}
            </h2>
            <p className="text-sm text-txt-muted mt-1">
              {currentStep === 0 && 'Basic customer demographic information'}
              {currentStep === 1 && 'Telecommunication service details'}
              {currentStep === 2 && 'Online and streaming service subscriptions'}
              {currentStep === 3 && 'Contract type, billing, and payment preferences'}
              {currentStep === 4 && 'Monthly and total charge information'}
            </p>
          </div>

          {/* Fields Grid */}
          <div
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 animate-slide-up"
            key={`fields-${currentStep}`}
          >
            {step.fields.map((fieldKey) => (
              <div key={fieldKey} className={stepErrors.includes(fieldKey) ? 'ring-1 ring-status-danger/50 rounded-xl' : ''}>
                <FormField
                  fieldKey={fieldKey}
                  value={formData[fieldKey]}
                  onChange={handleChange}
                />
              </div>
            ))}
          </div>

          {/* Validation message */}
          {stepErrors.length > 0 && (
            <p className="mt-4 text-xs text-status-danger font-medium animate-slide-down">
              Please fill in all fields before continuing
            </p>
          )}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between pt-8 mt-8 border-t border-surface-border">
          <div className="flex gap-3">
            {currentStep > 0 && (
              <button
                type="button"
                onClick={handleBack}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium text-txt-secondary bg-surface border border-surface-border hover:border-surface-border-hover hover:text-txt-primary transition-all"
              >
                <ChevronLeft className="w-4 h-4" />
                Back
              </button>
            )}
            <button
              type="button"
              onClick={handleReset}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium text-txt-muted bg-transparent border border-surface-border hover:border-surface-border-hover hover:text-txt-secondary transition-all"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset
            </button>
          </div>

          {isLastStep ? (
            <button
              type="submit"
              className="flex items-center gap-2 px-8 py-2.5 rounded-xl text-sm font-semibold text-white bg-accent hover:bg-accent-dark shadow-glow hover:shadow-glow-lg transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98]"
            >
              <Send className="w-4 h-4" />
              Predict Churn
            </button>
          ) : (
            <button
              type="button"
              onClick={handleNext}
              className="flex items-center gap-2 px-8 py-2.5 rounded-xl text-sm font-semibold text-white bg-accent hover:bg-accent-dark shadow-glow hover:shadow-glow-lg transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98]"
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </form>
    </div>
  );
}

export default PredictionForm;
