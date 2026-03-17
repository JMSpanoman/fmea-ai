/**
 * ProRoute: Wraps Pro-only route content. Redirects Lite users to /dfmea.
 */
import React from 'react';
import { Outlet } from 'react-router-dom';
import { ProGate } from './ProGate';

export function ProRoute() {
  return (
    <ProGate redirectLiteTo="/dfmea">
      <Outlet />
    </ProGate>
  );
}
