import { Message, TableData } from "@/components/chat/MessageBubble";

type ApiTableColumn = { id: string; label: string };
type ApiTable = { columns: ApiTableColumn[]; rows: Record<string, unknown>[]; title?: string };
type ApiChatMessage = { role: string; text: string; table?: ApiTable; warnings?: string[] };
type ApiChatResponse = { messages: ApiChatMessage[]; metadata?: Record<string, unknown> };

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function mapTable(table?: ApiTable): TableData | undefined {
  if (!table || !table.columns?.length) return undefined;

  const headers = table.columns.map((c) => c.label);
  const columnOrder = table.columns.map((c) => c.id);
  const rows = (table.rows || []).map((row) => columnOrder.map((key) => row[key] ?? ""));

  return {
    headers,
    rows,
    caption: table.title,
  };
}

function withWarnings(text: string, warnings?: string[]): string {
  if (!warnings?.length) return text;
  const warningText = warnings.map((w) => `• ${w}`).join("\n");
  return text ? `${text}\n\nWarnings:\n${warningText}` : `Warnings:\n${warningText}`;
}

export async function sendChat(message: string, sessionId?: string): Promise<Message[]> {
  const resp = await fetch(`${API_BASE}/api/chat/adk`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!resp.ok) {
    const detail = await resp.text();
    throw new Error(detail || `Request failed with status ${resp.status}`);
  }

  const data = (await resp.json()) as ApiChatResponse;
  const now = Date.now();

  return (data.messages || []).map((m, idx) => ({
    id: `${m.role}-${now}-${idx}`,
    role: m.role === "user" ? "user" : "agent",
    content: withWarnings(m.text ?? "", m.warnings),
    timestamp: new Date(),
    tableData: mapTable(m.table),
  }));
}

