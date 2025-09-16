// src/services/authService.ts

// Declare global fmeaApi
declare global {
  interface Window {
    fmeaApi: any;
  }
}

class AuthService {
  private static instance: AuthService;
  private token: string | null = null;

  private constructor() {}

  static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  async authenticate(): Promise<string> {
    try {
      console.log('AuthService: Starting authentication...');
      if (!window.fmeaApi) {
        console.error('AuthService: fmeaApi not available on window object');
        throw new Error('fmeaApi not available');
      }
      console.log('AuthService: fmeaApi is available');

      // Call the dev login endpoint
      console.log('AuthService: Calling window.fmeaApi.devLogin()...');
      const response = await window.fmeaApi.devLogin();
      console.log('AuthService: devLogin response:', response);
      
      // Extract the token from the response
      if (response && response.access_token && typeof response.access_token === 'string') {
        const accessToken = response.access_token as string;
        this.token = accessToken;
        // Store token in localStorage for axios interceptor
        localStorage.setItem('token', accessToken);
        // Also set the token in the fmeaApi instance
        if (window.fmeaApi) {
          window.fmeaApi.setToken(accessToken);
          console.log('AuthService: Token set in fmeaApi');
        }
        console.log('AuthService: Token stored successfully');
        return accessToken;
      } else {
        console.error('AuthService: No access token received in response:', response);
        throw new Error('No access token received');
      }
    } catch (error) {
      console.error('AuthService: Authentication failed:', error);
      throw error;
    }
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('token');
    }
    return this.token;
  }

  isAuthenticated(): boolean {
    const token = this.getToken();
    return !!token;
  }

  logout(): void {
    this.token = null;
    localStorage.removeItem('token');
  }
}

export default AuthService.getInstance(); 