import { ErrorBanner } from "@/components/common/ErrorBanner"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { useDebounce } from "@/hooks/useDebounce"
import { RavenMarketplace } from "@/types/RavenCloud/RavenMarketplace"
import { isSystemManager } from "@/utils/roles"
import { Filter, useFrappeGetDocList } from "frappe-react-sdk"
import { List, Grid3X3, Filter as FilterIcon, Search, Download, Bot, Zap, Bell, FileText } from "lucide-react"
import { useMemo, useState } from "react"

const categories = [
    { id: "all", name: "All Items", icon: Grid3X3 },
    { id: "Bot", name: "Bot", icon: Bot },
    { id: "Document Notification", name: "Document Notifications", icon: Bell },
    { id: "Schedule Messages", name: "Schedule Messages", icon: Zap }
]

const getIconbyMarketPlaceType = (type: string) => {
    switch (type) {
        case 'Bot':
            return Bot
        case 'Document Notification':
            return Bell
        case 'Schedule Messages':
            return Zap
        default:
            return FileText
    }
}

export const Marketplace = () => {
    const isCreateAllowed = isSystemManager()
    const [searchTerm, setSearchTerm] = useState("")

    const debounceText = useDebounce(searchTerm, 500)

    const [viewMode, setViewMode] = useState<"grid" | "list">("grid")
    const [sortBy, setSortBy] = useState("popular")
    const [selectedCategory, setSelectedCategory] = useState("all")

    const filters: Filter[] = useMemo(() => {
        if (selectedCategory === "all") {
            return []
        }
        return [['marketplace_type', '=', selectedCategory]]
    }, [selectedCategory])

    const marketplaceFilters: Filter[] = isCreateAllowed ? [] : [['status', '=', "Published"]]

    const { data, error, isLoading } = useFrappeGetDocList<RavenMarketplace>("Raven Marketplace", {
        filters: [...marketplaceFilters, ...filters],
        // @ts-expect-error expected
        fields: ["name", "title", "description", "marketplace_type", "download_count", "_user_tags", "creation"],
        orFilters: debounceText
            ? [
                ['title', 'like', `%${debounceText}%`],
                ['description', 'like', `%${debounceText}%`],
                ['_user_tags', 'like', `%${debounceText}%`]
            ]
            : undefined,
        limit: 999,
        orderBy: {
            'order': 'desc',
            'field': sortBy ? sortBy === "popular" ? "download_count" : "creation" : "download_count"
        }
    })

    return (
        <div className="min-h-screen">
            {/* Header */}
            <div className="bg-white border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Marketplace</h1>
                            <p className="text-gray-600 mt-1">Discover and download powerful tools for your workflow</p>
                        </div>
                        <div className="flex items-center space-x-4">
                            <Button variant="outline" size="sm" onClick={() => setViewMode(viewMode === "grid" ? "list" : "grid")}>
                                {viewMode === "grid" ? <List className="w-4 h-4" /> : <Grid3X3 className="w-4 h-4" />}
                            </Button>
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="outline" size="sm">
                                        <FilterIcon className="w-4 h-4 mr-2" />
                                        {sortBy === "popular" ? "Most Popular" : sortBy === "newest" ? "Newest" : "Sort by"}
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                    <DropdownMenuLabel>Sort Options</DropdownMenuLabel>
                                    <DropdownMenuSeparator />
                                    <DropdownMenuItem onClick={() => setSortBy("popular")}>Most Popular</DropdownMenuItem>
                                    <DropdownMenuItem onClick={() => setSortBy("newest")}>Newest</DropdownMenuItem>
                                </DropdownMenuContent>
                            </DropdownMenu>
                        </div>
                    </div>
                </div>
            </div>

            <div className="w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <ErrorBanner error={error} />
                <div className="flex gap-8">
                    {/* Sidebar */}
                    <div className="w-64 flex-shrink-0">
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg">Categories</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-2">
                                {categories.map((category) => (
                                    <Button
                                        key={category.id}
                                        variant={selectedCategory === category.id ? "default" : "ghost"}
                                        className="w-full justify-start"
                                        onClick={() => setSelectedCategory(category.id)}
                                    >
                                        <category.icon className="w-4 h-4 mr-2" />
                                        {category.name}
                                    </Button>
                                ))}
                            </CardContent>
                        </Card>
                    </div>

                    {/* Main Content */}
                    <div className="flex-1">
                        {/* Search Bar */}
                        <div className="relative mb-6">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                            <Input
                                type="text"
                                placeholder="Search marketplace items..."
                                className="pl-10"
                                autoFocus
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>

                        {/* Results Header */}
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-gray-900">
                                {selectedCategory === "all" ? "All Items" : categories.find((c) => c.id === selectedCategory)?.name}
                                <span className="text-gray-500 font-normal ml-2">({data?.length || 0} items)</span>
                            </h2>
                        </div>

                        {/* Items Grid/List or Skeleton */}
                        {isLoading ? (
                            <MarketplaceSkeleton viewMode={viewMode} />
                        ) : (
                            <>
                                {data?.length === 0 ? (
                                    <div className="text-center py-12">
                                        <div className="w-24 h-24 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-4">
                                            <Search className="w-8 h-8 text-gray-400" />
                                        </div>
                                        <h3 className="text-lg font-medium text-gray-900 mb-2">No items found</h3>
                                        <p className="text-gray-500">Try adjusting your search or filter criteria</p>
                                    </div>
                                ) : (
                                    <div className={viewMode === "grid" ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" : "space-y-4"}>
                                        {data?.map((item) => {
                                            const Icon = getIconbyMarketPlaceType(item.marketplace_type);
                                            // @ts-expect-error expected
                                            const tags = item._user_tags ? item._user_tags.split(",").map(tag => tag.trim()) : [];
                                            return (
                                                <Card
                                                    key={item.name}
                                                    className={`hover:shadow-lg transition-shadow cursor-pointer flex flex-col h-full ${viewMode === "list" ? "flex-row" : ""}`}
                                                >
                                                    <div className={viewMode === "list" ? "w-20 flex-shrink-0 p-4" : ""}>
                                                        <CardHeader className={viewMode === "list" ? "p-0" : ""}>
                                                            <div className="flex items-center justify-between">
                                                                <div className={`${viewMode === "list" ? "w-12 h-12" : "h-10 w-10"} flex items-center justify-center bg-blue-100 text-blue-600 rounded-lg`}>
                                                                    <Icon className={`${viewMode === "list" ? "w-8 h-8" : "w-6 h-6"}`} />
                                                                </div>
                                                                {viewMode === "grid" && (
                                                                    <Badge variant={"secondary"}>{"Free"}</Badge>
                                                                )}
                                                            </div>
                                                        </CardHeader>
                                                    </div>

                                                    <div className={viewMode === "list" ? "flex-1 flex flex-col" : "flex flex-col h-full"}>
                                                        <CardHeader className={viewMode === "list" ? "pb-2" : ""}>
                                                            <div className="flex items-center justify-between">
                                                                <CardTitle className="text-lg">{item.title}</CardTitle>
                                                                {viewMode === "list" && (
                                                                    <Badge variant={"secondary"}>{"Free"}</Badge>
                                                                )}
                                                            </div>
                                                            <CardDescription className="text-sm">{item.description}</CardDescription>
                                                        </CardHeader>

                                                        <CardContent className={`flex flex-col h-full ${viewMode === "list" ? "pt-0" : ""}`}>
                                                            <div>
                                                                <div className="flex items-center justify-between mb-4 mt-1">
                                                                    <div className="flex items-center space-x-4">
                                                                        <div className="flex items-center">
                                                                            <Download className="w-4 h-4 text-gray-400" />
                                                                            <span className="text-sm text-gray-600 ml-1">{item.download_count}</span>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                                <div className="flex flex-wrap gap-1 mb-4">
                                                                    {/* @ts-expect-error expected*/}
                                                                    {tags.filter(tag => tag).map((tag, index) => (
                                                                        <Badge key={index} variant="outline" className="text-xs">
                                                                            {tag}
                                                                        </Badge>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                            <Button className="w-full mt-auto">
                                                                <Download className="w-4 h-4 mr-2" />
                                                                Download
                                                            </Button>
                                                        </CardContent>
                                                    </div>
                                                </Card>
                                            );
                                        })}
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

// Skeleton Loader Component
const MarketplaceSkeleton = ({ viewMode = "grid" }: { viewMode?: "grid" | "list" }) => {
    const skeletonArray = Array(viewMode === "grid" ? 6 : 3).fill(0);

    return (
        <div className="flex gap-8">
            {/* Sidebar Skeleton */}
            <div className="w-64 flex-shrink-0">
                <div className="bg-white rounded-lg shadow p-4">
                    <div className="h-7 w-44 bg-gray-200 rounded mb-4 animate-pulse gap-4" />
                    {[...Array(4)].map((_, i) => (
                        <div key={i} className="flex items-center mb-2 gap-4">
                            <div className="w-6 h-6 bg-gray-200 rounded animate-pulse" />
                            <div className="h-6 w-34 bg-gray-200 rounded animate-pulse" />
                        </div>
                    ))}
                </div>
            </div>

            {/* Main Content Skeleton */}
            <div className="flex-1">
                {/* Search Bar Skeleton */}
                <div className="relative mb-6">
                    <div className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 bg-gray-200 rounded animate-pulse" />
                    <div className="h-10 bg-gray-200 rounded w-full pl-10 animate-pulse" />
                </div>

                {/* Results Header Skeleton */}
                <div className="h-6 w-48 bg-gray-200 rounded mb-6 animate-pulse" />

                {/* Cards Skeleton */}
                <div className={viewMode === "grid" ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" : "space-y-4"}>
                    {skeletonArray.map((_, idx) => (
                        <div
                            key={idx}
                            className={`bg-white rounded-lg shadow flex flex-col h-full p-4 ${viewMode === "list" ? "flex-row" : ""}`}
                        >
                            <div className={viewMode === "list" ? "w-20 flex-shrink-0 p-4" : ""}>
                                <div className="flex items-center justify-between mb-6">
                                    {/* Icon skeleton */}
                                    <div className={`${viewMode === "list" ? "w-12 h-12" : "h-10 w-10"} flex items-center justify-center bg-blue-100 rounded-lg`}>
                                        <div className={`${viewMode === "list" ? "w-8 h-8" : "w-6 h-6"} bg-gray-200 rounded animate-pulse`} />
                                    </div>
                                    {/* Badge skeleton (only in grid view) */}
                                    {viewMode === "grid" && (
                                        <div className="h-6 w-12 bg-gray-200 rounded ml-2 animate-pulse" />
                                    )}
                                </div>
                            </div>
                            <div className={viewMode === "list" ? "flex-1 flex flex-col" : "flex flex-col h-full"}>
                                <div className="flex items-center justify-between mt-2 mb-2">
                                    <div className="h-5 w-32 bg-gray-200 rounded animate-pulse" />
                                    {/* Badge skeleton (in list view) */}
                                    {viewMode === "list" && (
                                        <div className="h-6 w-12 bg-gray-200 rounded ml-2 animate-pulse" />
                                    )}
                                </div>
                                <div className="h-8 w-48 bg-gray-200 rounded mb-4 animate-pulse" />
                                <div className="flex gap-2 mb-4">
                                    <div className="h-4 w-12 bg-gray-200 rounded animate-pulse" />
                                    <div className="h-4 w-12 bg-gray-200 rounded animate-pulse" />
                                </div>
                                <div className="flex-1" />
                                <div className="h-10 w-full bg-gray-200 rounded mt-auto animate-pulse" />
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}