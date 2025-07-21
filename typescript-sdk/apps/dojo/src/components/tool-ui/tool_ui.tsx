// @ts-nocheck
import React, { useState, useEffect } from 'react';

const ToolExecutionUI = ({ toolName, args, result, status }) => {
  const [showTool, setShowTool] = useState(true);
  const [fadeOut, setFadeOut] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  // Auto-hide after 8 seconds with fade effect (longer than agent transfer)
  useEffect(() => {
    const timer = setTimeout(() => {
      // setFadeOut(true);
      // setTimeout(() => setShowTool(false), 300);
    }, 8000);

    return () => clearTimeout(timer);
  }, []);

  if (!showTool) return null;

  // Format tool name for display
  const formatToolName = (name) => {
    if (!name) return 'Unknown Tool';
    return name
      .replace(/_/g, ' ')
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, str => str.toUpperCase())
      .trim();
  };

  const getToolIcon = (toolName) => {
    const name = toolName?.toLowerCase() || '';
    
    if (name.includes('search') || name.includes('query')) {
      return (
        <svg className="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      );
    }
    
    if (name.includes('fetch') || name.includes('get') || name.includes('retrieve')) {
      return (
        <svg className="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
        </svg>
      );
    }
    
    if (name.includes('filter') || name.includes('sort')) {
      return (
        <svg className="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.707A1 1 0 013 7V4z" />
        </svg>
      );
    }
    
    if (name.includes('shortlist') || name.includes('list')) {
      return (
        <svg className="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
      );
    }
    
    // Default tool icon
    return (
      <svg className="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    );
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'executing':
        return (
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
        );
      case 'complete':
        return (
          <div className="h-4 w-4 bg-green-500 rounded-full flex items-center justify-center">
            <svg className="h-2 w-2 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        );
      case 'error':
        return (
          <div className="h-4 w-4 bg-red-500 rounded-full flex items-center justify-center">
            <svg className="h-2 w-2 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        );
      default:
        return (
          <div className="h-4 w-4 bg-blue-500 rounded-full flex items-center justify-center">
            <svg className="h-2 w-2 text-white" fill="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="3" />
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
        return 'border-indigo-200 bg-indigo-50';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'executing':
        return 'Executing...';
      case 'complete':
        return 'Completed';
      case 'error':
        return 'Failed';
      default:
        return 'Running';
    }
  };

  const truncateString = (str, maxLength = 100) => {
    if (typeof str !== 'string') return JSON.stringify(str);
    return str.length > maxLength ? str.substring(0, maxLength) + '...' : str;
  };

  const formatJson = (obj) => {
    try {
      return JSON.stringify(obj, null, 2);
    } catch (e) {
      return String(obj);
    }
  };

  return (
    <div className={`transition-all duration-300 ${fadeOut ? 'opacity-0 transform translate-y-2' : 'opacity-100'}`}>
      <div className={`rounded-lg border-2 ${getStatusColor(status)} shadow-sm mb-4 max-w-2xl`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 bg-indigo-500 rounded-lg flex items-center justify-center">
              {getToolIcon(toolName)}
            </div>
            <div>
              <div className="text-sm font-medium text-gray-900 flex items-center space-x-2">
                <span className="text-xs bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded-full font-semibold">
                  🔧 TOOL CALL
                </span>
                <span>{formatToolName(toolName)}</span>
                {getStatusIcon(status)}
              </div>
              <div className="text-xs text-gray-600">
                {getStatusText(status)}
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1 hover:bg-gray-200 rounded-full transition-colors text-gray-500 hover:text-gray-700"
              title="Toggle details"
            >
              <svg 
                className={`h-4 w-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <button
              onClick={() => {
                setFadeOut(true);
                setTimeout(() => setShowTool(false), 300);
              }}
              className="p-1 hover:bg-gray-200 rounded-full transition-colors"
            >
              <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Progress indicator for executing status */}
        {status === 'executing' && (
          <div className="px-4 pb-2">
            <div className="w-full bg-gray-200 rounded-full h-1">
              <div className="bg-indigo-500 h-1 rounded-full animate-pulse" style={{ width: '70%' }}></div>
            </div>
          </div>
        )}

        {/* Expandable content */}
        {isExpanded && (
          <div className="border-t border-gray-200 bg-white bg-opacity-50">
            {/* Arguments */}
            {args && Object.keys(args).length > 0 && (
              <div className="p-4 border-b border-gray-100">
                <h4 className="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">Arguments</h4>
                <div className="bg-gray-50 rounded p-3 text-xs font-mono">
                  {Object.keys(args).length <= 3 ? (
                    <div className="space-y-1">
                      {Object.entries(args).map(([key, value]) => (
                        <div key={key} className="flex">
                          <span className="text-purple-600 font-medium">{key}:</span>
                          <span className="ml-2 text-gray-800">{truncateString(value, 150)}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <pre className="whitespace-pre-wrap">{formatJson(args)}</pre>
                  )}
                </div>
              </div>
            )}

            {/* Results */}
            {result && (
              <div className="p-4">
                <h4 className="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">Result</h4>
                <div className="bg-gray-50 rounded p-3 text-xs">
                  {typeof result === 'string' ? (
                    <p className="text-gray-800">{truncateString(result, 300)}</p>
                  ) : Array.isArray(result) ? (
                    <div>
                      <span className="text-indigo-600 font-medium">Array ({result.length} items)</span>
                      {result.length <= 5 && (
                        <div className="mt-2 space-y-1">
                          {result.slice(0, 3).map((item, index) => (
                            <div key={index} className="pl-4 border-l-2 border-gray-300">
                              {truncateString(item, 100)}
                            </div>
                          ))}
                          {result.length > 3 && (
                            <div className="pl-4 text-gray-500 italic">... and {result.length - 3} more</div>
                          )}
                        </div>
                      )}
                    </div>
                  ) : (
                    <pre className="whitespace-pre-wrap font-mono text-gray-800">{formatJson(result)}</pre>
                  )}
                </div>
              </div>
            )}

            {/* Metadata */}
            <div className="px-4 pb-4 border-t border-gray-100 bg-gray-25">
              <div className="flex justify-between items-center text-xs text-gray-500 pt-3">
                <span>Tool: {toolName}</span>
                <span>Executed: {new Date().toLocaleTimeString()}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ToolExecutionUI;