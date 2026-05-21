/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect } from 'react';
import { motion } from 'motion/react';

export default function ThreeDBackground() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isActionHovered, setIsActionHovered] = useState(false);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      // Normalize mouse coordinates from -0.5 to +0.5
      setMousePosition({
        x: (e.clientX / window.innerWidth) - 0.5,
        y: (e.clientY / window.innerHeight) - 0.5,
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Listen to visual action hovered emitters to trigger extra background shift
  useEffect(() => {
    const handleHoverStart = () => setIsActionHovered(true);
    const handleHoverEnd = () => setIsActionHovered(false);

    window.addEventListener('action-hover-start', handleHoverStart);
    window.addEventListener('action-hover-end', handleHoverEnd);
    return () => {
      window.removeEventListener('action-hover-start', handleHoverStart);
      window.removeEventListener('action-hover-end', handleHoverEnd);
    };
  }, []);

  const displaceFactor = isActionHovered ? 1.6 : 1.0;

  // Spring physical config objects for each layer
  const spring1 = { type: 'spring', stiffness: 45, damping: 25, mass: 1.2 };
  const spring2 = { type: 'spring', stiffness: 35, damping: 22, mass: 1.5 };
  const spring3 = { type: 'spring', stiffness: 50, damping: 26, mass: 1.0 };
  const spring4 = { type: 'spring', stiffness: 55, damping: 28, mass: 0.9 };

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0 bg-[#191A23]">
      {/* Abstract Positivus Accent Grid (clean & crisp dark boundaries/borders representation) */}
      <svg className="absolute inset-0 w-full h-full opacity-[0.06] stroke-white" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse">
            <path d="M 60 0 L 0 0 0 60" fill="none" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>

      {/* Floating Positivus Brand Shapes - 1. Iconic Brand Asterisk (Top Right) */}
      <motion.div
        animate={{
          x: mousePosition.x * 50 * displaceFactor,
          y: mousePosition.y * 50 * displaceFactor,
          scale: isActionHovered ? 1.1 : 1.0,
          rotate: mousePosition.x * 120 + (isActionHovered ? 45 : 0),
        }}
        transition={spring1}
        className="absolute top-[12%] right-[10%] w-48 h-48 flex items-center justify-center opacity-80"
      >
        {/* Flat Custom Pure Rendered 8-Spike Positivus Star/Asterisk */}
        <svg viewBox="0 0 100 100" className="w-full h-full fill-current text-[#B9FF66]" xmlns="http://www.w3.org/2000/svg">
          <g transform="translate(50,50)">
            {Array.from({ length: 8 }).map((_, i) => (
              <rect
                key={i}
                x="-6"
                y="-45"
                width="12"
                height="90"
                rx="6"
                transform={`rotate(${i * 45})`}
              />
            ))}
            <circle cx="0" cy="0" r="14" className="fill-[#191A23]" />
          </g>
        </svg>
      </motion.div>

      {/* Floating Shape 2 - Lime Green Solid Circle with Thick Border (Bottom Left) */}
      <motion.div
        animate={{
          x: mousePosition.x * -70 * displaceFactor,
          y: mousePosition.y * -70 * displaceFactor,
          scale: isActionHovered ? 1.15 : 1.0,
          rotate: mousePosition.y * -60,
        }}
        transition={spring2}
        className="absolute bottom-[10%] left-[8%] w-32 h-32"
      >
        <div className="w-full h-full rounded-full bg-[#B9FF66] border-2 border-[#191A23] dark:border-white shadow-[4px_4px_0px_rgba(25,26,35,1)] dark:shadow-[4px_4px_0px_#B9FF66]" />
      </motion.div>

      {/* Floating Shape 3 - Isometric Neo-Brutalist Card Outline (Centered Left) */}
      <motion.div
        animate={{
          x: mousePosition.x * 40 * displaceFactor,
          y: mousePosition.y * -55 * displaceFactor,
          scale: isActionHovered ? 1.05 : 1.0,
          rotate: 15 + mousePosition.x * 30,
        }}
        transition={spring3}
        className="absolute top-[40%] left-[5%] w-24 h-24 hidden md:block"
      >
        <div className="w-full h-full rounded-2xl bg-white dark:bg-[#292A32] border-2 border-[#191A23] dark:border-white shadow-[6px_6px_0px_#B9FF66]" />
      </motion.div>

      {/* Floating Shape 4 - Iconic Mini Brand Asterisk (Top Left) */}
      <motion.div
        animate={{
          x: mousePosition.x * -50 * displaceFactor,
          y: mousePosition.y * 30 * displaceFactor,
          scale: isActionHovered ? 1.25 : 1.0,
          rotate: mousePosition.y * 180,
        }}
        transition={spring4}
        className="absolute top-[18%] left-[20%] w-12 h-12 opacity-60"
      >
        <svg viewBox="0 0 100 100" className="w-full h-full fill-current text-slate-600" xmlns="http://www.w3.org/2000/svg">
          <g transform="translate(50,50)">
            {Array.from({ length: 8 }).map((_, i) => (
              <rect
                key={i}
                x="-8"
                y="-45"
                width="16"
                height="90"
                rx="8"
                transform={`rotate(${i * 45})`}
              />
            ))}
          </g>
        </svg>
      </motion.div>

      {/* Bottom Floating Pill (Bottom Right) */}
      <motion.div
        animate={{
          x: mousePosition.x * 60 * displaceFactor,
          y: mousePosition.y * -30 * displaceFactor,
          scale: isActionHovered ? 1.1 : 1.0,
          rotate: -10 + mousePosition.x * 20,
        }}
        transition={spring1}
        className="absolute bottom-[15%] right-[15%] w-48 h-12 hidden lg:block"
      >
        <div className="w-full h-full rounded-full bg-[#B9FF66] border-2 border-[#191A23] dark:border-white shadow-[4px_4px_0px_#191A23] dark:shadow-[4px_4px_0px_white]" />
      </motion.div>
    </div>
  );
}
