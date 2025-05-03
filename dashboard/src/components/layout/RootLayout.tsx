import { Outlet } from "react-router-dom"
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/layout/Sidebar/AppSidebar"

export default function RootLayout() {
    return (
        <div className="App">
            <SidebarProvider>
                <AppSidebar />
                <div className="flex flex-col flex-1">
                    <SidebarTrigger />
                    <div className="flex flex-1 items-center justify-center">
                    <Outlet />
                </div>
                </div>
            </SidebarProvider>
        </div>
    )
} 