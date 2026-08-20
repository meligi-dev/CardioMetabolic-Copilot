import React from 'react';
import type { GuidelineCitation } from '../types';
import { BookOpen } from 'lucide-react';

interface Props {
  citations: GuidelineCitation[];
}

export const SourceViewer: React.FC<Props> = ({ citations }) => {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="card" style={{ marginTop: '16px' }}>
      <div className="card-title">
        <BookOpen size={18} color="var(--brand-primary)" />
        <span>Verified Guideline Citations ({citations.length})</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {citations.map((cite, i) => (
          <div key={i} className="citation-box">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="citation-header">
                {cite.guideline} — {cite.chapter_or_section}
              </div>
              {cite.evidence_level && (
                <span className="evidence-badge badge-class1" style={{ fontSize: '0.7rem' }}>
                  {cite.evidence_level}
                </span>
              )}
            </div>

            {cite.recommendation_id && (
              <div style={{ fontWeight: 600, fontSize: '0.78rem', color: '#34d399', marginBottom: '4px' }}>
                {cite.recommendation_id}
              </div>
            )}

            <div className="citation-snippet">
              "{cite.snippet}"
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
