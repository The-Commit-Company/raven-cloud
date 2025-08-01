import { useContext } from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import { UserContext } from '@/providers/UserProvider'
// import { Flex, Text } from '@radix-ui/'
// import { Stack } from '@/components/ui/stack'

export const ProtectedRoute = () => {

    const { currentUser, isLoading } = useContext(UserContext)

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                    <p className="mt-2">Loading...</p>
                </div>
            </div>
        )
    }

    if (!currentUser || currentUser === 'Guest') {
        return <Navigate to="/login" replace />
    }

    return <Outlet />
}