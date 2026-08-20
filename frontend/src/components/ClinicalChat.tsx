import React, { useState } from 'react';
import { MessageSquare, Send, Sparkles } from 'lucide-react';

interface Props {
  onQuery: (question: string) => void;
  isLoading: boolean;
}

const SAMPLE_QUESTIONS = [
  "What is the recommended 2nd-line therapy for T2D with CKD (eGFR 35) and prior stroke?",
  "When should SGLT2 inhibitors be held prior to elective surgery according to ADA guidelines?",
  "What are the 4 pillars of GDMT in Heart Failure with Reduced Ejection Fraction (HFrEF)?",
  "Is Pioglitazone safe in a diabetic patient with heart failure?"
];

export const ClinicalChat: React.FC<Props> = ({ onQuery, isLoading }) => {
  const [question, setQuestion] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    onQuery(question);
  };

  return (
    <div className="card">
      <div className="card-title">
        <MessageSquare size={18} color="var(--brand-primary)" />
        <span>Clinical Guideline Query & Literature Verification</span>
      </div>

      <div style={{ marginBottom: "16px" }}>
        <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "#64748b", marginBottom: "6px" }}>
          SAMPLE CLINICAL QUESTIONS:
        </div>
        <div className="presets-container">
          {SAMPLE_QUESTIONS.map((q, idx) => (
            <button
              key={idx}
              type="button"
              className="preset-chip"
              onClick={() => {
                setQuestion(q);
                onQuery(q);
              }}
            >
              <Sparkles size={12} color="var(--brand-primary)" />
              <span>{q}</span>
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Ask any question across ADA, ACC/AHA, or KDIGO Guidelines:</label>
          <textarea
            rows={3}
            className="form-textarea"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="e.g. 62yo female with T2D, eGFR 38, and HFpEF. What are the guideline recommendations for glycemic lowering with mortality reduction?"
            required
          />
        </div>

        <button type="submit" className="btn-primary" disabled={isLoading || !question.trim()}>
          {isLoading ? (
            <>
              <div className="spinner" />
              <span>Searching Weaviate & Synthesizing...</span>
            </>
          ) : (
            <>
              <Send size={16} />
              <span>Submit Clinical Query</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};
