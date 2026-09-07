import React from 'react';

interface Props { children: React.ReactNode }
interface State { hasError: boolean; message?: string }

export default class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('RailBlock AI caught a render error:', error, info);
  }

  handleReset = () => {
    this.setState({ hasError: false, message: undefined });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 m-6 text-center bg-signal-red/10 border border-signal-red/30 rounded-panel">
          <p className="text-signal-red font-semibold mb-2">This page hit an unexpected error.</p>
          <p className="text-sm text-slate-500 mb-4">{this.state.message}</p>
          <button
            onClick={this.handleReset}
            className="px-4 py-2 bg-steel text-white rounded-panel text-sm font-medium hover:bg-steel-dark transition-colors"
          >
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
