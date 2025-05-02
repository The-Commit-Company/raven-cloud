import { Outlet } from "react-router-dom"
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/layout/Sidebar/AppSidebar"

export default function RootLayout() {
    return (
        <div className="App">
            <SidebarProvider>
                <AppSidebar />
                <div className="flex-1">
                    <SidebarTrigger />
                    <Outlet />
                </div>
            </SidebarProvider>
        </div>
    )
} 