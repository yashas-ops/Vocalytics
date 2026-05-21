/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Upload, FileVideo, ChevronRight, AlertCircle, Sparkles, User, Briefcase } from 'lucide-react';

// Background hover-tactility custom-event dispatches
const triggerBgHoverStart = () => {
  window.dispatchEvent(new CustomEvent('action-hover-start'));
};
const triggerBgHoverEnd = () => {
  window.dispatchEvent(new CustomEvent('action-hover-end'));
};

interface UploadViewProps {
  onStartSimulation: (file: File | null, candidateName: string, roleName: string) => void;
  isSimulating: boolean;
  simulationStep: 'upload' | 'transcribe' | 'interpret' | 'report';
  simulationProgress: number;
}



export default function UploadView({
  onStartSimulation,
  isSimulating,
  simulationStep,
  simulationProgress,
}: UploadViewProps) {
  const [dragActive, setDragActive] = useState(false);

  const [candidateName, setCandidateName] = useState('');
  const [roleName, setRoleName] = useState('');
  const [showConfig, setShowConfig] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const [videoFileUrl, setVideoFileUrl] = useState<string>('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Stepper steps configuration
  const steps = [
    { number: '01', label: 'Upload' },
    { number: '02', label: 'Transcribe' },
    { number: '03', label: 'Interpret' },
    { number: '04', label: 'Report' }
  ];

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const processFile = (file: File) => {
    const validTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'audio/mpeg', 'audio/wav', 'audio/mp3'];
    const extension = file.name.split('.').pop()?.toLowerCase();
    const isVideoOrAudio = validTypes.includes(file.type) || ['mp4', 'mov', 'avi', 'mp3', 'wav'].includes(extension || '');

    if (!isVideoOrAudio) {
      setErrorMsg('Unsupported format. Please upload MP4, MOV, AVI, MP3, or WAV.');
      return;
    }

    setErrorMsg('');
    setUploadedFileName(file.name);
    setUploadedFile(file);

    // Create standard React object URL for active media playing
    const localUrl = URL.createObjectURL(file);
    setVideoFileUrl(localUrl);

    setShowConfig(true);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const handleBegin = () => {
    if (!candidateName.trim()) {
      setErrorMsg('Please specify a candidate name.');
      return;
    }
    if (!roleName.trim()) {
      setErrorMsg('Please specify a targeted role.');
      return;
    }

    setErrorMsg('');
    triggerBgHoverEnd();
    onStartSimulation(uploadedFile, candidateName, roleName);
  };

  return (
    <div className="relative z-10 max-w-7xl mx-auto px-4 md:px-8 py-10 lg:py-16 theme-transition">
      {/* Title & Description matching original layout */}
      <div className="mb-12 max-w-3xl">
        <motion.h1 
          initial={{ opacity: 0, y: -15 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl md:text-5xl lg:text-[56px] lg:leading-[1.1] font-bold tracking-tight text-[#191A23] dark:text-white mb-4"
          id="main-uploaded-title"
        >
          Vocalytics<br/>
          <span className="serif-display leading-[1.2]">Studio</span>
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="mt-3 text-base text-slate-600 dark:text-slate-400 leading-relaxed font-light"
        >
          An interactive, high-fidelity speech intelligence dashboard. Navigate verbal dynamics, filler occurrences, and facial metrics.
        </motion.p>
      </div>

      {/* Stepper Timeline Progress Index */}
      <div className="mb-16">
        <div className="relative flex flex-col md:flex-row justify-between items-start md:items-center gap-6 md:gap-0 w-full">
          {/* Background connectors */}
          <div className="absolute top-[18px] left-[25px] right-[25px] hidden md:block h-[2px] bg-[#191A23]/20 dark:bg-white/15 -z-10" />

          {/* Actual progress line */}
          {isSimulating && (
            <div 
              className="absolute top-[18px] left-[25px] hidden md:block h-[2px] bg-[#B9FF66] transition-all duration-300 -z-10"
              style={{
                width: 
                  simulationStep === 'upload' ? '15%' :
                  simulationStep === 'transcribe' ? '48%' :
                  simulationStep === 'interpret' ? '81%' : 'calc(100% - 50px)'
              }}
            />
          )}

          {steps.map((step, idx) => {
            const stepNum = idx + 1;
            let isActive = false;
            let isCompleted = false;

            if (isSimulating) {
              const order = ['upload', 'transcribe', 'interpret', 'report'];
              const currentIdx = order.indexOf(simulationStep);
              if (currentIdx === idx) {
                isActive = true;
              } else if (currentIdx > idx) {
                isCompleted = true;
              }
            } else {
              // Idle state: Step 1 is active
              if (idx === 0) isActive = true;
            }

            return (
              <div key={stepNum} className="flex md:flex-col items-center gap-4 md:gap-2 md:w-32 text-left md:text-center group">
                <div 
                  className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold transition-all duration-350 ${
                    isCompleted 
                      ? 'bg-[#B9FF66] text-black border border-[#191A23] shadow-[2px_2px_0px_#191A23]' 
                      : isActive 
                        ? 'bg-[#B9FF66] text-black ring-2 ring-[#191A23] font-bold scale-115 shadow-[3px_3px_0px_#191A23]' 
                        : 'bg-white dark:bg-slate-900 border border-[#191A23] dark:border-white/20 text-slate-400 dark:text-slate-500 shadow-[1px_1px_0px_rgba(0,0,0,0.1)]'
                  }`}
                >
                  {isCompleted ? '✓' : step.number}
                </div>
                <div className="flex flex-col">
                  <span className={`text-sm font-semibold transition-all duration-300 ${isActive ? 'text-slate-900 dark:text-white' : 'text-slate-400 dark:text-slate-500'}`}>
                    {step.label}
                  </span>
                  <span className="text-[11px] text-slate-500 block md:hidden">
                    {isActive ? '(Active)' : isCompleted ? '(Completed)' : '(Pending)'}
                  </span>
                  {idx === 0 && !isSimulating && (
                    <span className="text-[10px] text-slate-900 dark:text-[#B9FF66] font-mono tracking-widest uppercase mt-0.5 bg-[#B9FF66] dark:bg-transparent px-1.5 py-0.5 rounded text-black dark:text-[#B9FF66] inline-block">
                      (Active)
                    </span>
                  )}
                  {isActive && isSimulating && (
                    <span className="text-[10px] text-[#191A23] dark:text-[#B9FF66] font-mono tracking-widest uppercase mt-0.5 bg-[#B9FF66] dark:bg-transparent px-1.5 py-0.5 rounded text-black dark:text-[#B9FF66] inline-block animate-pulse">
                      ({simulationProgress}%)
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Grid: Frosted Card on Left, Descriptions on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Aspect: Analysis Initiator Column */}
        <div className="lg:col-span-7">
          <AnimatePresence mode="wait">
            {!isSimulating ? (
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -15 }}
                className="glass-card-premium rounded-3xl p-6 md:p-8"
              >
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                  <h2 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-[#B9FF66] fill-[#191A23] dark:fill-white" />
                    Start an entry sequence
                  </h2>


                </div>

                {/* Drag and Drop Zone with action hover hooks */}
                <div
                  onDragEnter={handleDrag}
                  onDragOver={handleDrag}
                  onDragLeave={handleDrag}
                  onDrop={handleDrop}
                  onClick={triggerFileInput}
                  onMouseEnter={triggerBgHoverStart}
                  onMouseLeave={triggerBgHoverEnd}
                  className={`relative border-2 border-dashed rounded-2xl p-8 md:p-12 text-center cursor-pointer transition-all duration-300 ${
                    dragActive 
                      ? 'border-[#B9FF66] bg-[#B9FF66]/10 scale-[0.99]' 
                      : 'border-[#191A23] dark:border-white/30 hover:border-[#B9FF66] dark:hover:border-[#B9FF66] hover:bg-[#B9FF66]/5 dark:hover:bg-white/5'
                  }`}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    accept="video/mp4,video/quicktime,video/x-msvideo,audio/mpeg,audio/wav"
                    onChange={handleFileChange}
                  />

                  <div className="flex flex-col items-center">
                    <div className="w-14 h-14 rounded-2xl bg-slate-100 dark:bg-slate-950 flex items-center justify-center text-slate-400 mb-4 shadow-[2px_2px_0px_#191A23] border border-slate-200 dark:border-white/5 group-hover:scale-110 transition-transform">
                      <Upload className="w-6 h-6 text-[#191A23] dark:text-white" />
                    </div>

                    <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200">
                      {uploadedFileName ? 'Replace Media Sequence' : 'Upload Video or Audio File'}
                    </h3>
                    
                    <p className="mt-2 text-xs md:text-sm text-slate-700 dark:text-slate-305 text-slate-705 dark:text-slate-400 max-w-sm mx-auto leading-relaxed font-medium">
                      Drag & drop or <span className="text-black dark:text-[#B9FF66] font-extrabold hover:underline">browse files</span>. Supported formats: MP4, MOV, AVI, MP3, WAV. Visible face trackers maximize analytical signal feedback.
                    </p>

                    {uploadedFileName && (
                      <div className="mt-4 flex items-center gap-2 bg-[#B9FF66] border-2 border-[#191A23] text-black px-3.5 py-1.5 rounded-xl text-xs font-bold shadow-[2px_2px_0px_rgba(0,0,0,1)]">
                        <FileVideo className="w-3.5 h-3.5" />
                        <span className="truncate max-w-[200px]">{uploadedFileName}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Optional Custom Configuration Form */}
                {showConfig && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="mt-6 border-t border-[#191A23]/20 dark:border-white/10 pt-5 space-y-4"
                  >
                    <h4 className="text-xs font-bold tracking-wider text-slate-400 dark:text-slate-500 uppercase font-mono">
                      Analysis Parameters
                    </h4>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5 flex items-center gap-1.5">
                          <User className="w-3 h-3 text-slate-400 dark:text-slate-500" />
                          Speaker Name
                        </label>
                        <input
                          type="text"
                          value={candidateName}
                          onMouseEnter={triggerBgHoverStart}
                          onMouseLeave={triggerBgHoverEnd}
                          onChange={(e) => setCandidateName(e.target.value)}
                          placeholder="e.g. Alex Mercer"
                          className="w-full px-3 py-2.5 text-sm bg-white dark:bg-slate-900 border-2 border-[#191A23] text-slate-900 dark:text-white rounded-xl focus:outline-none focus:border-[#B9FF66] transition-all"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5 flex items-center gap-1.5">
                          <Briefcase className="w-3 h-3 text-slate-400 dark:text-slate-500" />
                          Context / Scenario
                        </label>
                        <input
                          type="text"
                          value={roleName}
                          onMouseEnter={triggerBgHoverStart}
                          onMouseLeave={triggerBgHoverEnd}
                          onChange={(e) => setRoleName(e.target.value)}
                          placeholder="e.g. Team standup, Product interview"
                          className="w-full px-3 py-2.5 text-sm bg-white dark:bg-slate-900 border-2 border-[#191A23] text-slate-900 dark:text-white rounded-xl focus:outline-none focus:border-[#B9FF66] transition-all"
                        />
                      </div>
                    </div>
                  </motion.div>
                )}

                {errorMsg && (
                  <div className="mt-4 flex items-start gap-2 text-red-500 dark:text-red-400 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-500/25 p-3.5 rounded-xl text-xs">
                    <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                    <span>{errorMsg}</span>
                  </div>
                )}

                {/* Launch Button with action triggers */}
                <div className="mt-7 flex justify-end">
                  <button
                    onClick={handleBegin}
                    onMouseEnter={triggerBgHoverStart}
                    onMouseLeave={triggerBgHoverEnd}
                    disabled={!uploadedFileName}
                    className={`px-8 py-3.5 text-xs font-bold uppercase tracking-widest transition-all duration-300 rounded-xl border ${
                      uploadedFileName 
                        ? 'bg-[#B9FF66] border-[#191A23] text-black hover:bg-[#191A23] hover:text-white dark:hover:bg-white dark:hover:text-black cursor-pointer shadow-[3px_3px_0px_#191A23] dark:shadow-[3px_3px_0px_#B9FF66]' 
                        : 'bg-slate-100 dark:bg-slate-900 border-slate-200 dark:border-white/5 text-slate-350 dark:text-slate-600 cursor-not-allowed'
                    }`}
                  >
                    <span>Initiate Sequence</span>
                    <ChevronRight className="w-3 h-3 inline ml-1.5" />
                  </button>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="simulation"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                className="glass-card-premium rounded-3xl p-8 text-center relative overflow-hidden"
              >
                {/* Simulated Wave Glow backdrops */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-72 h-72 rounded-full bg-[#B9FF66]/10 blur-3xl -z-10 animate-pulse" />

                {/* Dynamic animated title for steps */}
                <div className="mb-8">
                  <span className="text-[11px] font-mono tracking-widest text-black dark:text-[#B9FF66] uppercase bg-[#B9FF66] border border-[#191A23] px-2.5 py-1 rounded-full font-bold">
                    Pipeline Active • {simulationProgress}%
                  </span>
                  
                  <h2 className="text-2xl font-bold text-slate-800 dark:text-white mt-4 capitalize tracking-tight">
                    {simulationStep === 'upload' && 'Encrypting & Staging Media'}
                    {simulationStep === 'transcribe' && 'Decoding Conversational Audio'}
                    {simulationStep === 'interpret' && 'Evaluating Behavioral Signals'}
                    {simulationStep === 'report' && 'Compiling Editorial Report'}
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 max-w-sm mx-auto leading-relaxed font-light">
                    {simulationStep === 'upload' && 'Validating secure data packets and allocating local sandbox memory blocks.'}
                    {simulationStep === 'transcribe' && 'Leveraging acoustic deep language filtering to extract word-level transcripts.'}
                    {simulationStep === 'interpret' && 'Assembling structural micro-expression arrays, pitch metrics, and coherence rating indexes.'}
                    {simulationStep === 'report' && 'Integrating confidence mappings and composing expert editorial coaching recs.'}
                  </p>
                </div>

                {/* Pipeline visualizer animation */}
                <div className="relative w-48 h-48 mx-auto mb-8 flex items-center justify-center">
                  <motion.div 
                    className="absolute inset-0 rounded-full border-2 border-dashed border-[#191A23] dark:border-[#B9FF66]/30"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
                  />
                  
                  {/* Fluctuating Sound Waves (for transcription vibe) */}
                  <div className="flex items-center gap-1.5 justify-center h-16">
                     {Array.from({ length: 9 }).map((_, i) => (
                      <motion.div
                        key={i}
                        className="w-1.5 rounded-full bg-gradient-to-t from-[#191A23] to-[#B9FF66] dark:from-[#B9FF66] dark:to-white"
                        animate={{ 
                          height: [12, Math.floor(Math.random() * 40) + 16, 12]
                        }}
                        transition={{ 
                          duration: 0.5 + (i * 0.08), 
                          repeat: Infinity, 
                          ease: 'easeInOut' 
                        }}
                        style={{ height: '16px' }}
                      />
                    ))}
                  </div>

                  {/* Absolute Center Micro Indicator */}
                  <span className="absolute bottom-4 text-[10px] font-mono text-[#191A23] dark:text-[#B9FF66] uppercase tracking-widest font-extrabold">
                    Analyzing
                  </span>
                </div>

                {/* Concrete progress status bar */}
                <div className="w-full max-w-md mx-auto bg-slate-100 dark:bg-slate-950 h-2 rounded-full overflow-hidden p-[1px] border border-slate-200 dark:border-white/5">
                  <motion.div 
                    className="h-full rounded-full bg-[#B9FF66]"
                    animate={{ width: `${simulationProgress}%` }}
                    transition={{ ease: 'easeOut' }}
                  />
                </div>

                {/* Pipeline checkpoints log */}
                <div className="mt-8 text-left max-w-xs mx-auto space-y-2.5 font-mono text-[11px] text-slate-500">
                  <div className="flex items-center gap-2">
                    <span className="text-[#B9FF66] font-extrabold bg-[#191A23] rounded-full w-4 h-4 flex items-center justify-center text-[9px]">✔</span>
                    <span className="text-slate-700 dark:text-slate-350">Allocated sandbox session</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={simulationProgress > 25 ? "text-[#B9FF66] font-extrabold bg-[#191A23] rounded-full w-4 h-4 flex items-center justify-center text-[9px]" : "text-amber-500 animate-pulse font-extrabold"}>
                      {simulationProgress > 25 ? "✔" : "●"}
                    </span>
                    <span className={simulationProgress > 25 ? "text-slate-700 dark:text-slate-350" : ""}>Acoustic parsing channels opened</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={simulationProgress > 60 ? "text-[#B9FF66] font-extrabold bg-[#191A23] rounded-full w-4 h-4 flex items-center justify-center text-[9px]" : simulationProgress > 25 ? "text-amber-500 animate-pulse font-extrabold" : "text-slate-350 dark:text-slate-655 font-medium"}>
                      {simulationProgress > 60 ? "✔" : simulationProgress > 25 ? "●" : "○"}
                    </span>
                    <span className={simulationProgress > 60 ? "text-slate-700 dark:text-slate-350" : ""}>Calculating syntactic variance & pauses</span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>


        </div>

        {/* Right Aspect: Supporting structural list columns */}
        <div className="lg:col-span-5 space-y-8 lg:pl-6 theme-transition">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-6"
          >
            {/* Aspect 1: Report coverage */}
            <div className="border-l-4 border-[#B9FF66] dark:border-[#B9FF66] pl-4 py-1 bg-slate-50/50 dark:bg-[#191A23] p-3 rounded-r-xl border border-[#191A23] dark:border-white/5">
              <h3 className="text-sm font-extrabold text-[#191A23] dark:text-slate-200 tracking-wider uppercase mb-1">
                Report Coverage
              </h3>
              <p className="text-[11px] text-slate-700 dark:text-slate-350 leading-relaxed uppercase tracking-widest font-mono font-bold">
                Multisensory metrics indexing
              </p>
            </div>

            {/* Aspect 2: Executive summary */}
            <div className="border-l-4 border-[#B9FF66] dark:border-[#B9FF66] pl-4 py-1 bg-slate-50/50 dark:bg-[#191A23] p-3 rounded-r-xl border border-[#191A23] dark:border-white/5">
              <h3 className="text-sm font-extrabold text-[#191A23] dark:text-slate-200 tracking-wider uppercase mb-1">
                Executive Summary
              </h3>
              <p className="text-[11px] text-slate-700 dark:text-slate-350 leading-relaxed uppercase tracking-widest font-mono font-bold">
                Confidence patterns & priority actions
              </p>
            </div>

            {/* Aspect 3: Behavioral signals */}
            <div className="border-l-4 border-[#B9FF66] dark:border-[#B9FF66] pl-4 py-1 bg-slate-50/50 dark:bg-[#191A23] p-3 rounded-r-xl border border-[#191A23] dark:border-white/5">
              <h3 className="text-sm font-extrabold text-[#191A23] dark:text-slate-200 tracking-wider uppercase mb-1">
                Behavioral Signals
              </h3>
              <p className="text-[11px] text-slate-700 dark:text-slate-350 leading-relaxed uppercase tracking-widest font-mono font-bold">
                Pacing logs & fillers statistics
              </p>
            </div>

            {/* Aspect 4: Supporting record */}
            <div className="border-l-4 border-[#B9FF66] dark:border-[#B9FF66] pl-4 py-1 bg-slate-50/50 dark:bg-[#191A23] p-3 rounded-r-xl border border-[#191A23] dark:border-white/5">
              <h3 className="text-sm font-extrabold text-[#191A23] dark:text-slate-200 tracking-wider uppercase mb-1">
                Supporting Record
              </h3>
              <p className="text-[11px] text-slate-700 dark:text-slate-350 leading-relaxed uppercase tracking-widest font-mono font-bold">
                Linear transcripts & history Presets
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
