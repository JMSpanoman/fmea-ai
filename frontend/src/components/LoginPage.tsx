import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginPage.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

interface LoginFormData {
  username: string;
  password: string;
}

interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  fullName: string;
  company: string;
  department: string;
}

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [loginData, setLoginData] = useState<LoginFormData>({
    username: '',
    password: ''
  });

  const [registerData, setRegisterData] = useState<RegisterFormData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    company: '',
    department: ''
  });

  const handleLoginChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLoginData({
      ...loginData,
      [e.target.name]: e.target.value
    });
  };

  const handleRegisterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRegisterData({
      ...registerData,
      [e.target.name]: e.target.value
    });
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: loginData.username,
          password: loginData.password
        })
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        setSuccess('Login successful!');
        setTimeout(() => {
          navigate('/');
        }, 1000);
      } else {
        setError(data.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    if (registerData.password !== registerData.confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: registerData.username,
          email: registerData.email,
          password: registerData.password,
          full_name: registerData.fullName,
          company: registerData.company,
          department: registerData.department
        })
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('Registration successful! Please login.');
        setIsLogin(true);
        setRegisterData({
          username: '',
          email: '',
          password: '',
          confirmPassword: '',
          fullName: '',
          company: '',
          department: ''
        });
      } else {
        setError(data.detail || 'Registration failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDevLogin = async () => {
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${API_BASE_URL}/auth/dev-login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        setSuccess('Development login successful!');
        setTimeout(() => {
          navigate('/');
        }, 1000);
      } else {
        setError('Development login failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>Foton aiQMS</h1>
          <p>Your comprehensive quality management system</p>
        </div>

        <div className="login-tabs">
          <button
            className={`tab ${isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(true)}
          >
            Login
          </button>
          <button
            className={`tab ${!isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(false)}
          >
            Register
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        {isLogin ? (
          <form onSubmit={handleLogin} className="login-form">
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                value={loginData.username}
                onChange={handleLoginChange}
                required
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={loginData.password}
                onChange={handleLoginChange}
                required
                disabled={isLoading}
              />
            </div>

            <button
              type="submit"
              className="login-button"
              disabled={isLoading}
            >
              {isLoading ? 'Logging in...' : 'Login'}
            </button>

            <div className="dev-login-section">
              <hr />
              <button
                type="button"
                className="dev-login-button"
                onClick={handleDevLogin}
                disabled={isLoading}
              >
                {isLoading ? 'Logging in...' : 'Development Login'}
              </button>
              <p className="dev-note">Quick access for development</p>
            </div>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="register-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="reg-username">Username</label>
                <input
                  type="text"
                  id="reg-username"
                  name="username"
                  value={registerData.username}
                  onChange={handleRegisterChange}
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={registerData.email}
                  onChange={handleRegisterChange}
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="fullName">Full Name</label>
              <input
                type="text"
                id="fullName"
                name="fullName"
                value={registerData.fullName}
                onChange={handleRegisterChange}
                required
                disabled={isLoading}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="company">Company</label>
                <input
                  type="text"
                  id="company"
                  name="company"
                  value={registerData.company}
                  onChange={handleRegisterChange}
                  disabled={isLoading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="department">Department</label>
                <input
                  type="text"
                  id="department"
                  name="department"
                  value={registerData.department}
                  onChange={handleRegisterChange}
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="reg-password">Password</label>
                <input
                  type="password"
                  id="reg-password"
                  name="password"
                  value={registerData.password}
                  onChange={handleRegisterChange}
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword">Confirm Password</label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={registerData.confirmPassword}
                  onChange={handleRegisterChange}
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            <button
              type="submit"
              className="register-button"
              disabled={isLoading}
            >
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default LoginPage; 