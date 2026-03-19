import { redirect } from 'next/navigation';
import { auth, signOut } from '@/auth';
import { apiClient } from '@/lib/api';

interface Decision {
  id: string;
  title: string;
  status: string;
  createdAt: string;
  contextPrompt?: string;
  _count?: {
    participants: number;
  };
}

export default async function DashboardPage() {
  const session = await auth();

  if (!session) {
    redirect('/login');
  }

  let decisions: Decision[] = [];
  let fetchError = '';

  try {
    decisions = await apiClient<Decision[]>('/api/v1/decisions', {
      token: session.accessToken,
    });
  } catch (err: any) {
    fetchError = err.message || 'Failed to load decisions';
  }

  return (
    <div className="dashboard-layout">
      <header className="dashboard-header">
        <h1>QUAICU</h1>
        <div className="user-info">
          <span>{session.user.email}</span>
          <form
            action={async () => {
              'use server';
              await signOut({ redirectTo: '/login' });
            }}
          >
            <button type="submit" className="btn-signout">
              Sign out
            </button>
          </form>
        </div>
      </header>

      <main className="dashboard-content">
        <h2>Your Decisions</h2>

        {fetchError && <div className="error-message">{fetchError}</div>}

        {decisions.length === 0 && !fetchError ? (
          <div className="empty-state">
            <p>No decisions yet.</p>
            <p>Create your first decision to get started.</p>
          </div>
        ) : (
          <div className="decisions-grid">
            {decisions.map((decision) => (
              <div key={decision.id} className="decision-card">
                <h3>{decision.title}</h3>
                <div className="meta">
                  <span className={`status-badge status-${decision.status}`}>
                    {decision.status.replace('_', ' ')}
                  </span>
                  <span>
                    {decision._count?.participants ?? 0} participant
                    {(decision._count?.participants ?? 0) !== 1 ? 's' : ''}
                  </span>
                  <span>
                    {new Date(decision.createdAt).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
