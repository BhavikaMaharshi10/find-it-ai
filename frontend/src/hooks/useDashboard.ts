import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { dashboardApi } from '../api/endpoints';

export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => dashboardApi.getStats().then((r) => r.data),
  });
}

export function useMatchDistribution() {
  return useQuery({
    queryKey: ['dashboard', 'match-distribution'],
    queryFn: () => dashboardApi.getMatchDistribution().then((r) => r.data),
  });
}

export function useSkillGaps() {
  return useQuery({
    queryKey: ['dashboard', 'skill-gaps'],
    queryFn: () => dashboardApi.getSkillGaps().then((r) => r.data),
  });
}

export function useApplicationTrends() {
  return useQuery({
    queryKey: ['dashboard', 'application-trends'],
    queryFn: () => dashboardApi.getApplicationTrends().then((r) => r.data),
  });
}

export function useApplicationStatus() {
  return useQuery({
    queryKey: ['dashboard', 'application-status'],
    queryFn: () => dashboardApi.getApplicationStatus().then((r) => r.data),
  });
}

export function useRefreshRecommendations() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => import('../api/endpoints').then((m) => m.recommendationsApi.generate()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
      queryClient.invalidateQueries({ queryKey: ['learning-roadmap'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
