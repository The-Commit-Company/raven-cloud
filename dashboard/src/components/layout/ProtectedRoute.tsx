import { useContext } from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import { UserContext } from '@/providers/UserProvider'
// import { Flex, Text } from '@radix-ui/'
// import { Stack } from '@/components/ui/stack'

export const ProtectedRoute = () => {

    const { currentUser, isLoading } = useContext(UserContext)

    if (isLoading) {
        return <div>Loading...</div>
    }
    else if (!currentUser || currentUser === 'Guest') {
        // TODO: use this once we have a login page
        // return <Navigate to="/login" replace />
        window.location.replace('/login')
    }
    return (
        <Outlet />
    )
}