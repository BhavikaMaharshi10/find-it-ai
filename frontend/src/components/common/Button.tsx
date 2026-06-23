import type { ReactNode, ButtonHTMLAttributes } from 'react';
import { motion } from 'framer-motion';
import { classNames } from '../../utils/helpers';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  children: ReactNode;
}

export default function Button({
  variant = 'primary',
  size = 'md',
  loading,
  children,
  className,
  disabled,
  type = 'button',
  ...props
}: ButtonProps) {
  return (
    <motion.button
      type={type}
      whileTap={{ scale: 0.98 }}
      className={classNames('btn', `btn--${variant}`, size === 'lg' && 'btn--lg', className)}
      disabled={disabled || loading}
      {...(props as object)}
    >
      {loading ? 'Loading...' : children}
    </motion.button>
  );
}
