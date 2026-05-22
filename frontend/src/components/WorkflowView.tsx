import { motion } from 'motion/react';
import { Upload, FileText, LineChart, FileCheck, ArrowRight } from 'lucide-react';

const steps = [
  {
    icon: Upload,
    title: 'Upload',
    desc: 'Upload a recorded mock interview video or record directly from your browser. We accept MP4, WebM, and MOV formats.',
  },
  {
    icon: FileText,
    title: 'Transcribe',
    desc: 'Your audio is transcribed with speaker diarization using Whisper. Every pause, filler word, and turn is captured.',
  },
  {
    icon: LineChart,
    title: 'Analyze',
    desc: 'AI evaluates speaking pace, filler word frequency, eye contact duration, facial expressions, and vocal confidence.',
  },
  {
    icon: FileCheck,
    title: 'Report',
    desc: 'Get a comprehensive dashboard with scores, timelines, emotion heatmaps, and actionable coaching priorities.',
  },
];

export default function WorkflowView({ onNavigate }: { onNavigate: (view: string) => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="w-full max-w-4xl mx-auto mt-16 px-4 pb-16"
    >
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">
          How It{' '}
          <span className="bg-[#B9FF66] text-black px-3 py-1 rounded inline-block">Works</span>
        </h2>
        <p className="text-lg text-slate-400 max-w-xl mx-auto">
          From raw recording to actionable insights in minutes.
        </p>
      </div>

      <div className="relative">
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
                </div>
                <p className="text-sm text-slate-400 leading-relaxed">{s.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="text-center mt-16">
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
