import { Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import ModelSelector, { AVAILABLE_MODELS } from "./ModelSelector";

interface TopBarProps {
  selectedModel: string;
  onModelChange: (model: string) => void;
}

const TopBar = ({ selectedModel, onModelChange }: TopBarProps) => {
  return (
    <header className="flex items-center justify-between px-5 py-4 border-b border-border bg-background">
      <div className="flex items-center gap-3">
        <div className="w-1 h-5 bg-primary rounded-full" aria-hidden="true" />
        <h1 className="text-lg font-semibold text-foreground tracking-tight">
          GTFS Sweden Chat
        </h1>
      </div>
      <div className="flex items-center gap-3">
        <ModelSelector
          value={selectedModel}
          onValueChange={onModelChange}
          className="w-[220px] h-9 text-xs"
        />
        <Button
          variant="ghost"
          size="icon"
          className="text-muted-foreground hover:text-foreground"
          aria-label="Settings"
        >
          <Settings className="h-5 w-5" />
        </Button>
      </div>
    </header>
  );
};

export default TopBar;
