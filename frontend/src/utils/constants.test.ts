import { describe, expect, it } from 'vitest';
import { ROUTES, APPLICATION_STATUSES } from './constants';

describe('constants', () => {
  it('defines all required routes', () => {
    expect(ROUTES.DASHBOARD).toBe('/dashboard');
    expect(ROUTES.JOBS).toBe('/jobs');
    expect(ROUTES.RECOMMENDATIONS).toBe('/recommendations');
  });

  it('defines application statuses', () => {
    expect(APPLICATION_STATUSES.length).toBe(6);
    expect(APPLICATION_STATUSES[0].value).toBe('applied');
  });
});
