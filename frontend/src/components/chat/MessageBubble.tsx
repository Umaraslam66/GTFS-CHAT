import { cn } from "@/lib/utils";
import DataTable from "./DataTable";
import MapPlaceholder from "./MapPlaceholder";
import LoadingIndicator from "./LoadingIndicator";
import { AlertCircle } from "lucide-react";

export interface TableData {
  headers: string[];
  rows: (string | number)[][];
  caption?: string;
}

export interface Message {
  id: string;
  role: "user" | "agent";
  content: string;
  timestamp: Date;
  isLoading?: boolean;
  isError?: boolean;
  tableData?: TableData;
  showMap?: boolean;
}

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex w-full animate-message-in",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[85%] md:max-w-[70%] lg:max-w-[60%]",
          isUser ? "items-end" : "items-start"
        )}
      >
        <div
          className={cn(
            "px-4 py-3 rounded-lg",
            isUser
              ? "bg-chat-user text-chat-user-foreground rounded-br-sm"
              : "bg-chat-agent border border-chat-agent-border text-foreground rounded-bl-sm",
            message.isError && "border-destructive/50 bg-destructive/10"
          )}
        >
          {message.isLoading ? (
            <LoadingIndicator />
          ) : message.isError ? (
            <div className="flex items-start gap-2">
              <AlertCircle className="h-4 w-4 text-destructive mt-0.5 shrink-0" />
              <p className="text-sm leading-relaxed">{message.content}</p>
            </div>
          ) : (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
          )}
        </div>

        {/* Data table if present */}
        {message.tableData && !message.isLoading && (
          <DataTable
            headers={message.tableData.headers}
            rows={message.tableData.rows}
            caption={message.tableData.caption}
          />
        )}

        {/* Map placeholder if requested */}
        {message.showMap && !message.isLoading && <MapPlaceholder />}

        {/* Timestamp */}
        <p
          className={cn(
            "text-xs text-muted-foreground mt-1.5 px-1",
            isUser ? "text-right" : "text-left"
          )}
        >
          {message.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </div>
  );
};

export default MessageBubble;
