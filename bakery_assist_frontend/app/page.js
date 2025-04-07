import { BakeIcon } from "lucide-react"; // Example using lucide-react icons

export default function Home() {
  return (
    // Slightly softer gradient, more padding overall
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-yellow-50 via-orange-100 to-red-100 text-gray-800 p-4">
      {/* Card: Slightly less padding, softer shadow, refined rounding */}
      <div className="bg-white p-10 rounded-2xl shadow-lg max-w-xl w-full mx-auto text-center">
        {/* Optional: Icon */}
        <div className="flex justify-center mb-5">
          {/* Replace with your actual logo or a relevant icon */}
          {/* Example using Lucide Icons (install: npm i lucide-react) */}
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="48" // Increased size
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5" // Slightly thinner stroke
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-orange-500" // Icon color
          >
            {/* Simple Chat Bubble Icon Path */}
            <path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z" />
            {/* Optional: Add a small element inside like a spark or lightbulb for 'AI' */}
            <path d="m12 7 1.14 2.3 2.36.34-1.7 1.66.4 2.4-2.1-.9-2.1.9.4-2.4-1.7-1.66 2.36-.34L12 7z" />
          </svg>
        </div>

        {/* Title: Slightly adjusted size/weight if needed, good line height */}
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-orange-600 leading-tight">
          Welcome to Bake Assist!
        </h1>

        {/* Subtitle: Softer color for hierarchy, more margin bottom */}
        <p className="text-base md:text-lg text-gray-600 mb-10">
          Your Agentic AI chatbot designed to help grow your bakery business.
        </p>

        {/* Button: Added subtle hover scale, maybe slightly less padding */}
        <div className="mt-6">
          {" "}
          {/* Ensure enough space above button */}
          <a
            href="/customers"
            className="inline-block bg-orange-500 hover:bg-orange-600 text-white font-semibold py-3 px-7 rounded-full transition-all duration-300 ease-in-out shadow hover:shadow-md transform hover:scale-105 active:scale-95"
          >
            Get Started
          </a>
        </div>
      </div>

      {/* Optional Footer/Link */}
      <footer className="mt-8 text-center text-sm text-orange-700/70">
        Powered by Ollama
      </footer>
    </div>
  );
}
