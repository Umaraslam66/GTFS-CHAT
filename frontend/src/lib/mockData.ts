import { Message, TableData } from "@/components/chat/MessageBubble";

export const sampleTableData: TableData = {
  caption: "Departures from Stockholm Central",
  headers: ["Departure", "Destination", "Train", "Platform", "Status"],
  rows: [
    ["08:15", "Gothenburg", "SJ X2000", "14", "On time"],
    ["08:32", "Uppsala", "Mälartåg", "7", "On time"],
    ["08:45", "Malmö", "SJ Snabbtåg", "12", "Delayed 5 min"],
    ["09:00", "Sundsvall", "SJ Regional", "3", "On time"],
    ["09:15", "Linköping", "SJ X2000", "11", "On time"],
  ],
};

export const sampleConversation: Message[] = [
  {
    id: "1",
    role: "user",
    content: "What trains leave from Stockholm Central in the next hour?",
    timestamp: new Date(Date.now() - 300000),
  },
  {
    id: "2",
    role: "agent",
    content:
      "Here are the upcoming departures from Stockholm Central. I've found 5 trains leaving within the next hour:",
    timestamp: new Date(Date.now() - 295000),
    tableData: sampleTableData,
  },
  {
    id: "3",
    role: "user",
    content: "Can you show me the route for the 08:15 train to Gothenburg?",
    timestamp: new Date(Date.now() - 180000),
  },
  {
    id: "4",
    role: "agent",
    content:
      "The SJ X2000 departing at 08:15 makes the following stops:\n\n• Stockholm Central (08:15)\n• Södertälje Syd (08:35)\n• Katrineholm (09:05)\n• Hallsberg (09:30)\n• Skövde (10:15)\n• Gothenburg Central (11:20)\n\nThe journey takes approximately 3 hours and 5 minutes.",
    timestamp: new Date(Date.now() - 175000),
    showMap: true,
  },
];

export const errorMessage: Message = {
  id: "error",
  role: "agent",
  content:
    "I couldn't understand that question. Please try rephrasing it or ask about specific stations, routes, or schedules.",
  timestamp: new Date(),
  isError: true,
};

export const loadingMessage: Message = {
  id: "loading",
  role: "agent",
  content: "",
  timestamp: new Date(),
  isLoading: true,
};

// Mock API response simulation
export const mockApiCall = async (
  userMessage: string
): Promise<{ content: string; tableData?: TableData; showMap?: boolean }> => {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 1500));

  const lowerMessage = userMessage.toLowerCase();

  // Simulate different responses based on keywords
  if (
    lowerMessage.includes("stockholm") &&
    (lowerMessage.includes("train") || lowerMessage.includes("departure"))
  ) {
    return {
      content:
        "Here are the upcoming departures from Stockholm Central. I've found 5 trains in the schedule:",
      tableData: sampleTableData,
    };
  }

  if (lowerMessage.includes("route") || lowerMessage.includes("stops")) {
    return {
      content:
        "I found the route information you requested. The train makes several stops along the way. A map visualization will be available soon.",
      showMap: true,
    };
  }

  if (lowerMessage.includes("help") || lowerMessage.includes("what can")) {
    return {
      content:
        "I can help you with:\n\n• Finding train schedules and departures\n• Looking up routes between stations\n• Checking platform information\n• Finding connections and transfers\n\nTry asking something like 'Show trains from Malmö to Stockholm' or 'What are the stops on the Uppsala line?'",
    };
  }

  // Default response
  return {
    content: `I found some information about your query regarding "${userMessage}". Swedish rail services cover an extensive network across the country, connecting major cities and towns.`,
  };
};
