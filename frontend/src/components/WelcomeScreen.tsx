import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { ApiClientRest } from '../rest/api_client_rest';
import { createChatApi } from '../rest/modules/chat';
import { addChatFromApi, setActiveChat } from '../services/chatStorage';

interface WelcomeScreenProps {
  onChatCreated: (chatId: string) => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onChatCreated }) => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const apiClient = useMemo(() => new ApiClientRest(), []);
  const chatApi = useMemo(() => createChatApi(apiClient), [apiClient]);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent, messageOverride?: string) => {
    e.preventDefault();

    const message = messageOverride || input;
    if (!message.trim()) return;

    setIsLoading(true);

    try {
      // Create a new chat
      const chat = await chatApi.createChat();

      // Store in session storage
      addChatFromApi(chat, message);
      setActiveChat(chat.id);

      // Send the initial message and await the response
      await chatApi.sendMessage(chat.id, message);
      
      // Now that the message has been sent and response received,
      // navigate to the chat page
      navigate(`/chat/${chat.id}`);
      onChatCreated(chat.id);
    } catch (error) {
      alert('Failed to create chat. Please try again.');
      setIsLoading(false);
    }
  };

  // Sample questions to help users get started
  const sampleQuestions = [
    "What is your return policy?",
    "How do I reset my device?",
    "My device is emitting a loud beeping noise, what should I do?",
    "Can I schedule a service appointment?",
    "Do you sell replacement batteries?",
    "What does Error E9-VORTEX mean?",
    "Can I talk to someone on the phone?",
    "Why is there steam coming out of the side vents?",
  ];

  const startWithSampleQuestion = (question: string) => {
    setInput(question);

    // Create a synthetic form event and pass the question directly
    const event = new Event('submit') as any;
    handleSubmit(event, question);
  };

  return (
    <div className="flex flex-col items-center justify-center h-full max-w-5xl mx-auto p-4">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-4">Customer Support Assistant</h1>
        <p className="text-xl opacity-80">
          How can I help you today?
        </p>
      </div>

      <form id="welcome-form" className="self-stretch mb-6" onSubmit={handleSubmit}>
        <div className="form-control w-full">
          <div className="input-group flex">
            <input
              type="text"
              placeholder="Ask a question..."
              className="input input-bordered flex-1"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isLoading || !input.trim()}
            >
              {isLoading ?
                <span className="loading loading-spinner"></span> :
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              }
            </button>
          </div>
        </div>
      </form>

      <div className="w-full">
        <h2 className="text-lg font-medium mb-4">Try asking about:</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {sampleQuestions.map((question, index) => (
            <button
              key={index}
              className="btn btn-outline btn-md text-left"
              onClick={() => startWithSampleQuestion(question)}
              disabled={isLoading}
            >
              {question}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;
