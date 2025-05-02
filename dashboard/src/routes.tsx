import { createBrowserRouter, createRoutesFromElements, Route } from "react-router-dom"
import RootLayout from "@/components/layout/RootLayout"
import Home from "@/pages/Home"
import ApiKeys from "@/pages/ApiKeys"
import NotFound from "@/pages/NotFound"

export const router = createBrowserRouter(
    createRoutesFromElements(
        <Route path="/" element={<RootLayout />}>
            <Route index element={<Home />} />
            <Route path="api-keys" element={<ApiKeys />} />
            <Route path="*" element={<NotFound />} />
        </Route>
    )
) 