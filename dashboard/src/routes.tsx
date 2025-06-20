import { createBrowserRouter, createRoutesFromElements, Route } from "react-router-dom"
import RootLayout from "@/components/layout/RootLayout"
import Home from "@/pages/Home"
import { ApiKeys } from "@/pages/ApiKeys"
import NotFound from "@/pages/NotFound"
import { ProtectedRoute } from "./components/layout/ProtectedRoute"

export const router = createBrowserRouter(
    createRoutesFromElements(
        <>
            <Route path="/login" element={<div>Login Page</div>} />
            <Route path="/" element={<ProtectedRoute />}>
                <Route element={<RootLayout />}>
                    <Route index element={<Home />} /> 
                    <Route path="profile" element={<ApiKeys />} />
                    <Route path="*" element={<NotFound />} />
                </Route>
            </Route>
        </>
    ),
    {
        basename: import.meta.env.VITE_BASE_NAME ? `/${import.meta.env.VITE_BASE_NAME}` : '',
    }
) 