import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, StopCircle, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const MCPChat = () => {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: "Hello! I'm **ThunderX AI**. I can help you investigate network threats, analyze logs, or answer questions about your security posture. How can I help you today?" }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [connectionError, setConnectionError] = useState(false);
    const messagesEndRef = useRef(null);

    // Auto-scroll to bottom
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);
        setConnectionError(false);

        try {
            // Note: In development, we might not have the API proxy set up in package.json yet
            // Assuming API is at localhost:8000 (mcp-ai-service)
            // Ideally we use a relative path like '/api/query' and nginx handles proxying

            const response = await fetch('http://localhost:8000/query/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: input })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            // Assuming data structure from phase 5: { answer: "...", intent: "..." }

            const assistantMessage = {
                role: 'assistant',
                content: data.answer || "Processing complete."
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Error:', error);
            // Fallback for demo if backend not running
            const errorMsg = {
                role: 'assistant',
                content: `⚠️ **Connection Error**: I couldn't reach the AI service.\n\n*Debug Info*: Ensure \`mcp-ai-service\` is running on port 8000.`
            };
            setMessages(prev => [...prev, errorMsg]);
            setConnectionError(true);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)] bg-thunder-800 rounded-xl shadow-2xl border border-thunder-700 overflow-hidden">
            {/* Header */}
            <div className="bg-thunder-900 p-4 border-b border-thunder-700 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                    <div className="bg-thunder-accent/20 p-2 rounded-lg">
                        <Sparkles className="w-5 h-5 text-thunder-accent" />
                    </div>
                    <div>
                        <h2 className="font-semibold text-white">AI Investigator</h2>
                        <p className="text-xs text-slate-400 flex items-center">
                            <span className={`w-2 h-2 rounded-full mr-2 ${connectionError ? 'bg-red-500' : 'bg-green-500'}`}></span>
                            {connectionError ? 'Offline' : 'Online'}
                        </p>
                    </div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
                {messages.map((msg, index) => (
                    <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`flex max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : 'flex-row'} items-start space-x-3`}>

                            {/* Avatar */}
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'assistant' ? 'bg-indigo-600' : 'bg-slate-600'
                                }`}>
                                {msg.role === 'assistant' ? <Bot size={18} className="text-white" /> : <User size={18} className="text-white" />}
                            </div>

                            {/* Bubble */}
                            <div className={`p-4 rounded-2xl ${msg.role === 'user'
                                    ? 'bg-thunder-accent text-white rounded-tr-none'
                                    : 'bg-thunder-700 text-slate-200 rounded-tl-none border border-thunder-600'
                                }`}>
                                <div className="prose prose-invert prose-sm max-w-none">
                                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="flex items-start space-x-3">
                            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center">
                                <Bot size={18} className="text-white" />
                            </div>
                            <div className="bg-thunder-700 px-4 py-3 rounded-2xl rounded-tl-none border border-thunder-600 flex items-center space-x-2">
                                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-100"></div>
                                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-200"></div>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 bg-thunder-900 border-t border-thunder-700">
                <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask ThunderX to investigate..."
                        className="w-full bg-thunder-800 text-white placeholder-slate-500 border border-thunder-600 rounded-xl pl-4 pr-12 py-4 focus:outline-none focus:border-thunder-accent focus:ring-1 focus:ring-thunder-accent transition-all shadow-lg"
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        className="absolute right-2 top-2 p-2 bg-thunder-accent hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                    >
                        {isLoading ? <StopCircle size={20} /> : <Send size={20} />}
                    </button>
                    <p className="text-xs text-center text-slate-500 mt-2">
                        AI can make mistakes. Verify critical findings.
                    </p>
                </form>
            </div>
        </div>
    );
};

export default MCPChat;
