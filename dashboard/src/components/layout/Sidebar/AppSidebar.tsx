import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from "@/components/ui/sidebar"
import { Home, KeyRound, Search, Video, Store } from "lucide-react"
import { Link } from "react-router-dom"
import { NavUser } from "@/components/layout/Sidebar/NavUser"

// Menu items.
const items = [
    {
        title: "Home",
        url: "/",
        icon: Home,
    },
    {
        title: "API Keys",
        url: "/profile",
        icon: KeyRound,
    },
    {
        title: "Marketplace",
        url: "/marketplace",
        icon: Store,
    }
]

const comingSoonItems = [
    {
        title: "Typesense Search",
        url: "/search",
        icon: Search,
    },
    {
        title: "Video Calling",
        url: "/video-calling",
        icon: Video,
    }
]

export function AppSidebar() {
    return (
        <Sidebar>
            <SidebarHeader />
            <SidebarContent>
                <SidebarGroup>
                    <SidebarGroupLabel>Application</SidebarGroupLabel>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            {items.map((item) => (
                                <SidebarMenuItem key={item.title}>
                                    <SidebarMenuButton asChild>
                                        <Link to={item.url}>
                                            <item.icon />
                                            <span>{item.title}</span>
                                        </Link>
                                    </SidebarMenuButton>
                                </SidebarMenuItem>
                            ))}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
                <SidebarGroup>
                    <SidebarGroupLabel>Coming Soon</SidebarGroupLabel>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            {comingSoonItems.map((item) => (
                                <SidebarMenuItem key={item.title}>
                                    <SidebarMenuButton asChild disabled>
                                        {/* <Link to={item.url}>
                                            <item.icon />
                                            <span>{item.title}</span>
                                        </Link> */}
                                        <div className="flex items-center gap-2 cursor-not-allowed">
                                            <item.icon />
                                            <span>{item.title}</span>
                                        </div>
                                    </SidebarMenuButton>
                                </SidebarMenuItem>
                            ))}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
            </SidebarContent>
            <SidebarFooter>
                <NavUser />
            </SidebarFooter>
        </Sidebar>
    )
}
