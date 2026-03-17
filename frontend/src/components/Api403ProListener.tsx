/**
 * Listens for api:403:pro custom events (from axios 403 Pro gate responses)
 * and shows an upgrade toast.
 */
import React, { useEffect } from 'react';
import { useToast } from './ui/Toast';

export function Api403ProListener() {
  const { addToast } = useToast();

  useEffect(() => {
    const handler = (e: CustomEvent<{ message?: string }>) => {
      const msg = e.detail?.message || 'This feature requires SmartRisk Pro. Upgrade to access.';
      addToast(msg, 'warning', 6000);
    };
    window.addEventListener('api:403:pro', handler as EventListener);
    return () => window.removeEventListener('api:403:pro', handler as EventListener);
  }, [addToast]);

  return null;
}
