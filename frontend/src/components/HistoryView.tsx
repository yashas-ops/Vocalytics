/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Search, Trash2, ExternalLink, Calendar, Award, Briefcase, Clock, RefreshCcw, UserPlus, FileVideo } from 'lucide-react';
import { AnalysisReport } from '../types';

// Background hover dispatches
const triggerBgHoverStart = () => {
  window.dispatchEvent(new CustomEvent('action-hover-start'));
};
const triggerBgHoverEnd = () => {
  window.dispatchEvent(new CustomEvent('action-hover-end'));
};

interface HistoryViewProps {
  historyItems: AnalysisReport[];
  onLoadReport: (report: AnalysisReport) => void;
  onDeleteReport: (id: string) => void;
  onRestorePresets: () => void;
}

export default function HistoryView({
  historyItems,
  onLoadReport,
  onDeleteReport,
  onRestorePresets,
}: HistoryViewProps) {
  const [searchTerm, setSearchTerm] = useState('');

  // Filtering items by name or role matching search criteria
  const filteredItems = historyItems.filter(item => 
    item.candidateName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.roleName.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds) % 60;
    return `${mins}m ${secs < 10 ? '0' : ''}${secs}s`;
  };

  return (
    <div className="relative z-10 max-w-7xl mx-auto px-4 md:px-8 py-10 lg:py-14 theme-transition">
      {/* Search Header and Actions block */}
      <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-800 dark:text-white mt-4 capitalize tracking-tight font-sans">
            ARCHIVED<br />
            <span className="serif-display">Analysis history logs</span>
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1.5 font-light theme-transition">
            Review past compiled reports, verified speech scores, and coaching benchmarks.
          </p>
        </div>

        {/* Restore default logs actions in case the user deletes everything */}
        <button
          onClick={() => {
            triggerBgHoverEnd();
            onRestorePresets();
          }}
          onMouseEnter={triggerBgHoverStart}
          onMouseLeave={triggerBgHoverEnd}
          className="px-4.5 py-2.5 text-xs font-bold text-black bg-[#B9FF66] border-2 border-[#191A23] hover:bg-[#191A23] hover:text-white rounded-xl transition-all flex items-center gap-2 self-start md:self-auto cursor-pointer shadow-[3px_3px_0px_#191A23]"
        >
          <RefreshCcw className="w-3.5 h-3.5" />
          <span>Restore Sample Reports</span>
        </button>
      </div>

      {/* Global Interactive Search Input */}
      <div className="mb-8 relative max-w-md">
        <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 dark:text-slate-500">
          <Search className="w-4 h-4" />
        </span>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onMouseEnter={triggerBgHoverStart}
          onMouseLeave={triggerBgHoverEnd}
          placeholder="Search by candidate name or targeted role..."
          className="w-full pl-10 pr-4 py-2.5 bg-white dark:bg-slate-900 border-2 border-[#191A23] rounded-xl text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-[#B9FF66] transition-all"
        />
      </div>

      {/* Main logs display */}
      <AnimatePresence mode="wait">
        {filteredItems.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            className="glass-card-premium rounded-3xl p-12 text-center max-w-md mx-auto"
          >
            <div className="w-12 h-12 rounded-2xl bg-slate-50 dark:bg-slate-950 flex items-center justify-center text-slate-400 mx-auto mb-4 border border-slate-200 dark:border-white/5 shadow-sm">
              <Search className="w-5 h-5 text-black dark:text-[#B9FF66]" />
            </div>
            <h3 className="text-base font-bold text-slate-800 dark:text-slate-200 tracking-tight">
              No matching records found
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 max-w-xs mx-auto leading-relaxed">
              Please refine your search criteria or restore sample mock templates.
            </p>
            <button
              onClick={() => {
                triggerBgHoverEnd();
                onRestorePresets();
              }}
              onMouseEnter={triggerBgHoverStart}
              onMouseLeave={triggerBgHoverEnd}
              className="mt-5 px-5 py-2.5 text-xs font-bold uppercase tracking-wider text-black bg-[#B9FF66] border border-[#191A23] hover:bg-[#191A23] hover:text-white rounded-xl transition-all inline-flex items-center gap-1.5 cursor-pointer shadow-[2px_2px_0px_#191A23]"
            >
              <UserPlus className="w-3.5 h-3.5" />
              <span>Restore Samples</span>
            </button>
          </motion.div>
        ) : (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {filteredItems.map((item) => (
              <motion.div
                key={item.id}
                layout
                whileHover={{ scale: 1.015, y: -2 }}
                onMouseEnter={triggerBgHoverStart}
                onMouseLeave={triggerBgHoverEnd}
                className="glass-card-premium rounded-3xl p-6 flex flex-col justify-between relative group overflow-hidden transition-all duration-300 border-2 border-transparent hover:border-[#191A23] dark:hover:border-[#B9FF66]"
              >
                {/* Visual score accent circle decoration */}
                <div className="absolute -top-6 -right-6 w-24 h-24 bg-[#B9FF66]/10 rounded-full blur-xl group-hover:bg-[#B9FF66]/25 transition-all duration-300 pointer-events-none" />

                <div>
                   <div className="flex items-start justify-between gap-2 mb-4">
                    <span className="text-[10px] font-mono font-bold text-black dark:text-[#B9FF66] bg-[#B9FF66]/20 border border-[#191A23] dark:border-[#B9FF66] px-2.5 py-1 rounded-xl flex items-center gap-1 shadow-sm font-semibold">
                      <Calendar className="w-2.5 h-2.5" />
                      {formatDate(item.timestamp)}
                    </span>

                    {/* overall rating widget */}
                    <div className="flex items-center gap-1 bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-white/10 px-2.5 py-1 rounded-xl text-[#191A23] dark:text-[#B9FF66] font-bold text-xs shadow-sm font-mono text-xs">
                      <Award className="w-3.5 h-3.5 text-[#B9FF66] fill-[#B9FF66]" />
                      <span>{item.overallScore}%</span>
                    </div>
                  </div>

                  <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200 group-hover:text-black dark:group-hover:text-[#B9FF66] transition-colors">
                    {item.candidateName}
                  </h3>

                  <div className="mt-4 space-y-2.5 text-xs text-slate-700 dark:text-slate-300">
                    <div className="flex items-center gap-1.5 font-medium">
                      <Briefcase className="w-3.5 h-3.5 text-black dark:text-[#B9FF66] shrink-0" />
                      <span className="truncate font-semibold">{item.roleName}</span>
                    </div>

                    <div className="flex items-center gap-1.5 font-medium">
                      <Clock className="w-3.5 h-3.5 text-black dark:text-[#B9FF66] shrink-0" />
                      <span>Duration: {formatDuration(item.durationSeconds)}</span>
                    </div>
                    
                    <div className="flex items-center gap-1.5 font-medium">
                      <FileVideo className="w-3.5 h-3.5 text-black dark:text-[#B9FF66] shrink-0" />
                      <span>{item.metrics.pacing} WPM • {item.metrics.fillerCount} Fillers</span>
                    </div>
                  </div>
                </div>

                {/* Card Action Controls */}
                <div className="mt-6 pt-4 border-t border-slate-100 dark:border-white/5 flex items-center justify-between">
                  <button
                    onClick={() => onDeleteReport(item.id)}
                    className="text-slate-655 text-slate-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400 p-2 rounded-xl hover:bg-red-50 dark:hover:bg-red-950/20 transition-all text-xs font-bold flex items-center gap-1 cursor-pointer"
                    title="Delete record from log"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Delete</span>
                  </button>

                  <button
                    onClick={() => {
                      triggerBgHoverEnd();
                      onLoadReport(item);
                    }}
                    className="px-4 py-2 bg-black dark:bg-[#B9FF66] text-white dark:text-black hover:bg-slate-800 dark:hover:bg-white rounded-xl text-xs font-bold uppercase tracking-wider transition-all cursor-pointer border border-black shadow-[2px_2px_0px_#191A23] dark:shadow-[2px_2px_0px_#fff]"
                  >
                    <span>Load Review</span>
                    <ExternalLink className="w-3.5 h-3.5 inline ml-1.5" />
                  </button>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
