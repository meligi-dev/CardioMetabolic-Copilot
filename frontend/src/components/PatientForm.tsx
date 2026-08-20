import React, { useState } from 'react';
import type { PatientParameters } from '../types';
import { Activity, Stethoscope, Sparkles } from 'lucide-react';

interface Props {
  onAnalyze: (params: PatientParameters) => void;
  isLoading: boolean;
}

const PRESET_CASES: { name: string; desc: string; data: PatientParameters }[] = [
  {
    name: "Case 1: T2D + CKD (eGFR 34) + Prior MI",
    desc: "64yo with uncontrolled diabetes, stage 3b CKD, and past myocardial infarction.",
    data: {
      age: 64,
      gender: "Male",
      hba1c: 8.9,
      egfr: 34,
      uacr: 180,
      blood_pressure: "142/86",
      lvef: 55,
      has_ascvd: true,
      has_heart_failure: false,
      has_ckd: true,
      current_medications: ["Metformin 1000mg BID", "Atorvastatin 40mg", "Lisinopril 20mg"],
      allergies_or_intolerances: ["None reported"],
      clinical_notes: "Patient reports worsening fatigue. Creatinine has risen over the last 6 months."
    }
  },
  {
    name: "Case 2: T2D + HFrEF (LVEF 30%)",
    desc: "58yo newly diagnosed with Heart Failure with Reduced EF and Type 2 Diabetes.",
    data: {
      age: 58,
      gender: "Female",
      hba1c: 7.8,
      egfr: 52,
      uacr: 45,
      blood_pressure: "135/80",
      lvef: 30,
      has_ascvd: false,
      has_heart_failure: true,
      has_ckd: false,
      current_medications: ["Metformin 500mg BID", "Carvedilol 12.5mg BID"],
      allergies_or_intolerances: [],
      clinical_notes: "Echo shows severe LV systolic dysfunction (EF 30%). Complains of dyspnea on exertion."
    }
  },
  {
    name: "Case 3: Obese T2D + Severe CKD (eGFR 24)",
    desc: "71yo obese patient with eGFR < 30 requiring glycemic control and kidney protection.",
    data: {
      age: 71,
      gender: "Male",
      hba1c: 9.4,
      egfr: 24,
      uacr: 420,
      blood_pressure: "150/92",
      lvef: 50,
      has_ascvd: true,
      has_heart_failure: false,
      has_ckd: true,
      current_medications: ["Glimepiride 4mg daily", "Metformin 1000mg daily", "Amlodipine 10mg"],
      allergies_or_intolerances: ["Sulfa allergy"],
      clinical_notes: "Severe microvascular disease. Metformin and Sulfonylurea safety needs immediate review."
    }
  }
];

export const PatientForm: React.FC<Props> = ({ onAnalyze, isLoading }) => {
  const [params, setParams] = useState<PatientParameters>(PRESET_CASES[0].data);
  const [medInput, setMedInput] = useState<string>(params.current_medications?.join(", ") || "");

  const handleApplyPreset = (preset: typeof PRESET_CASES[0]) => {
    setParams(preset.data);
    setMedInput(preset.data.current_medications?.join(", ") || "");
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const meds = medInput.split(",").map(m => m.trim()).filter(Boolean);
    onAnalyze({
      ...params,
      current_medications: meds
    });
  };

  return (
    <div className="card">
      <div className="card-title">
        <Stethoscope size={18} color="var(--brand-primary)" />
        <span>Patient Clinical Parameters</span>
      </div>

      {/* Presets Chips */}
      <div style={{ marginBottom: "16px" }}>
        <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "#64748b", marginBottom: "6px" }}>
          QUICK CLINICAL PRESET VIGNETTES:
        </div>
        <div className="presets-container">
          {PRESET_CASES.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              className="preset-chip"
              onClick={() => handleApplyPreset(preset)}
            >
              <Sparkles size={12} color="var(--brand-primary)" />
              <span>{preset.name}</span>
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Age (years)</label>
            <input
              type="number"
              className="form-input"
              value={params.age || ""}
              onChange={e => setParams({ ...params, age: Number(e.target.value) })}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Gender</label>
            <select
              className="form-select"
              value={params.gender || "Male"}
              onChange={e => setParams({ ...params, gender: e.target.value })}
            >
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">HbA1c (%)</label>
            <input
              type="number"
              step="0.1"
              className="form-input"
              value={params.hba1c || ""}
              onChange={e => setParams({ ...params, hba1c: Number(e.target.value) })}
              placeholder="e.g. 8.5"
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">eGFR (mL/min/1.73m²)</label>
            <input
              type="number"
              className="form-input"
              value={params.egfr || ""}
              onChange={e => setParams({ ...params, egfr: Number(e.target.value) })}
              placeholder="e.g. 35"
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Blood Pressure (mmHg)</label>
            <input
              type="text"
              className="form-input"
              value={params.blood_pressure || ""}
              onChange={e => setParams({ ...params, blood_pressure: e.target.value })}
              placeholder="e.g. 138/84"
            />
          </div>
          <div className="form-group">
            <label className="form-label">LVEF (Ejection Fraction %)</label>
            <input
              type="number"
              className="form-input"
              value={params.lvef || ""}
              onChange={e => setParams({ ...params, lvef: Number(e.target.value) })}
              placeholder="e.g. 35 or 55"
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">UACR (Albuminuria mg/g)</label>
          <input
            type="number"
            className="form-input"
            value={params.uacr || ""}
            onChange={e => setParams({ ...params, uacr: Number(e.target.value) })}
            placeholder="e.g. 150"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Comorbidities & Risk Factors</label>
          <div className="checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={!!params.has_ascvd}
                onChange={e => setParams({ ...params, has_ascvd: e.target.checked })}
              />
              <span>Established ASCVD (Prior MI, Stent, Stroke, CAD)</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={!!params.has_heart_failure}
                onChange={e => setParams({ ...params, has_heart_failure: e.target.checked })}
              />
              <span>Diagnosed Heart Failure (HFrEF / HFpEF)</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={!!params.has_ckd}
                onChange={e => setParams({ ...params, has_ckd: e.target.checked })}
              />
              <span>Chronic Kidney Disease (CKD)</span>
            </label>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Current Medications (comma separated)</label>
          <input
            type="text"
            className="form-input"
            value={medInput}
            onChange={e => setMedInput(e.target.value)}
            placeholder="e.g. Metformin 1000mg BID, Lisinopril 20mg"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Physician Clinical Notes</label>
          <textarea
            rows={2}
            className="form-textarea"
            value={params.clinical_notes || ""}
            onChange={e => setParams({ ...params, clinical_notes: e.target.value })}
            placeholder="e.g. Weight loss desired, complaining of orthopnea..."
          />
        </div>

        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? (
            <>
              <div className="spinner" />
              <span>Analyzing against ADA / ACC / KDIGO Guidelines...</span>
            </>
          ) : (
            <>
              <Activity size={18} />
              <span>Run Guideline Decision Support</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};
