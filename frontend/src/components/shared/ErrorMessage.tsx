import React from 'react';

interface ErrorMessageProps {
  message: string;
  title?: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  type?: 'error' | 'warning' | 'info';
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  title = 'Error',
  onRetry,
  onDismiss,
  type = 'error',
}) => {
  const typeStyles = {
    error: {
      container: 'bg-red-50 border-red-200',
      icon: 'bg-red-100 text-red-600',
      title: 'text-red-900',
      message: 'text-red-700',
      button: 'bg-red-600 hover:bg-red-700',
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-200',
      icon: 'bg-yellow-100 text-yellow-600',
      title: 'text-yellow-900',
      message: 'text-yellow-700',
      button: 'bg-yellow-600 hover:bg-yellow-700',
    },
    info: {
      container: 'bg-blue-50 border-blue-200',
      icon: 'bg-blue-100 text-blue-600',
      title: 'text-blue-900',
      message: 'text-blue-700',
      button: 'bg-blue-600 hover:bg-blue-700',
    },
  };

  const styles = typeStyles[type];

  const getIcon = () => {
    switch (type) {
      case 'error':
        return (
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        );
      case 'warning':
        return (
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        );
      case 'info':
        return (
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        );
    }
  };

  return (
    <div className={`rounded-lg border p-4 ${styles.container}`}>
      <div className="flex items-start">
        <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${styles.icon}`}>
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            {getIcon()}
          </svg>
        </div>

        <div className="ml-3 flex-1">
          <h3 className={`text-sm font-medium ${styles.title}`}>{title}</h3>
          <div className={`mt-2 text-sm ${styles.message}`}>
            <p>{message}</p>
          </div>

          {(onRetry || onDismiss) && (
            <div className="mt-4 flex gap-3">
              {onRetry && (
                <button
                  onClick={onRetry}
                  className={`px-4 py-2 text-sm font-medium text-white rounded-lg transition ${styles.button}`}
                >
                  Try Again
                </button>
              )}
              {onDismiss && (
                <button
                  onClick={onDismiss}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                >
                  Dismiss
                </button>
              )}
            </div>
          )}
        </div>

        {onDismiss && (
          <button
            onClick={onDismiss}
            className="flex-shrink-0 ml-3 text-gray-400 hover:text-gray-500"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;
