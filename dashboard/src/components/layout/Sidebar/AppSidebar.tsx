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
]

// *NOTE: temporarily commented out as this is not currently in upcoming plans (as of 02-03-2026)
// const comingSoonItems = [
//     {
//         title: "Typesense Search",
//         url: "/search",
//         icon: Search,
//     },
//     {
//         title: "Marketplace",
//         url: "/marketplace",
//         icon: Store,
//     },
//     {
//         title: "Video Calling",
//         url: "/video-calling",
//         icon: Video,
//     }
// ]

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

            </SidebarContent>
            <SidebarFooter>
                <NavUser />
            </SidebarFooter>
        </Sidebar>
    )
}
