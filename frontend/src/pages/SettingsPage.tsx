import { useForm } from 'react-hook-form';
import { authApi } from '../api/endpoints';
import Button from '../components/common/Button';
import Card from '../components/common/Card';

export default function SettingsPage() {
  const { register, handleSubmit, formState: { isSubmitSuccessful }, reset } = useForm<{
    old_password: string;
    new_password: string;
    new_password_confirm: string;
  }>();

  const onSubmit = async (data: {
    old_password: string;
    new_password: string;
    new_password_confirm: string;
  }) => {
    await authApi.changePassword(data);
    reset();
  };

  return (
    <div>
      <h1>Settings</h1>

      <Card style={{ marginTop: '1.5rem' }}>
        <h3>Change Password</h3>
        {isSubmitSuccessful && (
          <p style={{ color: 'var(--color-success)', margin: '0.5rem 0' }}>Password updated.</p>
        )}
        <form onSubmit={handleSubmit(onSubmit)} style={{ marginTop: '1rem' }}>
          <div style={{ display: 'grid', gap: '1rem' }}>
            <input type="password" className="input" placeholder="Current password" {...register('old_password', { required: true })} />
            <input type="password" className="input" placeholder="New password" {...register('new_password', { required: true, minLength: 8 })} />
            <input type="password" className="input" placeholder="Confirm new password" {...register('new_password_confirm', { required: true })} />
          </div>
          <Button type="submit" style={{ marginTop: '1rem' }}>Update Password</Button>
        </form>
      </Card>
    </div>
  );
}
