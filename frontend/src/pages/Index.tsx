import { useState, useCallback } from "react";
import MainLayout from "@/layouts/MainLayout";
import ChatContainer from "@/components/chat/ChatContainer";
import MessageInput from "@/components/chat/MessageInput";
import { Message } from "@/components/chat/MessageBubble";
import { sendChat } from "@/lib/api";
import { AVAILABLE_MODELS } from "@/components/chat/ModelSelector";

const Index = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState<string>(
    AVAILABLE_MODELS[0].value
  );
  const [sessionId] = useState<string>(() =>
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `session-${Date.now()}`
  );

  const handleSendMessage = useCallback(async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // Add loading indicator
    const loadingId = `loading-${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      {
        id: loadingId,
        role: "agent",
        content: "",
        timestamp: new Date(),
        isLoading: true,
      },
    ]);

    try {
      const responseMessages = await sendChat(content, sessionId, selectedModel);

      // Replace loading with actual response
      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== loadingId);
        return [...filtered, ...responseMessages];
      });
    } catch (err) {
      // Replace loading with error message
      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== loadingId);
        return [
          ...filtered,
          {
            id: `error-${Date.now()}`,
            role: "agent",
            content:
              err instanceof Error
                ? err.message
                : "Sorry, something went wrong. Please try again.",
            timestamp: new Date(),
            isError: true,
          },
        ];
      });
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, selectedModel]);

  return (
    <MainLayout
      selectedModel={selectedModel}
      onModelChange={setSelectedModel}
    >
      <ChatContainer messages={messages} onSuggestion={handleSendMessage} />
      <MessageInput onSend={handleSendMessage} disabled={isLoading} />
    </MainLayout>
  );
};

export default Index;
