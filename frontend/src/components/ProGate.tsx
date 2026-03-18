/**
 * ProGate: Shown when a Lite user hits a Pro-only feature.
 * Renders upgrade CTA and optionally redirects to Lite landing.
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { isProPlan } from '../config/features';

interface ProGateProps {
  /** Current user plan from AuthContext (uses context if not passed) */
  plan?: string | null;
  /** Content to render for Pro users */
  children: React.ReactNode;
  /** Optional: redirect Lite users instead of showing gate */
  redirectLiteTo?: string;
  /** Optional: custom message */
  message?: string;
}

/**
 * Wrapper: only render children for Pro users. Otherwise show upgrade gate.
 */
export function ProGate({ plan: planProp, children, redirectLiteTo, message }: ProGateProps) {
  const { user } = useAuth();
  const plan = planProp ?? user?.plan;
  const navigate = useNavigate();
  const isPro = isProPlan(plan);

  React.useEffect(() => {
    if (!isPro && redirectLiteTo) {
      navigate(redirectLiteTo, { replace: true });
      return;
    }
  }, [isPro, redirectLiteTo, navigate]);

  if (isPro) {
    return <>{children}</>;
  }

  if (redirectLiteTo) {
    return null; // Redirect in progress
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] px-6 text-center">
      <div className="max-w-md">
        <div className="text-6xl mb-4">🔒</div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          SmartRisk Pro feature
        </h2>
        <p className="text-gray-600 mb-6">
          {message ||
            'This feature is available on SmartRisk Pro. Upgrade to access projects, traceability, design controls, and more.'}
        </p>
        <button
          onClick={() => navigate('/dfmea')}
          className="px-4 py-2 bg-primary text-gray-900 rounded-lg hover:bg-primary/90 transition"
        >
          Back to FMEA
        </button>
        <p className="mt-4 text-sm text-gray-500">
          Contact us to upgrade to SmartRisk Pro.
        </p>
      </div>
    </div>
  );
}

export default ProGate;
