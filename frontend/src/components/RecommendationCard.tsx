import React from 'react';
import type { MedicationRecommendation } from '../types';
import { Award, BookOpen } from 'lucide-react';

interface Props {
  rec: MedicationRecommendation;
  isFirstLine?: boolean;
}

export const RecommendationCard: React.FC<Props> = ({ rec, isFirstLine = true }) => {
  const isClass1 = rec.evidence_grade.includes("Class I") || rec.evidence_grade.includes("Level A") || rec.evidence_grade.includes("1A");

  return (
    <div className="rec-card" style={{ borderLeft: isFirstLine ? '4px solid #059669' : '4px solid #0284c7' }}>
      <div className="rec-header">
        <div>
          <span className="drug-class-title">{rec.drug_class}</span>
          <div style={{ marginTop: '4px' }}>
            {rec.specific_agents.map((agent, i) => (
              <span key={i} className="agent-pill">{agent}</span>
            ))}
          </div>
        </div>

        <div className={`evidence-badge ${isClass1 ? 'badge-class1' : 'badge-class2'}`}>
          <Award size={13} />
          <span>{rec.evidence_grade}</span>
        </div>
      </div>

      <div className="rec-detail-grid">
        <div className="rec-detail-item">
          <div className="rec-detail-label">CLINICAL RATIONALE & TRIAL BENEFIT:</div>
          <div>{rec.indication_and_rationale}</div>
        </div>

        <div className="rec-detail-item" style={{ borderLeftColor: '#059669' }}>
          <div className="rec-detail-label">RENAL & DOSING RULES:</div>
          <div>{rec.renal_and_dosing_rules}</div>
        </div>

        {rec.warnings_or_contraindications && (
          <div className="rec-detail-item" style={{ borderLeftColor: '#dc2626', background: '#fff1f2' }}>
            <div className="rec-detail-label" style={{ color: '#b91c1c' }}>WARNINGS & MONITORING:</div>
            <div style={{ color: '#991b1b' }}>{rec.warnings_or_contraindications}</div>
          </div>
        )}

        <div style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
          <BookOpen size={13} color="var(--brand-primary)" />
          <span>Source: <strong>{rec.guideline_source}</strong></span>
        </div>
      </div>
    </div>
  );
};
