"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import { useRouter, usePathname } from "next/navigation";
import { DemoList } from "@/components/demo-list/demo-list";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { 
  Eye, 
  Code, 
  Book, 
  ChevronDown, 
  ChevronRight,
  Menu,
  X,
  Home,
  Settings,
  BarChart3,
  Users
} from "lucide-react";
import featureConfig from "@/config";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "../ui/dropdown-menu";
import { Button } from "../ui/button";
import { Feature } from "@/types/integration";
import { cn } from "@/lib/utils";

interface SidebarProps {
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  readmeContent?: string | null;
}

interface MenuItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  href?: string;
  children?: MenuItem[];
  isActive?: boolean;
}

export function Sidebar({ activeTab = "preview", onTabChange, readmeContent }: SidebarProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [isDarkTheme, setIsDarkTheme] = useState<boolean>(false);
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  // Fixed integration configuration
  const INTEGRATION_ID = "adk-middleware";
  const INTEGRATION_NAME = "Transfer Portal Analysis";
  const DEFAULT_DEMO_ID = "human_in_the_loop";

  // Extract the current demo ID from the pathname
  const pathParts = pathname.split("/");
  const currentDemoId = pathParts[pathParts.length - 1];

  // Define menu items
  const menuItems: MenuItem[] = [
    {
      id: "dashboard",
      label: "Dashboard",
      icon: <Home className="h-4 w-4" />,
      href: `/${INTEGRATION_ID}/dashboard`,
      isActive: pathname.includes("dashboard")
    },
    {
      id: "transfer-portal",
      label: "Transfer Portal",
      icon: <Users className="h-4 w-4" />,
      children: [
        {
          id: "analysis",
          label: "Analysis",
          icon: <BarChart3 className="h-4 w-4" />,
          href: `/${INTEGRATION_ID}/feature/${DEFAULT_DEMO_ID}`,
          isActive: currentDemoId === DEFAULT_DEMO_ID
        },
        {
          id: "prospects",
          label: "Prospects",
          icon: <Eye className="h-4 w-4" />,
          href: `/${INTEGRATION_ID}/feature/prospects`,
          isActive: currentDemoId === "prospects"
        }
      ]
    },
    {
      id: "settings",
      label: "Settings",
      icon: <Settings className="h-4 w-4" />,
      href: `/${INTEGRATION_ID}/settings`,
      isActive: pathname.includes("settings")
    }
  ];

  // Define the fixed integration object
  const currentIntegration = {
    id: INTEGRATION_ID,
    name: INTEGRATION_NAME,
    features: [] as Feature[]
  };

  // Filter demos based on current integration's features
  const filteredDemos = currentIntegration.features.length > 0
    ? featureConfig.filter((demo) =>
        currentIntegration.features.includes(demo.id as unknown as Feature),
      )
    : featureConfig;

  // Handle selecting a demo
  const handleDemoSelect = (demoId: string) => {
    router.push(`/${INTEGRATION_ID}/feature/${demoId}`);
  };

  // Handle menu item click
  const handleMenuItemClick = (item: MenuItem) => {
    if (item.href) {
      router.push(item.href);
    }
    
    if (item.children) {
      toggleExpanded(item.id);
    }
  };

  // Toggle expanded state for menu items with children
  const toggleExpanded = (itemId: string) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  // Check for dark mode using media query
  useEffect(() => {
    if (typeof window !== "undefined") {
      setIsDarkTheme(window.matchMedia("(prefers-color-scheme: dark)").matches);

      const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
      const handleChange = (e: MediaQueryListEvent) => {
        setIsDarkTheme(e.matches);
      };

      mediaQuery.addEventListener("change", handleChange);

      const observer = new MutationObserver(() => {
        setIsDarkTheme(document.documentElement.classList.contains("dark"));
      });

      observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ["class"],
      });

      return () => {
        mediaQuery.removeEventListener("change", handleChange);
        observer.disconnect();
      };
    }
  }, []);

  // Initialize expanded items
  useEffect(() => {
    // Auto-expand parent items if child is active
    menuItems.forEach(item => {
      if (item.children?.some(child => child.isActive)) {
        setExpandedItems(prev => new Set([...prev, item.id]));
      }
    });
  }, [pathname]);

  // Render menu item recursively
  const renderMenuItem = (item: MenuItem, level: number = 0) => {
    const isExpanded = expandedItems.has(item.id);
    const hasChildren = item.children && item.children.length > 0;

    return (
      <div key={item.id} className="mb-1">
        <div
          className={cn(
            "flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors",
            "hover:bg-accent hover:text-accent-foreground",
            item.isActive && "bg-accent text-accent-foreground font-medium",
            level > 0 && "ml-4"
          )}
          onClick={() => handleMenuItemClick(item)}
        >
          <div className="flex items-center space-x-3">
            {item.icon}
            {!isCollapsed && (
              <span className="text-sm font-medium">{item.label}</span>
            )}
          </div>
          
          {hasChildren && !isCollapsed && (
            <div className="ml-auto">
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </div>
          )}
        </div>

        {/* Render children if expanded */}
        {hasChildren && isExpanded && !isCollapsed && (
          <div className="mt-1">
            {item.children?.map(child => renderMenuItem(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      {/* Sidebar */}
      <div className={cn(
        "flex flex-col h-full border-r bg-background transition-all duration-300",
        isCollapsed ? "w-16" : "w-74 min-w-[296px]",
        "flex-shrink-0"
      )}>
        {/* Header */}
        <div className="p-4 border-b bg-background">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="p-2 hover:bg-accent"
              >
                {isCollapsed ? <Menu className="h-4 w-4" /> : <X className="h-4 w-4" />}
              </Button>
              
              {!isCollapsed && (
                <h1 className={`text-lg font-light ${isDarkTheme ? "text-white" : "text-gray-900"}`}>
                  SLAM SPORTS
                </h1>
              )}
            </div>

            {!isCollapsed && <ThemeToggle />}
          </div>
        </div>

        {/* Navigation Menu */}
        <div className="flex-1 p-4 overflow-y-auto">
          {!isCollapsed && (
            <div className="mb-4">
              <label className="block text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wide">
                Navigation
              </label>
            </div>
          )}
          
          <nav className="space-y-1">
            {menuItems.map(item => renderMenuItem(item))}
          </nav>

          {/* Demo List Section */}

        </div>

        {/* Footer */}
        {!isCollapsed && (
          <div className="p-4 border-t bg-background">
            <div className="text-xs text-muted-foreground">
              {INTEGRATION_NAME}
            </div>
          </div>
        )}
      </div>

      {/* Mobile Overlay */}
      {!isCollapsed && (
        <div 
          className="fixed inset-0 bg-black/20 z-40 md:hidden"
          onClick={() => setIsCollapsed(true)}
        />
      )}
    </>
  );
}