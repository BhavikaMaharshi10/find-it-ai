import type { ReactNode, CSSProperties } from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  style?: CSSProperties;
}

export default function Card({ children, className = '', hover = true, style }: CardProps) {
  return (
    <motion.div
      className={`card ${className}`}
      style={style}
      whileHover={hover ? { y: -2 } : undefined}
      transition={{ duration: 0.2 }}
    >
      {children}
    </motion.div>
  );
}
