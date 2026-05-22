import { motion } from 'motion/react';
import { Mic, Briefcase, Eye, Camera, MessageCircle, Activity, GraduationCap, Sparkles, ArrowRight } from 'lucide-react';

const useCases = [
  {
    icon: Mic,
    title: 'Public Speaking Training',
    desc: 'Practice speeches and presentations with AI-powered feedback on confidence, clarity, pacing, and delivery.',
  },
  {
    icon: Briefcase,
    title: 'Mock Interviews',
    desc: 'Simulate realistic interview conversations and improve communication, response quality, and speaking confidence.',
  },
  {
    icon: Eye,
    title: 'Expression Control & Body Language',
    desc: 'Analyze facial expressions, eye contact, and on-camera presence to enhance communication impact.',
  },
  {
    icon: Camera,
    title: 'Content Creator Coaching',
    desc: 'Improve storytelling, speaking style, audience engagement, and camera confidence for videos and podcasts.',
  },
  {
    icon: MessageCircle,
    title: 'Communication Skill Development',
    desc: 'Strengthen articulation, fluency, tone, and conversational ability through interactive AI practice.',
  },
  {
    icon: Activity,
    title: 'Real-Time Speech Analysis',
    desc: 'Receive insights on filler words, speaking pace, emotional tone, confidence, and overall communication effectiveness.',
  },
  {
    icon: GraduationCap,
    title: 'Student & Career Preparation',
    desc: 'Prepare for presentations, viva sessions, group discussions, and professional interactions with personalized feedback.',
  },
];

export default function UseCasesView({ onNavigate }: { onNavigate: (view: string) => void }) {
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
          Real-World Applications
        </span>
        <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">
          Use{' '}
          <span className="bg-[#B9FF66] text-black px-3 py-1 rounded inline-block">Cases</span>
        </h2>
        <p className="text-lg text-slate-400 max-w-xl mx-auto">
          From public speaking to interview prep — see how Vocalytics adapts to your communication goals.
        </p>
      </div>

      {/* Use case cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
        {useCases.map((uc, i) => (
          <motion.div
            key={uc.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.06 * i, duration: 0.3 }}
            className={`glass-card-premium p-6 md:p-8 ${i === useCases.length - 1 ? 'md:col-span-3 md:max-w-md md:mx-auto' : ''}`}
          >
            <div className="w-12 h-12 rounded-xl bg-[#B9FF66] border border-[#191A23] flex items-center justify-center mb-4 shadow-[2px_2px_0px_#191A23]">
              <uc.icon className="w-6 h-6 text-black" />
            </div>
            <h3 className="text-xl font-bold mb-2">{uc.title}</h3>
            <p className="text-sm text-slate-400 leading-relaxed">{uc.desc}</p>
          </motion.div>
        ))}
      </div>

      {/* CTA */}
      <div className="text-center">
        <button
          onClick={() => onNavigate('login')}
          className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-[#B9FF66] border-2 border-[#191A23] text-black font-bold text-base hover:bg-[#a8ee55] transition-all shadow-[4px_4px_0px_#191A23] dark:shadow-[4px_4px_0px_#B9FF66]"
        >
          Start Your Practice
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  );
}
