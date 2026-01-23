import React, { useState } from 'react';
import './App.css';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      // Add user message
      setMessages([...messages, 
        { text: input, sender: 'user' },
        { text: 'I am an ai chatbot', sender: 'bot' }
      ]);
      setInput('');
    }
  };

  return (
    <div className="App">
      <div className="chatbot-container">
        <h1>Chatbot</h1>
        <div className="messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender}`}>
              {msg.text}
            </div>
          ))}
        </div>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="chat-input"
          />
          <button type="submit">Send</button>
        </form>
      </div>
    </div>
  );
}

export default App;