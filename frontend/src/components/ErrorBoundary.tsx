import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0">
                <i className="fa-solid fa-exclamation-triangle text-red-500 text-2xl"></i>
              </div>
              <div className="ml-3">
                <h1 className="text-lg font-semibold text-gray-900">Something went wrong</h1>
                <p className="text-sm text-gray-600">An error occurred while loading this page</p>
              </div>
            </div>
            
            {this.state.error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <h3 className="text-sm font-medium text-red-800 mb-2">Error Details:</h3>
                <div className="text-xs text-red-700 font-mono">
                  <p><strong>Message:</strong> {this.state.error.message}</p>
                  <p><strong>Stack:</strong></p>
                  <pre className="whitespace-pre-wrap overflow-auto max-h-32">
                    {this.state.error.stack}
                  </pre>
                </div>
              </div>
            )}

            {this.state.errorInfo && (
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                <h3 className="text-sm font-medium text-blue-800 mb-2">Component Stack:</h3>
                <div className="text-xs text-blue-700 font-mono">
                  <pre className="whitespace-pre-wrap overflow-auto max-h-32">
                    {this.state.errorInfo.componentStack}
                  </pre>
                </div>
              </div>
            )}

            <div className="mt-6 flex space-x-3">
              <button
                onClick={() => window.location.reload()}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Reload Page
              </button>
              <button
                onClick={() => window.history.back()}
                className="flex-1 bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
              >
                Go Back
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 