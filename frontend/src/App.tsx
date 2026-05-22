import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Upload, BarChart3, History, Wand2, LogOut, Eye, EyeOff, Info } from 'lucide-react';

import ThreeDBackground from './components/ThreeDBackground';
import UploadView from './components/UploadView';
import DashboardView from './components/DashboardView';
import HistoryView from './components/HistoryView';
import AboutView from './components/AboutView';
import WorkflowView from './components/WorkflowView';
import UseCasesView from './components/UseCasesView';

import { AnalysisReport } from './types';
import { SAMPLE_INTERVIEWS } from './samples';

const STORAGE_KEY = 'ctracker_history_v1';
const AUTH_KEY = 'ctracker_user_v1';

const triggerBgHoverStart = () => {
  window.dispatchEvent(new CustomEvent('action-hover-start'));
};
const triggerBgHoverEnd = () => {
  window.dispatchEvent(new CustomEvent('action-hover-end'));
};

const API_BASE = '/api';

export default function App() {
  const [user, setUser] = useState<{user_id: number; username: string} | null>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem(AUTH_KEY);
      return saved ? JSON.parse(saved) : null;
    }
    return null;
  });
  const [activeView, setActiveView] = useState<'upload' | 'dashboard' | 'history' | 'login' | 'register' | 'about' | 'workflow' | 'usecases'>(user ? 'upload' : 'about');
  const [authLoading, setAuthLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [activeReport, setActiveReport] = useState<AnalysisReport | null>(null);
  const [historyItems, setHistoryItems] = useState<AnalysisReport[]>([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationStep, setSimulationStep] = useState<'upload' | 'transcribe' | 'interpret' | 'report'>('upload');
  const [simulationProgress, setSimulationProgress] = useState(0);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        const mapped = parsed.map(mapHistoryItem);
        setHistoryItems(mapped);
      } catch {
        setHistoryItems([]);
      }
    } else {
      const loadFromApi = async () => {
        try {
          const savedUser = localStorage.getItem(AUTH_KEY);
          const uid = savedUser ? JSON.parse(savedUser).user_id : 0;
          const res = await fetch(`${API_BASE}/history?user_id=${uid}`);
          const data = await res.json() as any[];
          if (data && data.length > 0) {
            const mapped = data.map(mapHistoryItem);
            setHistoryItems(mapped);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(mapped));
          }
        } catch {}
      };
      loadFromApi();
    }
  }, []);

  const syncHistory = (newItems: AnalysisReport[]) => {
    setHistoryItems(newItems);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newItems));
  };

  // Poll backend for job status
  useEffect(() => {
    let timer: ReturnType<typeof setInterval>;
    if (isSimulating) {
      timer = setInterval(async () => {
        const jobId = sessionStorage.getItem('current_job_id');
        if (!jobId) return;
        try {
          const res = await fetch(`${API_BASE}/status/${jobId}`);
          const data = await res.json();

          const stepMap: Record<string, 'upload' | 'transcribe' | 'interpret' | 'report'> = {
            'pending': 'upload',
            'processing': 'transcribe',
            'completed': 'report',
            'failed': 'report',
          };
          const step = data.status === 'processing'
            ? (data.progress > 50 ? 'interpret' : 'transcribe')
            : (stepMap[data.status] || 'upload');

          setSimulationStep(step);

          if (typeof data.progress === 'number') {
            // Map 0-100 to our step-based progress
            setSimulationProgress(data.progress);
          }

          if (data.status === 'completed' && data.result) {
            clearInterval(timer);
            setIsSimulating(false);

            const report = data.result as AnalysisReport;
            const updated = [report, ...historyItems.filter(h => h.id !== report.id)];
            syncHistory(updated);
            setActiveReport(report);
            setActiveView('dashboard');
            sessionStorage.removeItem('current_job_id');
          } else if (data.status === 'failed') {
            clearInterval(timer);
            setIsSimulating(false);
            console.error('Pipeline failed:', data.error);
            sessionStorage.removeItem('current_job_id');
          }
        } catch (e) {
          console.error('Polling error', e);
        }
      }, 1500);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isSimulating, historyItems]);

  const handleStartSimulation = async (
    file: File | null,
    candidateName: string,
    roleName: string,
  ) => {
    if (!file) {
      console.warn('No file uploaded — cannot run pipeline without a recording');
      return;
    }

    setSimulationStep('upload');
    setSimulationProgress(0);
    setIsSimulating(true);
    setActiveView('upload');

    const formData = new FormData();
    formData.append('video', file);
    formData.append('candidateName', candidateName);
    formData.append('roleName', roleName);
    if (user) formData.append('userId', String(user.user_id));

    try {
      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errText = await response.text();
        console.error('Upload failed:', errText);
        setIsSimulating(false);
        return;
      }
      const data = await response.json();
      const jobId = data.jobId;
      sessionStorage.setItem('current_job_id', jobId);
    } catch (err) {
      console.error('Failed to start analysis job', err);
      setIsSimulating(false);
    }
  };

  const handleDeleteReport = (id: string) => {
    const updated = historyItems.filter(item => item.id !== id);
    syncHistory(updated);
    if (activeReport?.id === id) {
      setActiveReport(updated[0] || null);
    }
  };

  const handleRestorePresets = () => {
    syncHistory(SAMPLE_INTERVIEWS);
    setActiveView('history');
  };

  const handleLoadReport = async (report: AnalysisReport) => {
    if (report.id.startsWith('sample-')) {
      setActiveReport(report);
      setActiveView('dashboard');
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/interview/${report.id}`);
      if (res.ok) {
        const data = await res.json();
        const mapped = mapHistoryItem(data);
        setActiveReport(mapped);
      } else {
        setActiveReport(report);
      }
    } catch {
      setActiveReport(report);
    }
    setActiveView('dashboard');
  };

  return (
    <div className="min-h-screen relative overflow-hidden font-sans flex flex-col justify-between dark text-white">
      <ThreeDBackground />

      <div className="flex-1 flex flex-col relative z-10 theme-transition">

        <header className="w-full border-b border-slate-200/50 dark:border-white/5 bg-white/40 dark:bg-slate-950/40 backdrop-blur-md sticky top-0 z-50 theme-transition">
          <div className="max-w-7xl mx-auto px-4 md:px-8 py-4 flex items-center justify-between">

            <div
              onClick={() => { if (!isSimulating) { user ? setActiveView('upload') : setActiveView('about'); } }}
              onMouseEnter={triggerBgHoverStart}
              onMouseLeave={triggerBgHoverEnd}
              className="flex items-center gap-2 cursor-pointer group"
            >
              <div className="w-10 h-10 rounded-xl bg-[#B9FF66] border border-[#191A23] flex items-center justify-center text-black shadow-[2px_2px_0px_#191A23] group-hover:rotate-6 transition-transform">
                <Wand2 className="w-5.5 h-5.5 fill-black text-black" />
              </div>
              <span className="font-bold tracking-wide text-slate-930 dark:text-white text-xl md:text-2xl transition-colors duration-300">
                Vocal<span className="bg-[#B9FF66] text-black font-semibold px-1.5 rounded border border-black inline-block">ytics</span>
              </span>
            </div>

            <div className="flex items-center gap-2 sm:gap-6">
              {!user && (
                <nav className="flex items-center gap-1 sm:gap-4">
                  <button
                    onClick={() => setActiveView('about')}
                    onMouseEnter={triggerBgHoverStart}
                    onMouseLeave={triggerBgHoverEnd}
                    className={`relative px-3 md:px-4 py-2 text-xs md:text-sm font-semibold transition-all duration-300 flex items-center gap-1.5 cursor-pointer ${
                      activeView === 'about' ? 'text-black dark:text-[#B9FF66] font-bold' : 'text-slate-500 dark:text-slate-400 hover:text-black dark:hover:text-[#B9FF66]'
                    }`}
                  >
                    About
                    {activeView === 'about' && (
                      <motion.div
                        layoutId="active-tab-line-landing"
                        className="absolute bottom-[-17px] left-0 right-0 h-[2.5px] bg-[#191A23] dark:bg-[#B9FF66] rounded-full"
                      />
                    )}
                  </button>

                  <button
                    onClick={() => setActiveView('workflow')}
                    onMouseEnter={triggerBgHoverStart}
                    onMouseLeave={triggerBgHoverEnd}
                    className={`relative px-3 md:px-4 py-2 text-xs md:text-sm font-semibold transition-all duration-300 flex items-center gap-1.5 cursor-pointer ${
                      activeView === 'workflow' ? 'text-black dark:text-[#B9FF66] font-bold' : 'text-slate-500 dark:text-slate-400 hover:text-black dark:hover:text-[#B9FF66]'
                    }`}
                  >
                    Workflow
                    {activeView === 'workflow' && (
                      <motion.div
                        layoutId="active-tab-line-landing"
                        className="absolute bottom-[-17px] left-0 right-0 h-[2.5px] bg-[#191A23] dark:bg-[#B9FF66] rounded-full"
                      />
                    )}
                  </button>

                  <button
                    onClick={() => setActiveView('usecases')}
                    onMouseEnter={triggerBgHoverStart}
                    onMouseLeave={triggerBgHoverEnd}
                    className={`relative px-3 md:px-4 py-2 text-xs md:text-sm font-semibold transition-all duration-300 flex items-center gap-1.5 cursor-pointer ${
                      activeView === 'usecases' ? 'text-black dark:text-[#B9FF66] font-bold' : 'text-slate-500 dark:text-slate-400 hover:text-black dark:hover:text-[#B9FF66]'
                    }`}
                  >
                    Use Cases
                    {activeView === 'usecases' && (
                      <motion.div
                        layoutId="active-tab-line-landing"
                        className="absolute bottom-[-17px] left-0 right-0 h-[2.5px] bg-[#191A23] dark:bg-[#B9FF66] rounded-full"
                      />
                    )}
                  </button>

                  <button
                    onClick={() => setActiveView('login')}
                    onMouseEnter={triggerBgHoverStart}
                    onMouseLeave={triggerBgHoverEnd}
                    className={`relative px-3 md:px-4 py-2 text-xs md:text-sm font-semibold transition-all duration-300 flex items-center gap-1.5 cursor-pointer ${
                      activeView === 'login' || activeView === 'register' ? 'text-black dark:text-[#B9FF66] font-bold' : 'text-slate-500 dark:text-slate-400 hover:text-black dark:hover:text-[#B9FF66]'
                    }`}
                  >
                    Sign In
                    {(activeView === 'login' || activeView === 'register') && (
                      <motion.div
                        layoutId="active-tab-line-landing"
                        className="absolute bottom-[-17px] left-0 right-0 h-[2.5px] bg-[#191A23] dark:bg-[#B9FF66] rounded-full"
                      />
                    )}
                  </button>
                </nav>
              )}
              {user && (
                <>
                <nav className="flex items-center gap-1 sm:gap-4">
                <button
                  onClick={() => setActiveView('about')}
                  onMouseEnter={triggerBgHoverStart}
                  onMouseLeave={triggerBgHoverEnd}
                  className={`relative px-3 md:px-4 py-2 text-xs md:text-sm font-semibold transition-all duration-300 flex items-center gap-1.5 cursor-pointer ${
                    activeView === 'about' ? 'text-black dark:text-[#B9FF66] font-bold' : 'text-slate-500 dark:text-slate-400 hover:text-black dark:hover:text-[#B9FF66]'
                  }`}
                >
                  <Info className="w-3.5 h-3.5" />
                  <span>About</span>
                  {activeView === 'about' && (
                    <motion.div
                      layoutId="active-tab-line"
                      className="absolute bottom-[-17px] left-0 right-0 h-[2.5px] bg-[#191A23] dark:bg-[#B9FF66] rounded-full"
                    />
                  )}
                </button>

                <button
                  disabled={isSimulating}
                  onClick={() => setActiveView('upload')}
                  onMouseEnter={triggerBgHoverStart}
                  onMouseLeave={triggerBgHoverEnd}
                  className={`relative px-3 md:px-4 py-2 text-xs md:text-sm font-semibold transition-all duration-300 flex items-center gap-1.5 cursor-pointer ${
                    activeView === 'upload' ? 'text-black dark:text-[#B9FF66] font-bold' : 'text-slate-500 dark:text-slate-400 hover:text-black dark:hover:text-[#B9FF66] disabled:opacity-50'
                  }`}
                >
                  <Upload className="w-3.5 h-3.5" />
                  <span>Upload</span>
                  {activeView === 'upload' && (
                    <motion.div
                      layoutId="active-tab-line"
                      className="absolute bottom-[-17px] left-0 right-0 h-[2.5px] bg-[#191A23] dark:bg-[#B9FF66] rounded-full"
                    />
                  )}
                </button>

                <button
                  disabled={isSimulating || !activeReport}
                  onClick={() => { if (activeReport) setActiveView('dashboard'); }}
                  onMouseEnter={triggerBgHoverStart}
                  onMouseLeave={triggerBgHoverEnd}
                  className={`relative px-3 md:px-4 py-2 text-xs md:text-sm font-semibold transition-all duration-300 flex items-center gap-1.5 cursor-pointer ${
                    activeView === 'dashboard' ? 'text-black dark:text-[#B9FF66] font-bold' : 'text-slate-500 dark:text-slate-400 hover:text-black dark:hover:text-[#B9FF66] disabled:opacity-50'
                  }`}
                >
                  <BarChart3 className="w-3.5 h-3.5" />
                  <span>Dashboard</span>
                  {activeView === 'dashboard' && (
                    <motion.div
                      layoutId="active-tab-line"
                      className="absolute bottom-[-17px] left-0 right-0 h-[2.5px] bg-[#191A23] dark:bg-[#B9FF66] rounded-full"
                    />
                  )}
                </button>

                <button
                  disabled={isSimulating}
                  onClick={() => {
                    setActiveView('history');
                    fetch(`${API_BASE}/history?user_id=${user.user_id}`)
                      .then(r => r.json())
                      .then(data => {
                        if (data && data.length > 0) {
                          const mapped = data.map(mapHistoryItem);
                          setHistoryItems(mapped);
                          localStorage.setItem(STORAGE_KEY, JSON.stringify(mapped));
                        }
                      })
                      .catch(() => {});
                  }}
                  onMouseEnter={triggerBgHoverStart}
                  onMouseLeave={triggerBgHoverEnd}
                  className={`relative px-3 md:px-4 py-2 text-xs md:text-sm font-semibold transition-all duration-300 flex items-center gap-1.5 cursor-pointer ${
                    activeView === 'history' ? 'text-black dark:text-[#B9FF66] font-bold' : 'text-slate-500 dark:text-slate-400 hover:text-black dark:hover:text-[#B9FF66] disabled:opacity-50'
                  }`}
                >
                  <History className="w-3.5 h-3.5" />
                  <span>History</span>
                  {activeView === 'history' && (
                    <motion.div
                      layoutId="active-tab-line"
                      className="absolute bottom-[-17px] left-0 right-0 h-[2.5px] bg-[#191A23] dark:bg-[#B9FF66] rounded-full"
                    />
                  )}
                </button>
              </nav>

              <span className="hidden sm:inline text-[10px] font-mono font-bold tracking-wider uppercase text-slate-400 dark:text-slate-500 px-1 select-none">
                {user.username}
              </span>

              <button
                onClick={() => {
                  localStorage.removeItem(AUTH_KEY);
                  setUser(null);
                  setActiveView('login');
                }}
                onMouseEnter={triggerBgHoverStart}
                onMouseLeave={triggerBgHoverEnd}
                className="flex items-center gap-1.5 p-2 rounded-xl bg-white dark:bg-slate-900 border border-[#191A23] dark:border-white/10 text-slate-600 dark:text-slate-450 hover:text-red-500 transition-all cursor-pointer shadow-[2px_2px_0px_#191A23] dark:shadow-[2px_2px_0px_#B9FF66]"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
                <span className="text-[10px] font-mono font-bold tracking-wider uppercase hidden sm:inline px-1">Logout</span>
              </button>
              </>
            )}

            </div>

          </div>
        </header>

        <main className="flex-1 flex flex-col justify-center">
          <AnimatePresence mode="wait">
            {activeView === 'about' && (
              <AboutView onNavigate={setActiveView} user={user} />
            )}

            {activeView === 'workflow' && (
              <WorkflowView onNavigate={setActiveView} />
            )}

            {activeView === 'usecases' && (
              <UseCasesView onNavigate={setActiveView} />
            )}

            {activeView === 'login' && (
              <motion.div
                key="login-tab"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25 }}
                className="w-full max-w-md mx-auto mt-16 px-4"
              >
                <div className="rounded-2xl border-2 border-[#191A23] dark:border-white/10 bg-white dark:bg-slate-900 p-8 shadow-[4px_4px_0px_#191A23] dark:shadow-[4px_4px_0px_#B9FF66]">
                  <h2 className="text-2xl font-bold mb-2">Sign in</h2>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">Access your interview analysis workspace.</p>
                  <form onSubmit={async (e) => {
                    e.preventDefault();
                    const form = e.target as HTMLFormElement;
                    const fd = new FormData(form);
                    setAuthLoading(true);
                    try {
                      const res = await fetch(`${API_BASE}/login`, { method: 'POST', body: fd });
                      if (!res.ok) {
                        const err = await res.json();
                        alert(err.detail || 'Login failed');
                      } else {
                        const data = await res.json();
                        localStorage.setItem(AUTH_KEY, JSON.stringify(data));
                        localStorage.removeItem(STORAGE_KEY);
                        setUser(data);
                        setHistoryItems([]);
                        setActiveReport(null);
                        setActiveView('upload');
                      }
                    } catch { alert('Login failed'); }
                    setAuthLoading(false);
                  }}>
                    <input name="username" required minLength={3} placeholder="Username" className="w-full mb-3 px-4 py-3 rounded-xl border-2 border-[#191A23] dark:border-white/10 bg-white dark:bg-slate-800 text-sm font-medium text-slate-900 dark:text-white outline-none focus:border-[#B9FF66] transition-colors" />
                    <div className="relative mb-4">
                      <input name="password" type={showPassword ? 'text' : 'password'} required minLength={6} placeholder="Password" className="w-full px-4 py-3 pr-12 rounded-xl border-2 border-[#191A23] dark:border-white/10 bg-white dark:bg-slate-800 text-sm font-medium text-slate-900 dark:text-white outline-none focus:border-[#B9FF66] transition-colors" />
                      <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white cursor-pointer">
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                    <button type="submit" disabled={authLoading} className="w-full px-6 py-3 rounded-xl bg-[#B9FF66] border-2 border-[#191A23] text-black font-bold text-sm hover:bg-[#a8ee55] transition-all shadow-[2px_2px_0px_#191A23] disabled:opacity-50">
                      {authLoading ? 'Signing in...' : 'Sign in'}
                    </button>
                  </form>
                  <p className="text-center text-xs text-slate-500 dark:text-slate-400 mt-4">
                    Don't have an account?{' '}
                    <button onClick={() => setActiveView('register')} className="text-[#191A23] dark:text-[#B9FF66] font-semibold underline cursor-pointer">Register</button>
                  </p>
                </div>
              </motion.div>
            )}

            {activeView === 'register' && (
              <motion.div
                key="register-tab"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25 }}
                className="w-full max-w-md mx-auto mt-16 px-4"
              >
                <div className="rounded-2xl border-2 border-[#191A23] dark:border-white/10 bg-white dark:bg-slate-900 p-8 shadow-[4px_4px_0px_#191A23] dark:shadow-[4px_4px_0px_#B9FF66]">
                  <h2 className="text-2xl font-bold mb-2">Create account</h2>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">Register to start tracking your interview practice.</p>
                  <form onSubmit={async (e) => {
                    e.preventDefault();
                    const form = e.target as HTMLFormElement;
                    const fd = new FormData(form);
                    const password = form.password.value;
                    const confirm = form.confirm.value;
                    if (password !== confirm) { alert('Passwords do not match'); return; }
                    setAuthLoading(true);
                    try {
                      const res = await fetch(`${API_BASE}/register`, { method: 'POST', body: fd });
                      if (!res.ok) {
                        const err = await res.json();
                        alert(err.detail || 'Registration failed');
                      } else {
                        alert('Account created. Please sign in.');
                        setActiveView('login');
                      }
                    } catch { alert('Registration failed'); }
                    setAuthLoading(false);
                  }}>
                    <input name="username" required minLength={3} maxLength={30} placeholder="Username (3–30 chars)" className="w-full mb-3 px-4 py-3 rounded-xl border-2 border-[#191A23] dark:border-white/10 bg-white dark:bg-slate-800 text-sm font-medium text-slate-900 dark:text-white outline-none focus:border-[#B9FF66] transition-colors" />
                    <div className="relative mb-3">
                      <input name="password" type={showPassword ? 'text' : 'password'} required minLength={6} placeholder="Password (min 6 chars)" className="w-full px-4 py-3 pr-12 rounded-xl border-2 border-[#191A23] dark:border-white/10 bg-white dark:bg-slate-800 text-sm font-medium text-slate-900 dark:text-white outline-none focus:border-[#B9FF66] transition-colors" />
                      <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white cursor-pointer">
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                    <input name="confirm" type={showPassword ? 'text' : 'password'} required minLength={6} placeholder="Confirm password" className="w-full mb-4 px-4 py-3 rounded-xl border-2 border-[#191A23] dark:border-white/10 bg-white dark:bg-slate-800 text-sm font-medium text-slate-900 dark:text-white outline-none focus:border-[#B9FF66] transition-colors" />
                    <button type="submit" disabled={authLoading} className="w-full px-6 py-3 rounded-xl bg-[#B9FF66] border-2 border-[#191A23] text-black font-bold text-sm hover:bg-[#a8ee55] transition-all shadow-[2px_2px_0px_#191A23] disabled:opacity-50">
                      {authLoading ? 'Creating account...' : 'Create account'}
                    </button>
                  </form>
                  <p className="text-center text-xs text-slate-500 dark:text-slate-400 mt-4">
                    Already have an account?{' '}
                    <button onClick={() => setActiveView('login')} className="text-[#191A23] dark:text-[#B9FF66] font-semibold underline cursor-pointer">Sign in</button>
                  </p>
                </div>
              </motion.div>
            )}

            {activeView === 'upload' && (
              <motion.div
                key="upload-tab"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25 }}
                className="w-full"
              >
                <UploadView
                  onStartSimulation={handleStartSimulation}
                  isSimulating={isSimulating}
                  simulationStep={simulationStep}
                  simulationProgress={simulationProgress}
                />
              </motion.div>
            )}

            {activeView === 'dashboard' && activeReport && (
              <motion.div
                key="dashboard-tab"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25 }}
                className="w-full"
              >
                <DashboardView report={activeReport} />
              </motion.div>
            )}

            {activeView === 'history' && (
              <motion.div
                key="history-tab"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25 }}
                className="w-full"
              >
                <HistoryView
                  historyItems={historyItems}
                  onLoadReport={handleLoadReport}
                  onDeleteReport={handleDeleteReport}
                  onRestorePresets={handleRestorePresets}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>

      <footer className="w-full py-6 mt-16 border-t border-slate-200/50 dark:border-white/5 relative z-10 text-center text-xs text-slate-450 dark:text-slate-500 font-light font-sans transition-colors duration-400">
        <p>© 2026 Vocalytics Studio. AI Communication Analysis Workspace.</p>
      </footer>
    </div>
  );
}

function mapHistoryItem(item: any): AnalysisReport {
  const ts = typeof item.timestamp === 'string'
    ? new Date(item.timestamp).getTime()
    : (item.timestamp || Date.now());

  const execSummary: string = item.executiveSummary || '';

  const keyStrengths = item.keyStrengths ? [...item.keyStrengths] : [];
  const coachingPriorities = item.coachingPriorities ? [...item.coachingPriorities] : [];

  return {
    id: item.id || `hist-${Date.now()}`,
    timestamp: ts,
    candidateName: item.candidateName || 'Candidate',
    roleName: item.roleName || 'Role',
    durationSeconds: item.durationSeconds || 0,
    overallScore: item.overallScore || 0,
    status: 'report',
    metrics: item.metrics || {
      confidence: 0,
      pacing: 0,
      fillerCount: 0,
      eyeContact: 0,
      coherence: 0,
    },
    behavioralSignals: item.behavioralSignals || {
      pacingFeedback: '',
      fillerWordsFeedback: '',
      eyeContactFeedback: '',
      expressionFeedback: '',
    },
    executiveSummary: execSummary,
    keyStrengths: keyStrengths,
    coachingPriorities: coachingPriorities,
    transcript: item.transcript || [],
    videoFileUrl: item.videoFileUrl || undefined,
    emotionDistribution: item.emotionDistribution || undefined,
  };
}
