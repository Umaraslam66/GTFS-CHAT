import { useRef, useEffect } from "react";
import MessageBubble, { Message } from "./MessageBubble";
import { Train } from "lucide-react";

interface ChatContainerProps {
  messages: Message[];
  onSuggestion?: (text: string) => void;
}

const ChatContainer = ({ messages, onSuggestion }: ChatContainerProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Empty state
  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12">
        <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-6">
          <Train className="h-8 w-8 text-muted-foreground" />
        </div>
        <h2 className="text-xl font-semibold text-foreground mb-2">
          Welcome to GTFS Sweden Chat
        </h2>
        <p className="text-sm text-muted-foreground text-center max-w-md leading-relaxed">
          Ask me anything about Swedish public transport schedules, routes, and
          stops. I can help you find train times, connections, and more.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-2">
          {[
            "Show trains from Stockholm to Gothenburg",
            "What stops are on line 10?",
            "Next departures from Malmö Central",
          ].map((suggestion) => (
            <button
              key={suggestion}
              className="px-4 py-2 text-sm bg-card border border-border rounded-lg text-foreground hover:bg-muted/50 transition-colors"
              onClick={() => onSuggestion?.(suggestion)}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto px-4 py-6"
      role="log"
      aria-live="polite"
    >
      <div className="max-w-3xl mx-auto space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
      </div>
    </div>
  );
};

export default ChatContainer;
