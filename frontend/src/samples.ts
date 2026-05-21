/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { AnalysisReport } from './types';

export const SAMPLE_INTERVIEWS: AnalysisReport[] = [
  {
    id: 'sample-frontend',
    timestamp: Date.now() - 3600000 * 2, // 2 hours ago
    candidateName: 'Alex Mercer',
    roleName: 'Senior Frontend Engineer',
    durationSeconds: 154,
    overallScore: 88,
    status: 'report',
    metrics: {
      confidence: 85,
      pacing: 125, // WPM (Perfect level)
      fillerCount: 4, // Very low
      eyeContact: 92, // Solid
      coherence: 90
    },
    behavioralSignals: {
      pacingFeedback: 'Balanced and deliberate. Alex speaks at 125 WPM, allowing technical concepts to settle with the listener while maintaining high engagement.',
      fillerWordsFeedback: 'Exceptional filler word control. Used only 4 filler terms during the response, reflecting high comfort and technical familiarity.',
      eyeContactFeedback: 'Highly steady at 92%. Maintained clean direct lens contact with minor natural cognitive deflections while formulating coding patterns.',
      expressionFeedback: 'Positive and welcoming. Dynamic facial highlights show interest, smiling naturally during collaborative scenarios.'
    },
    executiveSummary: 'Alex demonstrates strong senior-level technical communication. He handles performance-oriented questions with immediate architectural reasoning and provides a thorough breakdown of virtual DOM costs versus React 19 server components.',
    keyStrengths: [
      'Articulates complex runtime layouts with zero hesitation.',
      'Calm communication style with premium micro-pauses.',
      'Demonstrated high awareness of framework overheads.'
    ],
    coachingPriorities: [
      'Incorporate briefly more structured introductory thesis headers before deep-diving into bundle budgets.',
      'Slightly lower pitch variance when concluding technical paragraphs to reinforce authority.'
    ],
    transcript: [
      {
        speaker: 'Interviewer',
        timestamp: '00:05',
        text: 'Alex, how do you approach performance diagnostics and optimization when taking over a large-scale single page application?',
        sentiment: 'neutral'
      },
      {
        speaker: 'Candidate',
        timestamp: '00:18',
        text: 'First, I establish a baseline with real-user monitoring and Core Web Vitals, specifically targeting Interaction to Next Paint. I avoid guessing and dive straight to Chrome DevTools Performance tab to map frame times.',
        sentiment: 'confident'
      },
      {
        speaker: 'Candidate',
        timestamp: '00:38',
        text: 'Um, in many legacy projects, the bottleneck is unnecessary re-renders. We often see high tree density redrawing because context providers trigger child rebuilds globally.',
        sentiment: 'neutral'
      },
      {
        speaker: 'Interviewer',
        timestamp: '01:05',
        text: 'That makes sense. And what strategies do you look to use to prevent that generic context-driven repaint trigger?',
        sentiment: 'neutral'
      },
      {
        speaker: 'Candidate',
        timestamp: '01:12',
        text: 'I prefer to slice state into highly localized context capsules, or utilize modern light-weight signal primitives. Keeping State closer to the leaf nodes yields immediate, massive frame recovery.',
        sentiment: 'confident'
      },
      {
        speaker: 'Candidate',
        timestamp: '01:40',
        text: 'Uh, also chunking bundles using dynamic imports. There is no reason a dashboard user should load settings bundle on first paint.',
        sentiment: 'hesitant'
      },
      {
        speaker: 'Interviewer',
        timestamp: '02:15',
        text: 'Great details. That aligns perfectly with our front-end architecture goals.',
        sentiment: 'positive'
      }
    ],
    emotionDistribution: {
      confident: 0.42,
      neutral: 0.33,
      happy: 0.12,
      surprised: 0.08,
      sad: 0.05
    }
  },
  {
    id: 'sample-pm',
    timestamp: Date.now() - 3600000 * 24, // 1 day ago
    candidateName: 'Sarah Chen',
    roleName: 'Lead Product Manager',
    durationSeconds: 182,
    overallScore: 94,
    status: 'report',
    metrics: {
      confidence: 96,
      pacing: 138, // WPM (High energy)
      fillerCount: 3, 
      eyeContact: 95,
      coherence: 95
    },
    behavioralSignals: {
      pacingFeedback: 'Energetic and inspiring. Speaks at 138 WPM, standard for senior product pitches. Highly professional cadence with superb narrative flow.',
      fillerWordsFeedback: 'Extremely clean. Used almost no fillers ("um" or "like" occurred less than 3 times), demonstrating complete mastery of the roadmap topic.',
      eyeContactFeedback: 'Flawless camera proximity (95%). Addressed the interviewer directly, conveying immense authority and personal warmth.',
      expressionFeedback: 'Open, expressive, and highly professional. Uses hand gestures and confident facial cues to keep stakeholders aligned.'
    },
    executiveSummary: 'Sarah delivered an outstanding response on managing product tradeoffs for generative AI capabilities. She structured her presentation around clear quantitative metrics, immediate engineering constraints, and ethical guardrails.',
    keyStrengths: [
      'Mastered the GTM (Go-To-Market) messaging layout perfectly.',
      'Superb structured response (Framework used: Problem, Metric, Solution).',
      'Extremely high confidence and natural leadership presence.'
    ],
    coachingPriorities: [
      'Provide concrete engineering numbers or dollar estimations to demonstrate deeper budget familiarity.',
      'Practice brief summary recaps at the final tail of multi-part roadmap briefs.'
    ],
    transcript: [
      {
        speaker: 'Interviewer',
        timestamp: '00:02',
        text: 'Sarah, we want to integrate LLMs into our workspace platform. How do you pitch the roadmap priorities while handling latent risks?',
        sentiment: 'neutral'
      },
      {
        speaker: 'Candidate',
        timestamp: '00:12',
        text: 'I prioritize our LLM roadmap by tying AI triggers directly to documented user frustration nodes, rather than simply matching current tech trends. For instance, summarization of multi-tenant threads yields immediate value.',
        sentiment: 'confident'
      },
      {
        speaker: 'Candidate',
        timestamp: '00:41',
        text: 'However, LLMs introduce severe latency. Users expect UI response in under 200 milliseconds, but full inference ranges up to 3 seconds. To balance this tradeoff, we must couple asynchronous generation with stream-styled UX patterns.',
        sentiment: 'confident'
      },
      {
        speaker: 'Interviewer',
        timestamp: '01:21',
        text: 'Interesting. How would you measure success of this stream-styled UI?',
        sentiment: 'neutral'
      },
      {
        speaker: 'Candidate',
        timestamp: '01:29',
        text: 'We track active retention and helpfulness ratings, paired with LLM token overhead costs. If the unit economics don\'t justify the engagement liftoff, we quickly fall back to deterministic parsing filters.',
        sentiment: 'confident'
      },
      {
        speaker: 'Candidate',
        timestamp: '02:35',
        text: 'Ultimately, we want our users to feel assisted, not overwhelmed. We design loops that respect workflow context.',
        sentiment: 'positive'
      }
    ],
    emotionDistribution: {
      confident: 0.48,
      happy: 0.27,
      neutral: 0.18,
      surprised: 0.05,
      sad: 0.02
    }
  },
  {
    id: 'sample-sales',
    timestamp: Date.now() - 3600000 * 48, // 2 days ago
    candidateName: 'Marcus Brody',
    roleName: 'Strategic Sales Lead',
    durationSeconds: 140,
    overallScore: 82,
    status: 'report',
    metrics: {
      confidence: 91,
      pacing: 145, // Sales tempo
      fillerCount: 11, // Slightly higher
      eyeContact: 81, // Looking at documents occasionally
      coherence: 84
    },
    behavioralSignals: {
      pacingFeedback: 'Fast and high-octane. Speaks at 145 WPM, standard for sales prospecting but slightly fast for technical consensus building.',
      fillerWordsFeedback: 'Moderate use of fillers (11 count, frequently of "you know" and "like"). Can be polished for executive reviews.',
      eyeContactFeedback: 'Adequate at 81%. Natural deflections occurred as he scanned physical pitch collateral, which maintains authenticity but lowers visual impact.',
      expressionFeedback: 'Exuberant and highly expressive. Excellent voice inflection levels and energetic smile mechanics.'
    },
    executiveSummary: 'Marcus shows excellent persuasive drive and rapid consensus architecture. He handles enterprise gatekeeper resistance with calm active listening, though pacing can be slightly relaxed to ensure complex contract models land softly.',
    keyStrengths: [
      'Incredibly high charisma and immediate active-listening empathy hooks.',
      'Exceptional resilience when confronted with budget constraints.',
      'Strong storytelling to close value communication loops.'
    ],
    coachingPriorities: [
      'Incorporate brief structural silences to allow value metrics to settle with high-context buyers.',
      'Actively filter habitual filler repetitions (such as "really" or "you know").'
    ],
    transcript: [
      {
        speaker: 'Interviewer',
        timestamp: '00:04',
        text: 'Marcus, how do you navigate procurement security checks when closing half-million-dollar ARR platform commitments?',
        sentiment: 'neutral'
      },
      {
        speaker: 'Candidate',
        timestamp: '00:16',
        text: 'I bring our security architect into the cycle at stage two, rather than waiting for contract signing. You know, gatekeepers aren\'t there to block; they are there to protect corporate safety. If we respect that, we speed up cycles by weeks.',
        sentiment: 'confident'
      },
      {
        speaker: 'Candidate',
        timestamp: '00:43',
        text: 'Like, we deliver a pre-filled SOC2 compliance workbook, addressing trust nodes before they even file their vendor risk spreadsheets.',
        sentiment: 'neutral'
      },
      {
        speaker: 'Candidate',
        timestamp: '01:10',
        text: 'Uh, really, the secret is establishing high rapport. Securing security alignment early turns technical gatekeepers into internal advocates.',
        sentiment: 'neutral'
      },
      {
        speaker: 'Interviewer',
        timestamp: '02:00',
        text: 'Brilliant strategy, Marcus. That removes significant friction.',
        sentiment: 'positive'
      }
    ],
    emotionDistribution: {
      confident: 0.35,
      neutral: 0.30,
      happy: 0.20,
      surprised: 0.10,
      sad: 0.05
    }
  }
];
