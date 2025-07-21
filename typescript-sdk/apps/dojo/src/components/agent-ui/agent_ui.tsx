// @ts-nocheck
import React, { useState, useEffect } from 'react';

const AgentTransferUI = ({ args, result, status }) => {
  const [showTransfer, setShowTransfer] = useState(true);
  const [fadeOut, setFadeOut] = useState(false);

  const agentName = args?.agent_name || 'Unknown Agent';

  // Auto-hide after 5 seconds with fade effect
  useEffect(() => {
    const timer = setTimeout(() => {
      // setFadeOut(true);
      // setTimeout(() => setShowTransfer(false), 300);
    }, 5000);

    return () => clearTimeout(timer);
  }, []);

  if (!showTransfer) return null;

  // Format agent name for display
  const formatAgentName = (name) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'executing':
        return (
          <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-500 border-t-transparent"></div>
        );
      case 'complete':
        return (
          <div className="h-5 w-5 bg-green-500 rounded-full flex items-center justify-center">
            <svg className="h-3 w-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        );
      case 'error':
        return (
          <div className="h-5 w-5 bg-red-500 rounded-full flex items-center justify-center">
            <svg className="h-3 w-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        );
      default:
        return (
          <div className="h-5 w-5 bg-blue-500 rounded-full flex items-center justify-center">
            <svg className="h-3 w-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </div>
        );
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'executing':
        return 'border-blue-200 bg-blue-50';
      case 'complete':
        return 'border-green-200 bg-green-50';
      case 'error':
        return 'border-red-200 bg-red-50';
      default:
        return 'border-purple-200 bg-purple-50';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'executing':
        return 'Transferring...';
      case 'complete':
        return 'Transfer Complete';
      case 'error':
        return 'Transfer Failed';
      default:
        return 'Initiating Transfer';
    }
  };

  return (
    <div className={`transition-all duration-300 ${fadeOut ? 'opacity-0 transform translate-y-2' : 'opacity-100'}`}>
      <div className={`flex items-center justify-between p-4 rounded-lg border-2 ${getStatusColor(status)} shadow-sm mb-4 max-w-md`}>
        <div className="flex items-center space-x-3">
          {getStatusIcon(status)}
          <div>
            <div className="text-sm font-medium text-gray-900 flex items-center space-x-2">
              <span className="text-xs bg-purple-100 text-purple-800 px-2 py-0.5 rounded-full font-semibold">
                🤖 AGENT TRANSFER
              </span>
              <span>{getStatusText(status)}</span>
            </div>
            <div className="text-xs text-gray-600">
              Transferring to <span className="font-semibold text-purple-600">{formatAgentName(agentName)}</span>
            </div>
          </div>
        </div>
        
        <button
          onClick={() => {
            setFadeOut(true);
            setTimeout(() => setShowTransfer(false), 300);
          }}
          className="ml-4 p-1 hover:bg-gray-200 rounded-full transition-colors"
        >
          <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      {/* Progress indicator for executing status */}
      {status === 'executing' && (
        <div className="max-w-md mb-4">
          <div className="w-full bg-gray-200 rounded-full h-1">
            <div className="bg-blue-500 h-1 rounded-full animate-pulse" style={{ width: '60%' }}></div>
          </div>
        </div>
      )}

      {/* Additional info panel */}
      <details className="max-w-md">
        <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-800 mb-2">
          Transfer Details
        </summary>
        <div className="bg-gray-50 p-3 rounded text-xs">
          <div className="space-y-1">
            <div><span className="font-medium">Target Agent:</span> {agentName}</div>
            <div><span className="font-medium">Status:</span> {status || 'pending'}</div>
            <div><span className="font-medium">Timestamp:</span> {new Date().toLocaleTimeString()}</div>
            {result && (
              <div><span className="font-medium">Result:</span> {JSON.stringify(result)}</div>
            )}
          </div>
        </div>
      </details>
    </div>
  );
};

// Updated code snippet to replace in your existing file:
// Replace this part in your TransferPortalAssistant component:

/*
useCopilotAction({
  name: "transfer_to_agent",
  parameters: [
    {
      name: "agent_name",
      type: "string",
    }
  ],
  render: ({ args, result, status }) => {
  //  render transfer_to_agent call
  },
});
*/

// With this:
/*
useCopilotAction({
  name: "transfer_to_agent",
  parameters: [
    {
      name: "agent_name",
      type: "string",
    }
  ],
  render: ({ args, result, status }) => {
    return <AgentTransferUI args={args} result={result} status={status} />;
  },
});
*/

export default AgentTransferUI;