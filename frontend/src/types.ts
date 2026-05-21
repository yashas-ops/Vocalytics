/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export interface TranscriptSegment {
  speaker: 'Interviewer' | 'Candidate';
  timestamp: string;
  text: string;
  sentiment?: 'positive' | 'neutral' | 'confident' | 'hesitant';
}

export interface MetricBreakdown {
  confidence: number; // 0-100
  pacing: number; // Words per minute
  fillerCount: number; // Standard um/uh indicators
  eyeContact: number; // 0-100 %
  coherence: number; // 0-100 %
}

export interface BehavioralSignals {
  pacingFeedback: string;
  fillerWordsFeedback: string;
  eyeContactFeedback: string;
  expressionFeedback: string;
}

export interface AnalysisReport {
  id: string;
  timestamp: number; // ms since epoch
  candidateName: string;
  roleName: string;
  durationSeconds: number;
  overallScore: number; // 0-100
  status: 'upload' | 'transcribe' | 'interpret' | 'report';
  metrics: MetricBreakdown;
  behavioralSignals: BehavioralSignals;
  executiveSummary: string;
  keyStrengths: string[];
  coachingPriorities: string[];
  transcript: TranscriptSegment[];
  videoFileUrl?: string;
  emotionDistribution?: Record<string, number>;
}
