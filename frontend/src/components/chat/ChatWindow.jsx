import React, { useState } from 'react';


const ChatWindow = () => {
    const [messages, setMessages] = useState([]);


    const handleSendMessage = (message) => {
        setMessages([...messages, { text: message, sender: 'user' }]);
        
        // Removed mock invoice intent detection.
        setMessages(prev => [...prev, { text: "I am a helpful AI.", sender: 'ai' }]);
    };

    return (
        <div className="chat-container">
            <div className="chat-window">
                    <div className="messages">
                        {messages.map((m, i) => (
                            <div key={i} className={`message ${m.sender}`}>
                                {m.text}
                            </div>
                        ))}
                    </div>
                    <div className="input-area">
                        <input 
                            type="text" 
                            placeholder="Type a message..." 
                            onKeyDown={(e) => {
                                if(e.key === 'Enter') {
                                    handleSendMessage(e.target.value);
                                    e.target.value = '';
                                }
                            }} 
                        />
                    </div>
                </div>
        </div>
    );
};

export default ChatWindow;
