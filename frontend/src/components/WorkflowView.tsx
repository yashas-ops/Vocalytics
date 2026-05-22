import { motion } from 'motion/react';
import { Upload, FileText, LineChart, FileCheck, ArrowRight, Mic, Eye, Activity, Cpu, Database, BarChart3 } from 'lucide-react';

const steps = [
  {
    icon: Upload,
    title: 'Upload',
    desc: 'Upload a recorded mock interview video or record directly from your browser. We accept MP4, WebM, and MOV formats.',
    time: '~30s',
  },
  {
    icon: FileText,
    title: 'Transcribe',
    desc: 'Your audio is transcribed with speaker diarization using Whisper. Every pause, filler word, and turn is captured.',
    time: '~1–3 min',
  },
  {
    icon: LineChart,
    title: 'Analyze',
    desc: 'AI evaluates speaking pace, filler word frequency, eye contact duration, facial expressions, and vocal confidence.',
    time: '~2–4 min',
  },
  {
    icon: FileCheck,
    title: 'Report',
    desc: 'Get a comprehensive dashboard with scores, timelines, emotion heatmaps, and actionable coaching priorities.',
    time: 'Instant',
  },
];

const techStack = [
  {
    icon: Mic,
    name: 'faster-whisper',
    desc: 'Speech-to-text transcription via CTranslate2 — 4x faster than vanilla Whisper on CPU with INT8 quantization.',
  },
  {
    icon: Eye,
    name: 'MediaPipe',
    desc: '468-point face mesh landmark detection for gaze direction and eye contact analysis across video frames.',
  },
  {
    icon: Activity,
    name: 'DeepFace',
    desc: 'Emotion recognition across 7 expressions (happy, sad, neutral, surprise, fear, disgust, anger) using OpenCV detector.',
  },
  {
    icon: Cpu,
    name: 'spaCy',
    desc: 'Industrial-strength NLP for filler word detection and POS tagging with the compact en_core_web_sm model.',
  },
  {
    icon: Database,
    name: 'SQLite',
    desc: 'Zero-config local storage with WAL mode — all interview history persisted without external services.',
  },
  {
    icon: BarChart3,
    name: 'Plotly',
    desc: 'Interactive emotion timelines, confidence breakdowns, and performance charts rendered directly in the dashboard.',
  },
];

export default function WorkflowView({ onNavigate }: { onNavigate: (view: string) => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="w-full max-w-5xl mx-auto mt-16 px-4 pb-16"
    >
      {/* Header */}
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">
          How It{' '}
          <span className="bg-[#B9FF66] text-black px-3 py-1 rounded inline-block">Works</span>
        </h2>
        <p className="text-lg text-slate-400 max-w-xl mx-auto">
          From raw recording to actionable insights in minutes. Every step runs locally on your machine.
        </p>
      </div>

      {/* Pipeline steps */}
      <div className="relative max-w-4xl mx-auto mb-20">
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-[var(--connector-line)] opacity-20 hidden md:block" />

        <div className="space-y-12 md:space-y-16">
          {steps.map((s, i) => (
            <motion.div
              key={s.title}
              initial={{ opacity: 0, x: i % 2 === 0 ? -20 : 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.15 * i, duration: 0.35 }}
              className="relative flex flex-col md:flex-row items-start gap-6 md:gap-8"
            >
              <div className="relative z-10 flex-shrink-0 w-16 h-16 rounded-xl bg-[#B9FF66] border-2 border-[#191A23] flex items-center justify-center shadow-[3px_3px_0px_#191A23]">
                <s.icon className="w-7 h-7 text-black" />
              </div>
              <div className="glass-card-premium flex-1 p-6 md:p-8">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-xs font-mono font-bold text-[#B9FF66]">STEP {(i + 1).toString().padStart(2, '0')}</span>
                  <h3 className="text-xl font-bold">{s.title}</h3>
                  <span className="ml-auto text-xs font-mono font-semibold text-slate-400 bg-slate-800/50 px-2.5 py-1 rounded-md border border-slate-700/50">
                    {s.time}
                  </span>
                </div>
                <p className="text-sm text-slate-400 leading-relaxed">{s.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Tech Stack Section */}
      <div className="text-center mb-10">
        <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#B9FF66]/20 text-[#B9FF66] text-xs font-semibold tracking-wider uppercase mb-4 border border-[#B9FF66]/30">
          <Cpu className="w-3.5 h-3.5" />
          Powering the Pipeline
        </span>
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-3">
          Open-Source{' '}
          <span className="bg-[#B9FF66] text-black px-3 py-1 rounded inline-block">Tech Stack</span>
        </h2>
        <p className="text-base text-slate-400 max-w-xl mx-auto mb-10">
          Every component is free, locally-runnable, and carefully chosen for CPU performance.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
        {techStack.map((t, i) => (
          <motion.div
            key={t.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.06 * i, duration: 0.3 }}
            className="glass-card-premium p-6"
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-lg bg-[#B9FF66] border border-[#191A23] flex items-center justify-center shadow-[2px_2px_0px_#191A23] flex-shrink-0">
                <t.icon className="w-5 h-5 text-black" />
              </div>
              <div>
                <h3 className="text-base font-bold leading-tight">{t.name}</h3>
              </div>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">{t.desc}</p>
          </motion.div>
        ))}
      </div>

      {/* CTA */}
      <div className="text-center">
        <button
          onClick={() => onNavigate('login')}
          className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-[#B9FF66] border-2 border-[#191A23] text-black font-bold text-base hover:bg-[#a8ee55] transition-all shadow-[4px_4px_0px_#191A23] dark:shadow-[4px_4px_0px_#B9FF66]"
        >
          Start Practicing
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  );
}
