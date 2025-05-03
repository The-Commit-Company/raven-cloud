import { Outlet } from "react-router-dom"
import { SidebarProvider } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/layout/Sidebar/AppSidebar"

export default function RootLayout() {
    return (
        <div className="App">
            <SidebarProvider>
                <AppSidebar />
                <div className="flex flex-1 items-center justify-center p-8">
                    <Outlet />
                </div>
            </SidebarProvider>
        </div>
    )
} 