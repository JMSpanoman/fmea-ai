import React, { useState } from 'react';
import { Drawer } from '../ui/Drawer';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';

interface AiAssistantPanelProps {
  isOpen: boolean;
  onClose: () => void;
  context?: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const AiAssistantPanel: React.FC<AiAssistantPanelProps> = ({
  isOpen,
  onClose,
  context = '',
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const getContextTitle = () => {
    if (context.includes('fmea') || context.includes('dfmea')) return 'AI Assistant – Risk';
    if (context.includes('design')) return 'AI Assistant – Design Controls';
    if (context.includes('capa')) return 'AI Assistant – CAPA';
    if (context.includes('document')) return 'AI Assistant – Documents';
    return 'AI Assistant';
  };

  const quickActions = [
    { label: 'Suggest FMEA row', action: 'suggest-fmea' },
    { label: 'Summarize document', action: 'summarize-doc' },
    { label: 'Explain risk scores', action: 'explain-risks' },
    { label: 'Analyze traceability', action: 'analyze-trace' },
  ];

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I understand you need help with this. Let me assist you...',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title={getContextTitle()}
      position="right"
      width="420px"
    >
      <div className="flex flex-col h-full">
        {/* Context Header */}
        <div className="mb-4 p-3 bg-surface-secondary rounded-lg border border-border">
          <p className="text-xs text-text-secondary mb-1">Context</p>
          <p className="text-sm text-text-primary">{context || 'General'}</p>
        </div>

        {/* Quick Actions */}
        <div className="mb-4">
          <p className="text-xs text-text-secondary mb-2">Quick Actions</p>
          <div className="flex flex-wrap gap-2">
            {quickActions.map((action) => (
              <button
                key={action.action}
                onClick={() => setInput(action.label)}
                className="px-3 py-1.5 text-xs bg-surface-secondary hover:bg-surface-primary border border-border rounded-lg text-text-secondary hover:text-text-primary transition-smooth"
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto mb-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-text-secondary text-sm py-8">
              <span className="text-2xl mb-2 block">✨</span>
              <p>Start a conversation with AI</p>
              <p className="text-xs mt-1">Ask questions or use quick actions</p>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`
                flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}
              `}
            >
              <div
                className={`
                  max-w-[80%] px-4 py-2 rounded-lg
                  ${message.role === 'user'
                    ? 'bg-primary text-gray-900'
                    : 'bg-surface-secondary text-text-primary border border-border'
                  }
                `}
              >
                <p className="text-sm">{message.content}</p>
                <p className="text-xs opacity-70 mt-1">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-surface-secondary border border-border px-4 py-2 rounded-lg">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-text-secondary rounded-full animate-bounce" />
                  <span className="w-2 h-2 bg-text-secondary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <span className="w-2 h-2 bg-text-secondary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask AI..."
            className="flex-1"
          />
          <Button onClick={handleSend} disabled={isLoading || !input.trim()}>
            Send
          </Button>
        </div>
      </div>
    </Drawer>
  );
};

