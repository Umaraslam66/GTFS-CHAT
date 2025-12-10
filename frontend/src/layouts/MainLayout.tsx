import { ReactNode } from "react";
import TopBar from "@/components/chat/TopBar";

interface MainLayoutProps {
  children: ReactNode;
}

const MainLayout = ({ children }: MainLayoutProps) => {
  return (
    <div className="flex flex-col h-screen bg-background">
      <TopBar />
      <main className="flex-1 flex flex-col overflow-hidden">{children}</main>
    </div>
  );
};

export default MainLayout;
