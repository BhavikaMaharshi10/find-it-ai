import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useCallback, useState } from 'react';
import { resumeApi } from '../api/endpoints';
import Card from '../components/common/Card';

export default function ResumePage() {
  const [dragOver, setDragOver] = useState(false);
  const queryClient = useQueryClient();

  const { data: resume, isLoading } = useQuery({
    queryKey: ['resume', 'active'],
    queryFn: () => resumeApi.getActive().then((r) => r.data).catch(() => null),
    retry: false,
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => resumeApi.upload(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resume'] });
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });

  const handleFile = useCallback((file: File) => {
    if (file.type === 'application/pdf') {
      uploadMutation.mutate(file);
    }
  }, [uploadMutation]);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div>
      <h1>Resume</h1>
      <p className="text-secondary" style={{ marginBottom: '1.5rem' }}>
        Upload your resume for AI analysis and job matching
      </p>

      <Card>
        <div
          className={`resume-upload ${dragOver ? 'resume-upload--active' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          style={{
            border: '2px dashed var(--color-border)',
            borderRadius: '1rem',
            padding: '3rem',
            textAlign: 'center',
          }}
        >
          <p style={{ marginBottom: '1rem' }}>Drag & drop your PDF resume here, or click to browse</p>
          <input
            type="file"
            accept=".pdf"
            id="resume-file"
            hidden
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          />
          <label htmlFor="resume-file">
            <span className="btn btn--primary" style={{ cursor: 'pointer' }}>
              {uploadMutation.isPending ? 'Uploading...' : 'Browse Files'}
            </span>
          </label>
        </div>
      </Card>

      {isLoading ? (
        <p style={{ marginTop: '1.5rem' }}>Loading resume...</p>
      ) : resume ? (
        <div style={{ marginTop: '2rem' }}>
          <h2>Active Resume: {resume.original_filename}</h2>
          {resume.ai_summary && (
            <Card style={{ marginTop: '1rem' }}>
              <h3>AI Summary</h3>
              <p>{resume.ai_summary}</p>
            </Card>
          )}
          {resume.skills.length > 0 && (
            <Card style={{ marginTop: '1rem' }}>
              <h3>Skills</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
                {resume.skills.map((s) => <span key={s} className="badge">{s}</span>)}
              </div>
            </Card>
          )}
          {resume.work_experience.length > 0 && (
            <Card style={{ marginTop: '1rem' }}>
              <h3>Experience</h3>
              {resume.work_experience.map((exp, i) => (
                <div key={i} style={{ marginTop: '0.75rem' }}>
                  <strong>{exp.title}</strong> at {exp.company}
                  <p className="text-secondary" style={{ fontSize: '0.875rem' }}>{exp.description}</p>
                </div>
              ))}
            </Card>
          )}
        </div>
      ) : (
        !uploadMutation.isPending && (
          <Card style={{ marginTop: '1.5rem' }}>
            <p>No resume uploaded yet.</p>
          </Card>
        )
      )}
    </div>
  );
}
