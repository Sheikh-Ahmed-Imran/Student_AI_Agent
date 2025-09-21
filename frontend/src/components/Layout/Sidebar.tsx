import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { 
  MessageSquare, 
  BarChart3, 
  Users, 
  UserPlus,
  GraduationCap
} from "lucide-react";

const navigation = [
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Students", href: "/students", icon: Users },
  { name: "Add Student", href: "/students/add", icon: UserPlus },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <div className="flex h-full w-64 flex-col bg-dashboard-sidebar border-r border-dashboard-border">
      <div className="flex h-16 items-center justify-center border-b border-dashboard-border">
        <div className="flex items-center gap-2">
          <GraduationCap className="h-8 w-8 text-primary" />
          <span className="text-xl font-bold text-foreground">Campus Admin</span>
        </div>
      </div>
      
      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                "group flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-dashboard-nav-active text-primary"
                  : "text-muted-foreground hover:bg-dashboard-nav-active/50 hover:text-foreground"
              )}
            >
              <item.icon
                className={cn(
                  "mr-3 h-5 w-5 shrink-0",
                  isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                )}
              />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}