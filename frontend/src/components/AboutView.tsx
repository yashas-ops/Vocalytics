import { motion } from 'motion/react';
import { Mic, Activity, Eye, TrendingUp, Sparkles, ArrowRight, Globe, Lock, Zap, Target, Shield, Cpu } from 'lucide-react';

const features = [
  {
    icon: Mic,
    title: 'Speech Transcription',
    desc: 'Accurate speech-to-text with speaker diarization. Every word captured and attributed — no detail missed.',
  },
  {
    icon: Activity,
    title: 'Pacing & Filler Words',
    desc: 'Real-time speaking pace analysis and filler word detection (um, uh, like). Know exactly where to tighten your delivery.',
  },
  {
    icon: Eye,
    title: 'Eye Contact & Expressions',
    desc: 'Facial landmark tracking evaluates gaze direction and emotional expressions. See how you present under pressure.',
  },
  {
    icon: TrendingUp,
    title: 'Confidence Scoring',
    desc: 'Multi-dimensional scoring from vocal tone, facial cues, and speech coherence. Track your improvement over time.',
  },
];

const stats = [
  { icon: Globe, value: '100%', label: 'Local Processing' },
  { icon: Lock, value: 'Zero', label: 'Cloud Dependencies' },
  { icon: Zap, value: 'Real-time', label: 'Feedback Loop' },
  { icon: Cpu, value: 'Open Source', label: 'AI Models' },
];

const philosophy = [
  {
    icon: Target,
    title: 'Actionable Insights',
    desc: 'Every metric translates to a concrete coaching takeaway. No vanity numbers — just what helps you improve.',
  },
  {
    icon: Shield,
    title: 'Privacy by Design',
    desc: 'Your recordings and data never leave your machine. All transcription, analysis, and scoring happen locally with zero external API calls.',
  },
  {
    icon: Cpu,
    title: 'Open & Accessible',
    desc: 'Built entirely with open-source models — Whisper, MediaPipe, DeepFace, spaCy. No paid tiers, no usage caps, no lock-in.',
  },
];

export default function AboutView({ onNavigate }: { onNavigate: (view: string) => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="w-full max-w-5xl mx-auto mt-16 px-4 pb-16"
    >
      {/* Header */}
      <div className="text-center mb-16">
        <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#B9FF66]/20 text-[#B9FF66] text-xs font-semibold tracking-wider uppercase mb-6 border border-[#B9FF66]/30">
          <Sparkles className="w-3.5 h-3.5" />
          Vocalytics Studio
        </span>
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-4">
          AI-Powered{' '}
          <span className="bg-[#B9FF66] text-black px-3 py-1 rounded inline-block">Communication Intelligence</span>
        </h1>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto">
          Record or upload any speaking presentation — interviews, pitches, meetings — and get instant, data-driven feedback on your confidence, delivery, and presence. All running locally with zero cloud dependencies.
        </p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-16">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 * i, duration: 0.3 }}
            className="glass-card-premium p-5 md:p-6 text-center"
          >
            <s.icon className="w-5 h-5 text-[#B9FF66] mx-auto mb-2" />
            <div className="text-2xl md:text-3xl font-bold">{s.value}</div>
            <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider mt-1">{s.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Feature cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
        {features.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * i, duration: 0.3 }}
            className="glass-card-premium p-6 md:p-8"
          >
            <div className="w-12 h-12 rounded-xl bg-[#B9FF66] border border-[#191A23] flex items-center justify-center mb-4 shadow-[2px_2px_0px_#191A23]">
              <f.icon className="w-6 h-6 text-black" />
            </div>
            <h3 className="text-xl font-bold mb-2">{f.title}</h3>
            <p className="text-sm text-slate-400 leading-relaxed">{f.desc}</p>
          </motion.div>
        ))}
      </div>

      {/* Philosophy / Why Vocalytics */}
      <div className="text-center mb-10">
        <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#B9FF66]/20 text-[#B9FF66] text-xs font-semibold tracking-wider uppercase mb-4 border border-[#B9FF66]/30">
          <Sparkles className="w-3.5 h-3.5" />
          Our Approach
        </span>
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-3">
          Built for{' '}
          <span className="bg-[#B9FF66] text-black px-3 py-1 rounded inline-block">Real Growth</span>
        </h2>
        <p className="text-base text-slate-400 max-w-xl mx-auto mb-10">
          We believe communication coaching should be private, free, and powered by the best open-source AI.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
        {philosophy.map((p, i) => (
          <motion.div
            key={p.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * i, duration: 0.3 }}
            className="glass-card-premium p-6 md:p-8"
          >
            <div className="w-11 h-11 rounded-lg bg-[#B9FF66] border border-[#191A23] flex items-center justify-center mb-4 shadow-[2px_2px_0px_#191A23]">
              <p.icon className="w-5.5 h-5.5 text-black" />
            </div>
            <h3 className="text-lg font-bold mb-2">{p.title}</h3>
            <p className="text-sm text-slate-400 leading-relaxed">{p.desc}</p>
          </motion.div>
        ))}
      </div>

      {/* CTA */}
      <div className="text-center">
        <button
          onClick={() => onNavigate('login')}
          className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-[#B9FF66] border-2 border-[#191A23] text-black font-bold text-base hover:bg-[#a8ee55] transition-all shadow-[4px_4px_0px_#191A23] dark:shadow-[4px_4px_0px_#B9FF66]"
        >
          Get Started
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  );
}
