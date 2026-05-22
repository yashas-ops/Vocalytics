import { motion } from 'motion/react';
import { Mic, Activity, Eye, TrendingUp, Sparkles, ArrowRight } from 'lucide-react';

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

export default function AboutView({ onNavigate }: { onNavigate: (view: string) => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="w-full max-w-5xl mx-auto mt-16 px-4 pb-16"
    >
      <div className="text-center mb-16">
        <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#B9FF66]/20 text-[#B9FF66] text-xs font-semibold tracking-wider uppercase mb-6 border border-[#B9FF66]/30">
          <Sparkles className="w-3.5 h-3.5" />
          Vocalytics Studio
        </span>
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-4">
          AI-Powered{' '}
          <span className="bg-[#B9FF66] text-black px-3 py-1 rounded inline-block">Interview Practice</span>
        </h1>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto">
          Record or upload your mock interviews and get instant, data-driven feedback on your communication skills — all running locally with zero cloud dependencies.
        </p>
      </div>

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
