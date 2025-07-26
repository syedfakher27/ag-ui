// @ts-nocheck
"use client";
import React, { useState, useEffect } from "react";
import { X, Plus, Mail, Send, User } from 'lucide-react';

interface Recipient {
  name: string;
  email: string;
}

interface EmailApprovalArgs {
  recipients: Recipient[];
  conversation_summary: string;
}

interface EmailApprovalComponentProps {
  args: EmailApprovalArgs;
  respond: (response: { 
    accepted: boolean; 
    message?: string; 
    modified_summary?: string; 
    recipients?: Recipient[] 
  }) => void;
  status: string;
}

const MultiRecipientEmailApprovalComponent: React.FC<EmailApprovalComponentProps> = ({
  args,
  respond,
  status,
}) => {
  const [emailDetails, setEmailDetails] = useState({
    recipients: [] as Recipient[],
    conversation_summary: "",
  });

  const [accepted, setAccepted] = useState<boolean | null>(null);
  const [sendingStatus, setSendingStatus] = useState<string>("");
  const [isSending, setIsSending] = useState<boolean>(false);

  // Update state whenever args change
  useEffect(() => {
    console.log('Args received:', args);
    if (args && args.recipients) {
      setEmailDetails({
        recipients: args.recipients || [],
        conversation_summary: args.conversation_summary || "",
      });
    }
  }, [args]);

  const handleSummaryChange = (value: string) => {
    setEmailDetails(prev => ({
      ...prev,
      conversation_summary: value,
    }));
  };

  const handleRecipientChange = (index: number, field: keyof Recipient, value: string) => {
    setEmailDetails(prev => ({
      ...prev,
      recipients: prev.recipients.map((recipient, i) =>
        i === index ? { ...recipient, [field]: value } : recipient
      ),
    }));
  };

  const addRecipient = () => {
    setEmailDetails(prev => ({
      ...prev,
      recipients: [...prev.recipients, { name: "", email: "" }],
    }));
  };

  const removeRecipient = (index: number) => {
    setEmailDetails(prev => ({
      ...prev,
      recipients: prev.recipients.filter((_, i) => i !== index),
    }));
  };

  const handleApprove = async () => {
    if (!respond) {
      console.error('No respond function available');
      return;
    }

    setIsSending(true);
    setSendingStatus("Preparing to send emails...");

    // Filter out recipients with empty emails
    const validRecipients = emailDetails.recipients.filter(r => r.email.trim());
    
    if (validRecipients.length === 0) {
      console.log('No valid recipients found');
      setIsSending(false);
      respond({
        accepted: false,
        message: "No valid recipients found. Please add at least one recipient with an email address.",
        recipients: []
      });
      return;
    }

    setSendingStatus(`Sending emails to ${validRecipients.length} recipients...`);
    console.log(`Starting batch email sending to ${validRecipients.length} recipients`);

    try {
      // Prepare batch payload with all recipients (as objects with name and email)
      const batchEmailPayload = {
        sender_email: "no-reply@disearch.ai",
        sender_username: "SLAM",
        recipients: validRecipients.map(recipient => ({
          name: recipient.name,
          email: recipient.email
        })), // Send array of objects with name and email
        body: emailDetails.conversation_summary
      };

      console.log('Sending batch email payload:', batchEmailPayload);

      const response = await fetch('https://us-central1-slamsportsai.cloudfunctions.net/sendgrid-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(batchEmailPayload)
      });

      if (response.ok) {
        const responseData = await response.json();
        console.log('Batch email response:', responseData);

        // Process the CF response
        const { message, results, successful_sends, total_recipients } = responseData;
        
        // Create detailed results message
        const detailedResults = results.map((result: any) => {
          const recipientName = validRecipients.find(r => r.email === result.recipient)?.name || result.recipient;
          return result.status === 'success' 
            ? `✓ ${recipientName}: ${result.message}`
            : `✗ ${recipientName}: ${result.message}`;
        }).join('\n');

        const finalMessage = `${message}\n\nDetailed Results:\n${detailedResults}`;
        
        setSendingStatus(finalMessage);
        setAccepted(true);
        setIsSending(false);
        console.log('Final batch email result:', finalMessage);

        // IMPORTANT: Call respond to complete the CopilotKit action
        respond({
          accepted: true,
          message: finalMessage,
          recipients: validRecipients,
          batch_results: responseData
        });

      } else {
        const errorText = await response.text();
        const errorMessage = `Failed to send batch emails. Status: ${response.status}\nError: ${errorText}`;
        console.error(errorMessage);
        
        setSendingStatus(errorMessage);
        setAccepted(false);
        setIsSending(false);

        respond({
          accepted: false,
          message: errorMessage,
          recipients: validRecipients
        });
      }

    } catch (error) {
      const errorMessage = `Network error occurred while sending batch emails: ${error}`;
      console.error(errorMessage);
      
      setSendingStatus(errorMessage);
      setAccepted(false);
      setIsSending(false);

      respond({
        accepted: false,
        message: errorMessage,
        recipients: validRecipients
      });
    }
  };

  const handleReject = () => {
    console.log('User rejected email sending');
    if (!respond) {
      console.error('No respond function available');
      return;
    }
    
    setAccepted(false);
    respond({ 
      accepted: false,
      message: "Email cancelled by user"
    });
  };

  // Early return with better debugging
  if (!args) {
    console.log('No args provided to EmailApprovalComponent');
    return <div className="p-4 text-red-500">No email data provided</div>;
  }

  // if (!respond) {
  //   console.log('No respond function provided to EmailApprovalComponent');
  //   return <div className="p-4 text-red-500">No respond function available</div>;
  // }

  console.log('Rendering with emailDetails:', emailDetails);
  console.log('Component status:', status);
  // console.log('Respond function available:', !!respond);

  return (
    <div className="flex flex-col gap-4 w-full max-w-4xl bg-white rounded-lg p-6 mb-4 border border-gray-200 shadow-sm">
      <div className="text-black space-y-4">
        {/* Header */}
        <div className="flex items-center gap-3 pb-4 border-b border-gray-200">
          <div className="p-2 bg-blue-600 rounded-lg">
            <Mail className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-800">📧 Review & Send Email Summary</h2>
            <p className="text-sm text-gray-600">Send conversation summary to multiple recipients</p>
          </div>
        </div>

        {/* From Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">From</label>
          <div className="px-4 py-3 bg-gray-100 border border-gray-300 rounded-md flex items-center gap-2">
            <User className="w-4 h-4 text-gray-500" />
            <span>no-reply@disearch.ai (SLAM)</span>
          </div>
        </div>

        {/* Recipients Section */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-medium text-gray-700">
              Recipients ({emailDetails.recipients.length})
            </label>
            <button
              onClick={addRecipient}
              className="flex items-center gap-1 px-3 py-1 text-blue-600 hover:bg-blue-50 rounded-md transition-colors text-sm"
              disabled={accepted !== null}
            >
              <Plus className="w-4 h-4" />
              Add Recipient
            </button>
          </div>

          <div className="space-y-3 max-h-60 overflow-y-auto">
            {emailDetails.recipients.map((recipient, index) => (
              <div key={index} className="grid grid-cols-1 md:grid-cols-2 gap-3 p-3 bg-gray-50 rounded-md">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Name</label>
                  <input
                    type="text"
                    value={recipient.name}
                    onChange={(e) => handleRecipientChange(index, "name", e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Recipient name"
                    disabled={accepted !== null}
                  />
                </div>
                <div className="flex gap-2">
                  <div className="flex-1">
                    <label className="block text-xs font-medium text-gray-600 mb-1">Email *</label>
                    <input
                      type="email"
                      value={recipient.email}
                      onChange={(e) => handleRecipientChange(index, "email", e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="recipient@example.com"
                      disabled={accepted !== null}
                      required
                    />
                  </div>
                  <button
                    onClick={() => removeRecipient(index)}
                    className="mt-6 p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
                    disabled={accepted !== null}
                    title="Remove recipient"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}

            {emailDetails.recipients.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Mail className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p className="text-sm">No recipients added yet</p>
                <button
                  onClick={addRecipient}
                  className="mt-2 text-blue-600 hover:text-blue-700 text-sm"
                  disabled={accepted !== null}
                >
                  Add your first recipient
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Conversation Summary */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Conversation Summary</label>
          <textarea
            value={emailDetails.conversation_summary}
            onChange={(e) => handleSummaryChange(e.target.value)}
            rows={8}
            className="w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
            placeholder="Review and edit the conversation summary..."
            disabled={accepted !== null}
          />
        </div>

        {/* Debug Info - helpful for troubleshooting */}
        {process.env.NODE_ENV === 'development' && (
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md text-xs">
            <strong>Debug Info:</strong>
            <div>Status: {status}</div>
            <div>Recipients count: {emailDetails.recipients.length}</div>
            <div>Valid recipients: {emailDetails.recipients.filter(r => r.email.trim()).length}</div>
            <div>Respond function: {respond ? 'Available' : 'Missing'}</div>
            <div>Accepted state: {accepted?.toString()}</div>
          </div>
        )}

        {/* Sending Status */}
        {accepted === true && sendingStatus && (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
            <div className="flex items-start gap-3">
              {sendingStatus.includes('successfully') || sendingStatus.includes('completed') ? (
                <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <div className="w-3 h-3 bg-white rounded-full"></div>
                </div>
              ) : sendingStatus.includes('Failed') || sendingStatus.includes('error') ? (
                <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <div className="w-3 h-3 bg-white rounded-full"></div>
                </div>
              ) : (
                <div className="animate-spin w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full flex-shrink-0"></div>
              )}
              <div className="flex-1">
                <p className="text-sm font-medium text-blue-800 mb-2">Batch Email Status</p>
                <div className="text-xs text-blue-700 whitespace-pre-wrap bg-white p-3 rounded border max-h-48 overflow-y-auto">
                  {sendingStatus}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      {accepted === null && (
        <div className="flex justify-end space-x-4 pt-4 border-t border-gray-200">
          <button
            className="flex items-center gap-2 px-6 py-2 rounded-lg bg-gray-200 text-gray-800 hover:bg-gray-300 transition-colors"
            onClick={handleReject}
          >
            Cancel
          </button>
          <button
            className="flex items-center gap-2 px-6 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
            onClick={handleApprove}
            disabled={emailDetails.recipients.filter(r => r.email.trim()).length === 0}
            onMouseDown={() => console.log('Send button clicked!')}
          >
            <Send className="w-4 h-4" />
            Send to {emailDetails.recipients.filter(r => r.email.trim()).length} Recipients
          </button>
        </div>
      )}

      {/* Status Feedback */}
      {accepted !== null && accepted === false && (
        <div className="flex justify-end">
          <div className="px-4 py-2 rounded bg-red-100 text-red-800">
            ✗ Cancelled
          </div>
        </div>
      )}
    </div>
  );
};

export default MultiRecipientEmailApprovalComponent;