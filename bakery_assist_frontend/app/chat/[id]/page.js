"use client"; // Required for hooks like useState, useEffect, useRef, useParams

import { useState, useEffect, useRef, useCallback } from "react";
import { useParams } from "next/navigation";
import { SendHorizonal } from "lucide-react"; // Using lucide-react for icons

// --- Configuration ---
// Define the API endpoint where messages will be sent
const CHAT_API_BASE_ENDPOINT = "http://127.0.0.1:5000/api/chat";

// --- Helper Components ---

// Message Bubble Component - MODIFIED
function MessageBubble({ message }) {
  const isUser = message.sender === "user";
  return (
    <div className={`flex mb-4 ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        // Added whitespace-pre-wrap to render newlines correctly
        className={`py-2 px-4 rounded-xl max-w-md lg:max-w-lg xl:max-w-xl break-words whitespace-pre-wrap ${
          isUser
            ? "bg-blue-600 text-white rounded-br-none"
            : "bg-gray-200 text-gray-800 rounded-bl-none"
        }`}
      >
        {message.text}
      </div>
    </div>
  );
}

// Loading Indicator Component (Unchanged)
function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4">
      <div className="py-2 px-4 rounded-xl bg-gray-200 text-gray-500 rounded-bl-none animate-pulse">
        <div className="flex space-x-1 items-center h-5">
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></span>
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></span>
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-300"></span>
        </div>
      </div>
    </div>
  );
}

// --- Main Chat Page Component ---

export default function ChatPage() {
  const params = useParams();
  const customerId = params.id;

  const [messages, setMessages] = useState([
    { id: "init", sender: "bot", text: `Hello! How can I help you today?` },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Function to handle sending a message - MODIFIED
  const handleSendMessage = useCallback(async () => {
    const trimmedInput = inputValue.trim();
    if (!trimmedInput || isLoading || !customerId) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: trimmedInput,
    };

    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInputValue("");
    setIsLoading(true);
    setError(null);

    try {
      const apiUrlWithParam = `${CHAT_API_BASE_ENDPOINT}?customer_number=${encodeURIComponent(
        customerId
      )}`;

      const response = await fetch(apiUrlWithParam, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: trimmedInput,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error ||
            `API Error: ${response.status} ${response.statusText}`
        );
      }

      const data = await response.json();

      // --- MODIFIED: Check for 'reply' field instead of 'response' ---
      if (!data || typeof data.reply !== "string") {
        // Updated check
        throw new Error(
          "Invalid response format received from the server (expected 'reply' field)." // Updated error message
        );
      }

      const botMessage = {
        id: `bot-${Date.now()}`,
        sender: "bot",
        // --- MODIFIED: Use data.reply ---
        text: data.reply, // Use the 'reply' field from the JSON
      };

      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (err) {
      console.error("Failed to send message or get response:", err);
      setError(err.message || "An unexpected error occurred.");
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          id: `err-${Date.now()}`,
          sender: "bot",
          text: `Error: ${err.message}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [inputValue, isLoading, customerId]);

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  if (!customerId) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-red-500">Error: Customer ID not found in URL.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 via-stone-50 to-gray-100">
      <header className="bg-white border-b border-gray-200 p-4 shadow-sm sticky top-0 z-10">
        <h1 className="text-xl font-semibold text-gray-800 text-center">
          Agentic AI ChatBot for Customer: {customerId}
        </h1>
      </header>

      <div className="flex-grow overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isLoading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="p-2 text-center text-red-600 bg-red-100 border-t border-red-200">
          {error}
        </div>
      )}

      <div className="bg-white border-t border-gray-200 p-4 sticky bottom-0">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            className="flex-grow px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-150 ease-in-out"
            disabled={isLoading}
            aria-label="Chat message input"
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || inputValue.trim() === ""}
            className={`p-2 rounded-full text-white transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
              isLoading || inputValue.trim() === ""
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700"
            }`}
            aria-label="Send message"
          >
            <SendHorizonal size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}

// "use client"; // Required for hooks like useState, useEffect, useRef, useParams

// import { useState, useEffect, useRef, useCallback } from "react";
// import { useParams } from "next/navigation";
// import { SendHorizonal } from "lucide-react"; // Using lucide-react for icons

// // --- Configuration ---
// // Define the API endpoint where messages will be sent
// const CHAT_API_BASE_ENDPOINT = "http://127.0.0.1:5000/api/chat";

// // --- Helper Components ---

// // Message Bubble Component
// function MessageBubble({ message }) {
//   const isUser = message.sender === "user";
//   return (
//     <div className={`flex mb-4 ${isUser ? "justify-end" : "justify-start"}`}>
//       <div
//         className={`py-2 px-4 rounded-xl max-w-md lg:max-w-lg xl:max-w-xl break-words ${
//           isUser
//             ? "bg-blue-600 text-white rounded-br-none"
//             : "bg-gray-200 text-gray-800 rounded-bl-none"
//         }`}
//       >
//         {message.text}
//       </div>
//     </div>
//   );
// }

// // Loading Indicator Component
// function TypingIndicator() {
//   return (
//     <div className="flex justify-start mb-4">
//       <div className="py-2 px-4 rounded-xl bg-gray-200 text-gray-500 rounded-bl-none animate-pulse">
//         <div className="flex space-x-1 items-center h-5">
//           <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></span>
//           <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></span>
//           <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-300"></span>
//         </div>
//       </div>
//     </div>
//   );
// }

// // --- Main Chat Page Component ---

// export default function ChatPage() {
//   const params = useParams();
//   const customerId = params.id;

//   const [messages, setMessages] = useState([
//     // Optional: Start with a welcome message from the bot
//     { id: "init", sender: "bot", text: `Hello! How can I help you today?` },
//   ]);
//   const [inputValue, setInputValue] = useState("");
//   const [isLoading, setIsLoading] = useState(false);
//   const [error, setError] = useState(null);

//   const messagesEndRef = useRef(null); // Ref for auto-scrolling

//   // Function to scroll to the bottom of the messages list
//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   };

//   // Effect to scroll down when messages change
//   useEffect(() => {
//     scrollToBottom();
//   }, [messages]); // Dependency array includes messages

//   // Function to handle sending a message
//   const handleSendMessage = useCallback(async () => {
//     const trimmedInput = inputValue.trim();
//     if (!trimmedInput || isLoading) return; // Don't send empty or while loading

//     const userMessage = {
//       id: `user-${Date.now()}`, // Simple unique ID
//       sender: "user",
//       text: trimmedInput,
//     };

//     // Optimistically update UI with user message
//     setMessages((prevMessages) => [...prevMessages, userMessage]);
//     setInputValue(""); // Clear input field
//     setIsLoading(true); // Set loading state
//     setError(null); // Clear previous errors

//     try {
//       // --- Construct the API URL with the query parameter ---
//       const apiUrlWithParam = `${CHAT_API_BASE_ENDPOINT}?customer_number=${encodeURIComponent(
//         customerId
//       )}`;
//       // Using encodeURIComponent is good practice for URL parameters

//       // Send message to the backend API
//       const response = await fetch(apiUrlWithParam, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({
//           message: trimmedInput,
//         }),
//       });

//       if (!response.ok) {
//         // Handle HTTP errors
//         const errorData = await response.json().catch(() => ({})); // Try to parse error details
//         throw new Error(
//           errorData.error ||
//             `API Error: ${response.status} ${response.statusText}`
//         );
//       }

//       const data = await response.json();

//       // Ensure the response has the expected format
//       if (!data || typeof data.response !== "string") {
//         throw new Error("Invalid response format received from the server.");
//       }

//       const botMessage = {
//         id: `bot-${Date.now()}`, // Simple unique ID
//         sender: "bot",
//         text: data.response, // Assuming the API returns { response: "..." }
//       };

//       // Update UI with bot response
//       setMessages((prevMessages) => [...prevMessages, botMessage]);
//     } catch (err) {
//       console.error("Failed to send message or get response:", err);
//       setError(err.message || "An unexpected error occurred.");
//       // Optionally add an error message to the chat
//       setMessages((prevMessages) => [
//         ...prevMessages,
//         {
//           id: `err-${Date.now()}`,
//           sender: "bot",
//           text: `Error: ${err.message}`,
//         },
//       ]);
//     } finally {
//       setIsLoading(false); // Reset loading state
//     }
//   }, [inputValue, isLoading, customerId]); // Dependencies for useCallback

//   // Handle Enter key press in input field
//   const handleKeyDown = (event) => {
//     if (event.key === "Enter" && !event.shiftKey) {
//       event.preventDefault(); // Prevent default newline behavior
//       handleSendMessage();
//     }
//   };

//   return (
//     <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 via-stone-50 to-gray-100">
//       {/* Optional Header */}
//       <header className="bg-white border-b border-gray-200 p-4 shadow-sm sticky top-0 z-10">
//         <h1 className="text-xl font-semibold text-gray-800 text-center">
//           Agentic AI ChatBot
//         </h1>
//       </header>

//       {/* Message Display Area */}
//       <div className="flex-grow overflow-y-auto p-4 space-y-4">
//         {messages.map((msg) => (
//           <MessageBubble key={msg.id} message={msg} />
//         ))}
//         {/* Show typing indicator when loading */}
//         {isLoading && <TypingIndicator />}
//         {/* Element to scroll to */}
//         <div ref={messagesEndRef} />
//       </div>

//       {/* Error Display Area */}
//       {error && (
//         <div className="p-2 text-center text-red-600 bg-red-100 border-t border-red-200">
//           {error}
//         </div>
//       )}

//       {/* Input Area */}
//       <div className="bg-white border-t border-gray-200 p-4 sticky bottom-0">
//         <div className="flex items-center space-x-2">
//           <input
//             type="text"
//             value={inputValue}
//             onChange={(e) => setInputValue(e.target.value)}
//             onKeyDown={handleKeyDown} // Handle Enter key
//             placeholder="Type your message..."
//             className="flex-grow px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-150 ease-in-out"
//             disabled={isLoading} // Disable input while loading
//             aria-label="Chat message input"
//           />
//           <button
//             onClick={handleSendMessage}
//             disabled={isLoading || inputValue.trim() === ""} // Disable button if loading or input is empty
//             className={`p-2 rounded-full text-white transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
//               isLoading || inputValue.trim() === ""
//                 ? "bg-gray-400 cursor-not-allowed"
//                 : "bg-blue-600 hover:bg-blue-700"
//             }`}
//             aria-label="Send message"
//           >
//             <SendHorizonal size={20} />
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// }
