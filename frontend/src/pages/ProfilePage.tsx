import { useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { profileApi } from '../api/endpoints';
import Button from '../components/common/Button';
import Card from '../components/common/Card';
import type { Profile } from '../types';

export default function ProfilePage() {
  const queryClient = useQueryClient();
  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: () => profileApi.get().then((r) => r.data),
  });

  const { register, handleSubmit, reset } = useForm<Partial<Profile>>();

  useEffect(() => {
    if (profile) {
      reset({
        headline: profile.headline,
        location: profile.location,
        phone: profile.phone,
        linkedin_url: profile.linkedin_url,
        github_url: profile.github_url,
      });
    }
  }, [profile, reset]);

  const updateMutation = useMutation({
    mutationFn: (data: Partial<Profile>) => profileApi.update(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });

  if (isLoading) return <p>Loading profile...</p>;

  return (
    <div>
      <h1>Profile</h1>
      <p className="text-secondary" style={{ marginBottom: '1.5rem' }}>
        {profile?.user.first_name} {profile?.user.last_name} — {profile?.user.email}
      </p>

      <Card>
        <form onSubmit={handleSubmit((data) => updateMutation.mutate(data))}>
          <div style={{ display: 'grid', gap: '1rem' }}>
            <div>
              <label htmlFor="headline">Headline</label>
              <input id="headline" className="input" defaultValue={profile?.headline} {...register('headline')} />
            </div>
            <div>
              <label htmlFor="location">Location</label>
              <input id="location" className="input" defaultValue={profile?.location} {...register('location')} />
            </div>
            <div>
              <label htmlFor="phone">Phone</label>
              <input id="phone" className="input" defaultValue={profile?.phone} {...register('phone')} />
            </div>
            <div>
              <label htmlFor="linkedin">LinkedIn URL</label>
              <input id="linkedin" className="input" defaultValue={profile?.linkedin_url} {...register('linkedin_url')} />
            </div>
            <div>
              <label htmlFor="github">GitHub URL</label>
              <input id="github" className="input" defaultValue={profile?.github_url} {...register('github_url')} />
            </div>
          </div>
          <Button type="submit" loading={updateMutation.isPending} style={{ marginTop: '1.5rem' }}>
            Save Profile
          </Button>
        </form>
      </Card>
    </div>
  );
}
