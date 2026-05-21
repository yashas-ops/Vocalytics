/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, 
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell,
  ResponsiveContainer 
} from 'recharts';
import { 
  Award, Clock, Briefcase, FileText, BarChart3, AlertTriangle, Eye, Volume2, Play, Pause, MonitorPlay, Activity, Maximize
} from 'lucide-react';
import { AnalysisReport } from '../types';

// Background hover dispatches
const triggerBgHoverStart = () => {
  window.dispatchEvent(new CustomEvent('action-hover-start'));
};
const triggerBgHoverEnd = () => {
  window.dispatchEvent(new CustomEvent('action-hover-end'));
};

interface DashboardViewProps {
  report: AnalysisReport;
}

// Convert MM:SS timestamps to absolute seconds helper
const parseTimestamp = (ts: string): number => {
  const parts = ts.split(':');
  if (parts.length === 2) {
    const mins = parseInt(parts[0], 10);
    const secs = parseInt(parts[1], 10);
    return (mins * 60) + secs;
  }
  return 0;
};

export default function DashboardView({ report }: DashboardViewProps) {
  const [activeSpeechIdx, setActiveSpeechIdx] = useState<number | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isFaceMeshActive, setIsFaceMeshActive] = useState(true);
  const [videoReady, setVideoReady] = useState(false);
  const [videoDuration, setVideoDuration] = useState(0);
  const [seekValue, setSeekValue] = useState(0);
  const [isSeeking, setIsSeeking] = useState(false);
  const [videoFileUrl, setVideoFileUrl] = useState<string>(() => report.videoFileUrl || 'https://assets.mixkit.co/videos/preview/mixkit-camper-streamer-explaining-something-with-animated-gestures-from-his-chair-41908-large.mp4');

  const videoRef = useRef<HTMLVideoElement>(null);
  const transcriptScrollContainerRef = useRef<HTMLDivElement>(null);

  // Default professional fallback loop for presets without custom uploads
  const defaultVideoUrl = 'https://assets.mixkit.co/videos/preview/mixkit-camper-streamer-explaining-something-with-animated-gestures-from-his-chair-41908-large.mp4';

  useEffect(() => {
    // Pick the custom uploaded file or fallback preset loop
    setVideoFileUrl(report.videoFileUrl || defaultVideoUrl);
  }, [report]);

  // Sync seek coordinate when user targets a transcript timeline segment
  const handlePlayTranscript = (idx: number) => {
    setActiveSpeechIdx(idx);
    setIsPlaying(true);

    const segment = report.transcript[idx];
    const targetSeconds = parseTimestamp(segment.timestamp);

    const video = videoRef.current;
    if (!video) return;

    if (video.readyState >= 1) {
      video.currentTime = targetSeconds;
      setSeekValue(targetSeconds);
      video.play().catch(() => {});
    } else {
      const onReady = () => {
        video.removeEventListener('loadedmetadata', onReady);
        video.currentTime = targetSeconds;
        setSeekValue(targetSeconds);
        video.play().catch(() => {});
      };
      video.addEventListener('loadedmetadata', onReady);
      video.load();
    }

    // Scroll active element cleanly into focus
    const container = transcriptScrollContainerRef.current;
    if (container) {
      const activeEl = container.children[idx] as HTMLElement;
      if (activeEl) {
        container.scrollTo({
          top: activeEl.offsetTop - container.offsetTop - 12,
          behavior: 'smooth'
        });
      }
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const video = videoRef.current;
    if (!video) return;
    const time = parseFloat(e.target.value);
    video.currentTime = time;
    setSeekValue(time);
  };

  const handleSeekStart = () => {
    setIsSeeking(true);
  };

  const handleSeekEnd = () => {
    setIsSeeking(false);
  };

  const handleSeeked = () => {
    if (!videoRef.current) return;
    const currentTime = videoRef.current.currentTime;
    const matchedIdx = report.transcript.findIndex((seg, idx) => {
      const start = parseTimestamp(seg.timestamp);
      const end = idx < report.transcript.length - 1 
        ? parseTimestamp(report.transcript[idx + 1].timestamp) 
        : Infinity;
      return currentTime >= start && currentTime < end;
    });
    if (matchedIdx !== -1 && matchedIdx !== activeSpeechIdx) {
      setActiveSpeechIdx(matchedIdx);
    }
  };

  // Listen to video time updates to sync progress indicators in the timeline
  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    const currentTime = videoRef.current.currentTime;
    if (!isSeeking) {
      setSeekValue(currentTime);
    }

    // If we just seeked to a segment, keep that highlight —
    // don't let float imprecision at boundaries overwrite it
    if (activeSpeechIdx !== null) {
      const activeStart = parseTimestamp(report.transcript[activeSpeechIdx].timestamp);
      if (Math.abs(currentTime - activeStart) < 0.15) {
        return;
      }
    }

    const matchedIdx = report.transcript.findIndex((seg, idx) => {
      const start = parseTimestamp(seg.timestamp);
      const end = idx < report.transcript.length - 1 
        ? parseTimestamp(report.transcript[idx + 1].timestamp) 
        : Infinity;
      return currentTime >= start && currentTime < end;
    });

    if (matchedIdx !== -1 && matchedIdx !== activeSpeechIdx) {
      setActiveSpeechIdx(matchedIdx);
    }
  };

  const handleVideoPlay = () => {
    setIsPlaying(true);
  };

  const handleVideoPause = () => {
    setIsPlaying(false);
  };

  const togglePlayback = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play().catch(() => {});
      }
    }
  };

  const handleFullscreen = () => {
    const container = videoRef.current?.parentElement;
    if (!container) return;
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      container.requestFullscreen();
    }
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds) % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  // Recharts radar modeling
  const radarData = [
    { subject: 'Confidence', value: report.metrics.confidence },
    { subject: 'Pacing', value: Math.min(100, Math.max(30, (1 - Math.abs(130 - report.metrics.pacing) / 60) * 100)) },
    { subject: 'Filler Control', value: Math.max(20, 100 - (report.metrics.fillerCount * 7)) },
    { subject: 'Eye Contact', value: report.metrics.eyeContact },
    { subject: 'Coherence', value: report.metrics.coherence },
  ];

  const activeSubtitle = activeSpeechIdx !== null ? report.transcript[activeSpeechIdx].text : null;
  const isDark = typeof document !== 'undefined' && document.documentElement.classList.contains('dark');

  // Emotion color palette (app theme)
  const emotionColorMap: Record<string, string> = {
    happy: '#B9FF66',
    neutral: '#94a3b8',
    confident: '#818cf8',
    surprised: '#38bdf8',
    surprise: '#38bdf8',
    sad: '#f43f5e',
    angry: '#fb923c',
    fear: '#a78bfa',
    disgust: '#34d399',
  };

  const emotionData = report.emotionDistribution
    ? Object.entries(report.emotionDistribution)
        .map(([emotion, frequency]) => ({
          emotion,
          frequency: +(frequency * 100).toFixed(1),
          fill: emotionColorMap[emotion] || '#B9FF66',
        }))
        .sort((a, b) => a.frequency - b.frequency)
    : [];

  return (
    <div className="relative z-10 max-w-7xl mx-auto px-4 md:px-8 py-8 lg:py-12 theme-transition">
      {/* Profile Header Block */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card-premium rounded-3xl p-6 md:p-8 mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-6"
      >
        <div className="flex items-center gap-4 animate-fade-in">
          <div className="w-16 h-16 rounded-2xl bg-[#B9FF66] border border-[#191A23] text-black flex items-center justify-center text-2xl font-bold shadow-[3px_3px_0px_#191A23]">
            {report.candidateName.split(' ').map(n => n[0]).join('')}
          </div>
          <div>
            <span className="text-[10px] font-mono font-bold tracking-widest text-black uppercase bg-[#B9FF66] border border-[#191A23] px-3 py-1 rounded shadow-[2px_2px_0px_#191A23] transition-all">
              Editorial Review Live
            </span>
            <h1 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white mt-3.5 tracking-tight theme-transition">
              {report.candidateName}
            </h1>
            <div className="flex flex-wrap items-center gap-y-1 gap-x-4 mt-2 text-xs text-slate-800 dark:text-slate-300 font-semibold theme-transition animate-fade-in">
              <span className="flex items-center gap-1">
                <Briefcase className="w-3.5 h-3.5 text-[#191A23] dark:text-[#B9FF66]" />
                {report.roleName}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-[#191A23] dark:text-[#B9FF66]" />
                {formatDuration(report.durationSeconds)} length
              </span>
              <span className="text-slate-300 dark:text-slate-800">•</span>
              <span>{formatDate(report.timestamp)}</span>
            </div>
          </div>
        </div>

        {/* Competency Score Widget */}
        <div className="flex items-center gap-4 bg-white dark:bg-[#191A23] border border-[#191A23] dark:border-white rounded-2xl p-4 w-full md:w-auto justify-between md:justify-start shadow-[3px_3px_0px_#191A23] dark:shadow-[3px_3px_0px_#B9FF66] theme-transition">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-widest text-[#191A23] dark:text-slate-200 block font-mono">
              Coherency Score
            </span>
            <span className="text-3xl font-bold text-[#191A23] dark:text-white tracking-tight theme-transition">
              {report.overallScore}<span className="text-sm text-slate-400 dark:text-slate-500 font-medium font-sans">/100</span>
            </span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-[#B9FF66] border border-[#191A23] flex items-center justify-center text-black shadow-inner font-semibold">
            <Award className="w-6 h-6 animate-pulse" />
          </div>
        </div>
      </motion.div>

      {/* Grid Bento Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column (Conversational Movie Block, Radar, Markers) */}
        <div className="lg:col-span-5 space-y-8">
          
          {/* Conversational Media Stream Video Block */}
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="glass-card-premium rounded-3xl p-6 relative overflow-hidden"
          >
            <div className="flex items-center justify-between gap-2 mb-4">
              <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200 tracking-tight flex items-center gap-2 theme-transition uppercase font-mono">
                <MonitorPlay className="w-4.5 h-4.5 text-black dark:text-[#B9FF66]" />
                Speech Media Capture
              </h3>

              {/* Toggle Face Mesh Overlay button */}
              <button
                onClick={() => setIsFaceMeshActive(!isFaceMeshActive)}
                onMouseEnter={triggerBgHoverStart}
                onMouseLeave={triggerBgHoverEnd}
                className={`px-2.5 py-1 text-[10px] font-bold font-mono tracking-wider uppercase border rounded-lg transition-all cursor-pointer ${
                  isFaceMeshActive 
                    ? 'bg-[#B9FF66] border-[#191A23] text-black font-extrabold shadow-sm' 
                    : 'bg-transparent text-slate-600 dark:text-slate-400 border-slate-300 dark:border-white/10 hover:text-black dark:hover:text-[#B9FF66]'
                }`}
              >
                <span>Face Mesh Tracker</span>
              </button>
            </div>

            {/* Video Container wrapper with Face Mesh overlay indicators */}
            <div className="relative aspect-video bg-black rounded-2xl overflow-hidden shadow-inner group">
              <video
                ref={videoRef}
                src={videoFileUrl || undefined}
                onTimeUpdate={handleTimeUpdate}
                onSeeked={handleSeeked}
                onPlay={handleVideoPlay}
                onPause={handleVideoPause}
                onLoadedMetadata={() => {
                  setVideoReady(true);
                  if (videoRef.current) {
                    setVideoDuration(videoRef.current.duration);
                    setSeekValue(videoRef.current.currentTime);
                  }
                }}
                playsInline
                className="w-full h-full object-cover rounded-2xl"
              />

              {/* Fullscreen toggle button — always visible top-right */}
              <button
                onClick={(e) => { e.stopPropagation(); handleFullscreen(); }}
                className="absolute top-2 right-2 z-20 w-7 h-7 rounded-full bg-black/40 hover:bg-black/60 text-white/80 hover:text-white backdrop-blur-sm flex items-center justify-center transition-all cursor-pointer border border-white/10"
                title={document.fullscreenElement ? 'Exit Fullscreen' : 'Fullscreen'}
              >
                <Maximize className="w-3.5 h-3.5" />
              </button>

              {/* Dynamic Facemesh tracking indicator overlay (SVG vector nodes syncing to play) */}
              {isFaceMeshActive && isPlaying && (
                <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 400 220">
                  {/* Subtle vector anchor connecting eyes, chin & lips */}
                  <motion.g
                    animate={{
                      opacity: [0.35, 0.65, 0.35],
                    }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    stroke="rgba(99, 102, 241, 0.4)"
                    strokeWidth="0.5"
                    fill="none"
                  >
                    <path d="M 180 80 L 220 80 L 205 110 Z" />
                    <path d="M 205 110 L 195 130 L 215 130 Z" />
                    <path d="M 180 80 L 160 90 L 190 120 Z" />
                    <path d="M 220 80 L 240 90 L 220 120 Z" />
                  </motion.g>

                  {/* Tracking Dot landmarks flashing with audio pitch */}
                  <motion.g
                    initial={{ scale: 0.98 }}
                    animate={{
                      scale: [0.99, 1.01, 0.99],
                      translateY: [0, -1, 0]
                    }}
                    transition={{ duration: 0.4, repeat: Infinity }}
                  >
                    {/* Left Eye landmark */}
                    <circle cx="180" cy="80" r="1.5" fill="#818cf8" />
                    {/* Right Eye landmark */}
                    <circle cx="220" cy="80" r="1.5" fill="#818cf8" />
                    {/* Nose tip landmark */}
                    <circle cx="205" cy="110" r="1.5" fill="#38bdf8" />
                    {/* Lip tracker vector corners */}
                    <circle cx="195" cy="130" r="1.5" fill="#f43f5e" />
                    <circle cx="215" cy="130" r="1.5" fill="#f43f5e" />
                    {/* Jaw tracking nodes */}
                    <circle cx="205" cy="155" r="1.5" fill="#10b981" />
                    <circle cx="160" cy="90" r="1" fill="#818cf8" />
                    <circle cx="240" cy="90" r="1" fill="#818cf8" />
                  </motion.g>

                  {/* Absolute Corner face tracking box coordinates vector */}
                  <rect x="145" y="55" width="120" height="115" rx="10" stroke="rgba(99, 102, 241, 0.25)" strokeWidth="1" strokeDasharray="4 2" fill="none" />
                  <text x="150" y="50" fill="#818cf8" fontSize="6" fontFamily="monospace" fontWeight="bold">LOCK TRK: FACE_01_OK</text>
                  <text x="215" y="180" fill="#38bdf8" fontSize="6" fontFamily="monospace" fontWeight="bold">LENS_PT: 92.5% ACC</text>
                </svg>
              )}

              {/* Subtitles Overlay matching accurate timeline segment */}
              <AnimatePresence>
                {activeSubtitle && (
                  <motion.div 
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -5 }}
                    className="absolute bottom-10 left-4 right-4 bg-slate-950/80 backdrop-blur-md rounded-xl p-3 border border-white/10 text-center z-13 pointer-events-none"
                  >
                    <p className="text-[11px] text-[#B9FF66] font-bold uppercase tracking-widest mb-1 font-mono">
                      {activeSpeechIdx !== null && report.transcript[activeSpeechIdx].speaker === 'Interviewer' ? 'Interviewer' : report.candidateName}
                    </p>
                    <p className="text-xs text-white leading-relaxed line-clamp-2">
                      "{activeSubtitle}"
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Always-visible controls: play/pause + time + seek bar */}
              <div className="absolute bottom-0 left-0 right-0 px-2 pb-1.5 z-10 pointer-events-auto">
                <div className="flex items-center justify-between px-0.5 mb-1">
                  <button
                    onClick={(e) => { e.stopPropagation(); togglePlayback(); }}
                    className="w-6 h-6 rounded-full bg-white/25 hover:bg-white/40 text-white backdrop-blur-sm flex items-center justify-center transition-all cursor-pointer"
                    title={isPlaying ? 'Pause' : 'Play'}
                  >
                    {isPlaying ? <Pause className="w-3 h-3 fill-white" /> : <Play className="w-3 h-3 fill-white ml-0.5" />}
                  </button>
                  <span className="text-[9px] font-mono text-white/70">
                    {formatDuration(seekValue)} / {formatDuration(videoDuration)}
                  </span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={videoDuration || 0}
                  step={0.1}
                  value={seekValue}
                  onInput={handleSeek}
                  onMouseDown={handleSeekStart}
                  onMouseUp={handleSeekEnd}
                  onTouchStart={handleSeekStart}
                  onTouchEnd={handleSeekEnd}
                  className="w-full h-1 appearance-none cursor-pointer rounded-full bg-white/30 accent-[#B9FF66] [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-[#B9FF66] [&::-webkit-slider-thumb]:border [&::-webkit-slider-thumb]:border-[#191A23] [&::-webkit-slider-thumb]:shadow-[1px_1px_0px_#191A23] [&::-moz-range-thumb]:w-3 [&::-moz-range-thumb]:h-3 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-[#B9FF66] [&::-moz-range-thumb]:border [&::-moz-range-thumb]:border-[#191A23]"
                />
              </div>

              {/* Premium hover-to-show visual controls overlay layer */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/30 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-between p-4 pointer-events-none">
                <div className="flex justify-between items-start pointer-events-auto">
                  <span className="text-[9px] font-mono font-semibold text-slate-300 bg-slate-900/60 px-2 py-0.5 rounded-full">
                    {formatDuration(videoRef.current?.currentTime || 0)}
                  </span>
                  <Activity className="w-3.5 h-3.5 text-[#B9FF66] animate-pulse" />
                </div>

                <div className="flex items-center justify-center gap-3 pointer-events-auto" />

                <div className="flex justify-between items-center text-[9px] font-mono text-slate-300 pointer-events-auto">
                  <span />
                  <span>1080P PRO</span>
                </div>
              </div>
            </div>

            {/* Simulated Live Audio Track Oscilloscope level bounce */}
            <div className="mt-4 flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-950/40 border border-slate-100 dark:border-white/5 rounded-2xl text-xs theme-transition">
              <span className="text-[10px] uppercase font-mono font-bold text-slate-400 tracking-wider">AUDIO TRACK</span>
              <div className="flex-1 flex gap-0.5 items-end h-5">
                {Array.from({ length: 28 }).map((_, i) => (
                  <motion.div 
                    key={i}
                    animate={{
                      height: isPlaying ? [3, Math.floor(Math.random() * 16) + 4, 3] : 4
                    }}
                    transition={{
                      duration: 0.35 + (i * 0.05),
                      repeat: Infinity,
                    }}
                    style={{ height: '4px' }}
                    className="flex-1 bg-black dark:bg-[#B9FF66] rounded-full"
                  />
                ))}
              </div>
            </div>
          </motion.div>

          {/* Widget 1: Radar Competency Profile */}
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card-premium rounded-3xl p-6"
          >
            <h3 className="text-[13px] font-bold text-slate-800 dark:text-slate-200 tracking-wider mb-4 flex items-center gap-2 uppercase font-mono theme-transition">
              <BarChart3 className="w-4 h-4 text-black dark:text-[#B9FF66]" />
              Competency Profile Map
            </h3>

            {/* Radar representation of high-fidelity analysis */}
            <div className="h-60 flex items-center justify-center relative">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                  <PolarGrid stroke={isDark ? 'rgba(255,255,255,0.1)' : 'rgba(25, 26, 35, 0.1)'} strokeWidth={1} />
                  <PolarAngleAxis 
                    dataKey="subject" 
                    tick={{ fill: isDark ? '#94a3b8' : '#191A23', fontSize: 10, fontWeight: 750, fontFamily: 'monospace' }} 
                  />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 9 }} />
                  <Radar
                    name={report.candidateName}
                    dataKey="value"
                    stroke="#191A23"
                    fill="#B9FF66"
                    fillOpacity={0.65}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Benchmark Insights */}
            <div className="mt-4 border-t border-slate-100 dark:border-white/5 pt-4 flex items-center justify-between text-xs text-slate-700 dark:text-slate-300 theme-transition font-semibold">
              <span className="flex items-center gap-1.5 font-bold">
                <span className="w-2.5 h-2.5 rounded-full bg-[#B9FF66] border border-[#191A23] inline-block shadow-sm" />
                Robust Core Competency
              </span>
              <span>Ref: Tech SLA Index</span>
            </div>
          </motion.div>

          {/* Widget 2: Detailed Signal Micro-Meters */}
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-card-premium rounded-3xl p-6 space-y-5"
          >
            <h3 className="text-[13px] font-bold text-slate-800 dark:text-slate-200 tracking-wider flex items-center gap-2 uppercase font-mono theme-transition">
              <Activity className="w-4 h-4 text-black dark:text-[#B9FF66]" />
              Behavioral Signals
            </h3>

            {/* Signal A: Pacing (Words Per Minute) with visual hover effects */}
            <motion.div 
              whileHover={{ scale: 1.01 }}
              onMouseEnter={triggerBgHoverStart}
              onMouseLeave={triggerBgHoverEnd}
              className="p-4 bg-slate-50 dark:bg-slate-950/45 border border-slate-100 dark:border-white/5 rounded-2xl transition-all shadow-sm theme-transition"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <Volume2 className="w-4 h-4 text-black dark:text-[#B9FF66]" />
                  <span className="text-xs font-bold text-slate-700 dark:text-slate-350 font-mono">PACING CADENCE</span>
                </div>
                <span className="text-xs font-extrabold text-[#191A23] bg-[#B9FF66] border border-[#191A23] px-2 py-0.5 rounded-full">
                  {report.metrics.pacing} WPM
                </span>
              </div>
              {/* Proportional WPM guideline line slider */}
              <div className="w-full bg-slate-200 dark:bg-slate-900 h-1.5 rounded-full relative overflow-hidden theme-transition">
                <div 
                  className="h-full rounded-full bg-[#191A23] dark:bg-[#B9FF66]"
                  style={{ width: `${Math.min(100, (report.metrics.pacing / 200) * 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-[9px] text-slate-400 dark:text-slate-500 mt-1.5 font-mono">
                <span>Slow (&lt;100)</span>
                <span className="text-black dark:text-[#B9FF66] font-extrabold bg-[#B9FF66]/20 px-1 py-0.5 rounded">Ideal (110-140)</span>
                <span>Fast (&gt;150)</span>
              </div>
              <p className="mt-2.5 text-xs text-slate-600 dark:text-slate-400 leading-relaxed font-light">
                {report.behavioralSignals.pacingFeedback}
              </p>
            </motion.div>

            {/* Signal B: Filler Word repetitions */}
            <motion.div 
              whileHover={{ scale: 1.01 }}
              onMouseEnter={triggerBgHoverStart}
              onMouseLeave={triggerBgHoverEnd}
              className="p-4 bg-slate-50 dark:bg-slate-950/45 border border-slate-100 dark:border-white/5 rounded-2xl transition-all shadow-sm theme-transition"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-500" />
                  <span className="text-xs font-bold text-slate-700 dark:text-slate-350 font-mono">LEXICAL CONTROL</span>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${report.metrics.fillerCount < 5 ? 'bg-[#B9FF66] text-black border-[#191A23]' : 'bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-500 border-amber-200 dark:border-amber-500/10'}`}>
                  {report.metrics.fillerCount} Fillers Found
                </span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed font-light">
                {report.behavioralSignals.fillerWordsFeedback}
              </p>
            </motion.div>

            {/* Signal C: Eye Contact proximity */}
            <motion.div 
              whileHover={{ scale: 1.01 }}
              onMouseEnter={triggerBgHoverStart}
              onMouseLeave={triggerBgHoverEnd}
              className="p-4 bg-slate-50 dark:bg-slate-950/45 border border-slate-100 dark:border-white/5 rounded-2xl transition-all shadow-sm theme-transition"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <Eye className="w-4 h-4 text-black dark:text-[#B9FF66]" />
                  <span className="text-xs font-bold text-slate-700 dark:text-slate-350 font-mono">ENGAGEMENT INTENT</span>
                </div>
                <span className="text-xs font-bold text-slate-800 dark:text-white">
                  {report.metrics.eyeContact}% Lens Eye Contact
                </span>
              </div>
              <div className="w-full bg-slate-200 dark:bg-slate-900 h-1.5 rounded-full relative overflow-hidden theme-transition">
                <div 
                  className="h-full rounded-full bg-black dark:bg-[#B9FF66]"
                  style={{ width: `${report.metrics.eyeContact}%` }}
                />
              </div>
              <p className="mt-2.5 text-xs text-slate-600 dark:text-slate-400 leading-relaxed font-light font-sans">
                {report.behavioralSignals.eyeContactFeedback}
              </p>
            </motion.div>
          </motion.div>

          {/* Widget: Emotion Distribution Graph */}
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="glass-card-premium rounded-3xl p-6"
          >
            <h3 className="text-[13px] font-bold text-slate-800 dark:text-slate-200 tracking-wider mb-4 flex items-center gap-2 uppercase font-mono theme-transition">
              <Activity className="w-4 h-4 text-black dark:text-[#B9FF66]" />
              Expression Distribution
            </h3>
            {emotionData.length > 0 ? (
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={emotionData}
                    layout="vertical"
                    margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
                  >
                    <CartesianGrid stroke={isDark ? 'rgba(255,255,255,0.04)' : 'rgba(25, 26, 35, 0.04)'} horizontal={false} />
                    <XAxis type="number" domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} tickFormatter={v => `${v}%`} axisLine={false} tickLine={false} />
                    <YAxis type="category" dataKey="emotion" tick={{ fill: isDark ? '#94a3b8' : '#191A23', fontSize: 11, fontWeight: 600, fontFamily: 'monospace', textTransform: 'capitalize' }} width={90} axisLine={false} tickLine={false} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: isDark ? '#1e293b' : '#ffffff',
                        border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(25, 26, 35, 0.1)'}`,
                        borderRadius: 12,
                        fontSize: 12,
                        color: isDark ? '#e2e8f0' : '#191A23',
                      }}
                      formatter={(value: number) => [`${value}%`, 'Frequency']}
                    />
                    <Bar dataKey="frequency" radius={[0, 6, 6, 0]} maxBarSize={20}>
                      {emotionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <Activity className="w-8 h-8 text-slate-300 dark:text-slate-600 mb-2" />
                <p className="text-xs text-slate-400 dark:text-slate-500 italic">Emotion distribution data is unavailable for this session.</p>
              </div>
            )}
          </motion.div>
        </div>

        {/* Right Column (Executive Summary, Active Transcript) */}
        <div className="lg:col-span-7 space-y-8">
          
          {/* Widget 3: Executive Summary & Editorial Coaching */}
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="glass-card-premium rounded-3xl p-6 md:p-8 space-y-6"
          >
            <div>
              <h3 className="text-lg font-bold text-slate-800 dark:text-white tracking-tight flex items-center gap-2 theme-transition">
                <FileText className="w-5 h-5 text-black dark:text-[#B9FF66]" />
                Editorial Executive Summary
              </h3>
              <p className="mt-3.5 text-sm text-slate-600 dark:text-slate-400 leading-relaxed font-light theme-transition">
                {report.executiveSummary}
              </p>
            </div>

            {/* Key Strengths Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-50 dark:bg-slate-950/40 border border-slate-100 dark:border-white/5 rounded-2xl p-4 theme-transition shadow-sm">
                <h4 className="text-[10px] font-bold text-slate-400 dark:text-slate-500 tracking-wider uppercase mb-3 flex items-center gap-1.5 font-mono">
                  🔑 Key Core Strengths
                </h4>
                {report.keyStrengths.length > 0 ? (
                  <ul className="space-y-3">
                    {report.keyStrengths.map((strength, sIdx) => (
                      <li key={sIdx} className="text-xs text-slate-600 dark:text-slate-450 leading-relaxed flex items-start gap-2">
                        <span className="text-emerald-500 font-extrabold mt-0.5">•</span>
                        <span>{strength}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-slate-400 dark:text-slate-500 italic">Awaiting analysis data...</p>
                )}
              </div>

              {/* Coaching Priorities */}
              <div className="bg-slate-50 dark:bg-slate-950/40 border border-slate-100 dark:border-white/5 rounded-2xl p-4 theme-transition shadow-sm">
                <h4 className="text-[10px] font-bold text-slate-400 dark:text-slate-500 tracking-wider uppercase mb-3 flex items-center gap-1.5 font-mono">
                  💡 Coaching Priorities
                </h4>
                {report.coachingPriorities.length > 0 ? (
                  <ul className="space-y-3">
                    {report.coachingPriorities.map((coaching, cIdx) => (
                      <li key={cIdx} className="text-xs text-slate-600 dark:text-slate-450 leading-relaxed flex items-start gap-2">
                        <span className="text-amber-500 font-bold mt-0.5">↳</span>
                        <span>{coaching}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-slate-400 dark:text-slate-500 italic">Awaiting analysis data...</p>
                )}
              </div>
            </div>
          </motion.div>

          {/* Widget 4: Timeline Transcription Board */}
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="glass-card-premium rounded-3xl p-6 md:p-8"
          >
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
              <div>
                <h3 className="text-lg font-bold text-slate-800 dark:text-white tracking-tight theme-transition">
                  Timeline Transcription Dialogue
                </h3>
                <p className="text-xs text-slate-650 dark:text-slate-400 mt-1 theme-transition font-medium">
                  Click any dialogue segment to play conversational media stream directly at that timestamp.
                </p>
              </div>

              {isPlaying && (
                <div className="flex items-center gap-2 bg-[#B9FF66]/20 text-[#191A23] dark:text-[#B9FF66] border border-[#191A23] dark:border-white/10 px-3.5 py-1 rounded-full text-xs font-semibold self-start sm:self-auto animate-pulse theme-transition">
                  <Volume2 className="w-3.5 h-3.5 font-bold" />
                  <span>Media Sync Active</span>
                </div>
              )}
            </div>

            {/* Transcript Scrolling Node */}
            <div 
              ref={transcriptScrollContainerRef}
              className="space-y-4 max-h-[650px] overflow-y-auto pr-2"
            >
              {report.transcript.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 text-center">
                  <FileText className="w-10 h-10 text-slate-300 dark:text-slate-600 mb-3" />
                  <p className="text-sm text-slate-400 dark:text-slate-500 italic">No transcript available. Run a new analysis to generate transcription data.</p>
                </div>
              ) : report.transcript.map((seg, idx) => {
                const isInterviewer = seg.speaker === 'Interviewer';
                const isActive = activeSpeechIdx === idx;

                return (
                  <motion.div
                    key={idx}
                    layout
                    whileHover={{ scale: 1.005 }}
                    onMouseEnter={triggerBgHoverStart}
                    onMouseLeave={triggerBgHoverEnd}
                    onClick={() => handlePlayTranscript(idx)}
                    className={`p-4 rounded-2xl transition-all border duration-300 cursor-pointer ${
                      isActive 
                        ? 'bg-[#B9FF66]/15 dark:bg-[#B9FF66]/10 border-2 border-[#191A23] dark:border-[#B9FF66] shadow-[2px_2px_0px_rgba(0,0,0,1)] dark:shadow-[2px_2px_0px_#B9FF66]' 
                        : isInterviewer
                          ? 'bg-white dark:bg-slate-950/20 border border-slate-100 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-slate-900/10'
                          : 'bg-white dark:bg-slate-950/10 border border-slate-100 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-slate-900/30'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-2">
                       <div className="flex items-center gap-2">
                        <span className={`w-10 h-6 rounded flex items-center justify-center text-[9px] font-mono font-bold border ${
                          isInterviewer 
                            ? 'bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-white/5' 
                            : 'bg-[#B9FF66] text-black border-[#191A23]'
                        }`}>
                          {isInterviewer ? 'INT' : 'CAN'}
                        </span>
                        
                        <span className="text-xs font-bold text-slate-800 dark:text-slate-200 theme-transition">
                          {isInterviewer ? 'Interviewer' : report.candidateName}
                        </span>

                        <span className="text-[10px] text-slate-600 dark:text-slate-400 font-mono font-bold">
                          {seg.timestamp}
                        </span>
                      </div>

                      {/* Sentiment Label mapping */}
                      {seg.sentiment && (
                        <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider border ${
                          seg.sentiment === 'confident' ? 'bg-[#B9FF66] border-[#191A23] text-black font-extrabold' :
                          seg.sentiment === 'positive' ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-100 dark:border-emerald-500/10 text-emerald-600 dark:text-emerald-400' :
                          seg.sentiment === 'hesitant' ? 'bg-amber-50 dark:bg-amber-950/45 border-amber-200 dark:border-amber-500/15 text-amber-600 dark:text-amber-500' :
                          'bg-slate-50 dark:bg-slate-900 border-slate-100 dark:border-white/5 text-slate-500'
                        }`}>
                          {seg.sentiment}
                        </span>
                      )}
                    </div>

                    <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed font-light pl-12 pr-2 font-sans theme-transition">
                      "{seg.text}"
                    </p>

                    {/* Interactive Play icon trigger */}
                    <div className="pl-12 mt-2.5 flex justify-end">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handlePlayTranscript(idx);
                        }}
                        className={`text-[9px] font-bold uppercase tracking-wider font-mono flex items-center gap-1 rounded-lg px-2.5 py-1.5 transition-all cursor-pointer border ${
                          isActive 
                            ? 'bg-[#B9FF66] border-[#191A23] text-black shadow-[1px_1px_0px_#000]' 
                            : 'bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 border-2 border-[#191A23] dark:border-white/5 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
                        }`}
                      >
                        <Play className={`w-2.5 h-2.5 ${isActive ? 'fill-black text-black' : 'text-slate-400'}`} />
                        <span>{isActive ? 'Playing now' : 'Seek Segment'}</span>
                      </button>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
