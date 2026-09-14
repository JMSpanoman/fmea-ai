import { describe, expect, it } from 'vitest';
import { resolveApiBaseUrl } from './apiBaseUrl';

describe('resolveApiBaseUrl', () => {
  it('defaults to same-origin /api for production nginx and local Vite proxy', () => {
    expect(resolveApiBaseUrl()).toBe('/api');
  });
});
