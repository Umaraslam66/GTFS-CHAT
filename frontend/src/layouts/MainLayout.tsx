import { ReactNode } from "react";
import TopBar from "@/components/chat/TopBar";

interface MainLayoutProps {
  children: ReactNode;
  selectedModel: string;
  onModelChange: (model: string) => void;
}

const MainLayout = ({
  children,
  selectedModel,
  onModelChange,
}: MainLayoutProps) => {
  return (
    <div className="flex flex-col h-screen bg-background">
      <TopBar selectedModel={selectedModel} onModelChange={onModelChange} />
      <main className="flex-1 flex flex-col overflow-hidden">{children}</main>
    </div>
  );
};

export default MainLayout;
