import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, X, Minimize2, Maximize2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './ChatbotSidebar.css';

const suggestedPrompts = [
    "What's the best location for a coffee shop?",
    "Analyze foot traffic in Sector 1",
    "Compare income levels across districts",
    "Find areas with low competition"
];

const initialMessages = [
    {
        id: 1,
        type: 'bot',
        text: "👋 Hello! I'm your AI location consultant. Ask me anything about retail locations in Bucharest!",
        timestamp: new Date()
    }
];

const ChatbotSidebar = () => {
    const [messages, setMessages] = useState(initialMessages);
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = () => {
        if (!inputValue.trim()) return;

        const userMessage = {
            id: messages.length + 1,
            type: 'user',
            text: inputValue,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsTyping(true);

        // Simulate bot response
        setTimeout(() => {
            const botMessage = {
                id: messages.length + 2,
                type: 'bot',
                text: "I'm analyzing the data for your query. In a production environment, I would provide detailed insights about locations, demographics, and strategic recommendations based on your specific needs.",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, botMessage]);
            setIsTyping(false);
        }, 1500);
    };

    const handlePromptClick = (prompt) => {
        setInputValue(prompt);
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className={`chatbot-sidebar ${isMinimized ? 'minimized' : ''}`}>
            <div className="chatbot-header glass">
                <div className="header-content">
                    <div className="header-icon">
                        <Sparkles size={20} color="#f97316" />
                    </div>
                    <div className="header-text">
                        <h3>Strategy Assistant</h3>
                        <p className="status">
                            <span className="status-dot"></span>
                            Online
                        </p>
                    </div>
                </div>
                <button
                    className="minimize-btn"
                    onClick={() => setIsMinimized(!isMinimized)}
                >
                    {isMinimized ? <Maximize2 size={18} /> : <Minimize2 size={18} />}
                </button>
            </div>

            <AnimatePresence>
                {!isMinimized && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="chatbot-content"
                    >
                        {/* Suggested Prompts */}
                        {messages.length === 1 && (
                            <div className="suggested-prompts">
                                <p className="prompts-title">Try asking:</p>
                                <div className="prompts-grid">
                                    {suggestedPrompts.map((prompt, index) => (
                                        <button
                                            key={index}
                                            className="prompt-btn glass"
                                            onClick={() => handlePromptClick(prompt)}
                                        >
                                            {prompt}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Messages */}
                        <div className="messages-container">
                            {messages.map((message) => (
                                <motion.div
                                    key={message.id}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className={`message ${message.type}`}
                                >
                                    <div className="message-content">
                                        {message.text}
                                    </div>
                                </motion.div>
                            ))}

                            {isTyping && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="message bot"
                                >
                                    <div className="message-content typing">
                                        <span className="typing-dot"></span>
                                        <span className="typing-dot"></span>
                                        <span className="typing-dot"></span>
                                    </div>
                                </motion.div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input */}
                        <div className="chatbot-input">
                            <div className="input-wrapper glass">
                                <textarea
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Ask about locations, strategies..."
                                    rows="1"
                                />
                                <button
                                    className="send-btn"
                                    onClick={handleSend}
                                    disabled={!inputValue.trim()}
                                >
                                    <Send size={18} />
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default ChatbotSidebar;
