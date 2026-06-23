import { describe, expect, it } from 'vitest';
import { formatDate, formatScore, getInitials, truncate } from '../utils/helpers';

describe('helpers', () => {
  it('formatScore rounds to percentage', () => {
    expect(formatScore(92.4)).toBe('92%');
  });

  it('getInitials returns uppercase initials', () => {
    expect(getInitials('John', 'Doe')).toBe('JD');
  });

  it('truncate shortens long text', () => {
    expect(truncate('Hello World', 5)).toBe('Hello...');
  });

  it('formatDate returns readable date', () => {
    expect(formatDate('2024-01-15')).toMatch(/Jan/);
  });
});
