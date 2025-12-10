import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export interface ModelOption {
  value: string;
  label: string;
  description?: string;
}

export const AVAILABLE_MODELS: ModelOption[] = [
  {
    value: "mistralai/devstral-2512:free",
    label: "Mistral Devstral 2.5 (Free)",
    description: "Fast, good JSON support",
  },
  {
    value: "amazon/nova-2-lite-v1:free",
    label: "Amazon Nova 2 Lite (Free)",
    description: "May have JSON issues",
  },
  {
    value: "openrouter/meta-llama/llama-3.1-8b-instruct:free",
    label: "Llama 3.1 8B (Free)",
    description: "Good for tool calling",
  },
  {
    value: "openrouter/google/gemini-2.0-flash-exp",
    label: "Google Gemini 2.0 Flash",
    description: "Excellent JSON support",
  },
  {
    value: "openrouter/anthropic/claude-3-haiku",
    label: "Claude 3 Haiku",
    description: "Reliable, paid",
  },
];

interface ModelSelectorProps {
  value: string;
  onValueChange: (value: string) => void;
  className?: string;
}

export default function ModelSelector({
  value,
  onValueChange,
  className,
}: ModelSelectorProps) {
  return (
    <Select value={value} onValueChange={onValueChange}>
      <SelectTrigger className={className || "w-[240px] h-9 text-xs"}>
        <SelectValue placeholder="Select model" />
      </SelectTrigger>
      <SelectContent>
        {AVAILABLE_MODELS.map((model) => (
          <SelectItem key={model.value} value={model.value}>
            <div className="flex flex-col">
              <span className="font-medium">{model.label}</span>
              {model.description && (
                <span className="text-xs text-muted-foreground">
                  {model.description}
                </span>
              )}
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

