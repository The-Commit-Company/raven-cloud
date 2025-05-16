import { FrappeProvider } from 'frappe-react-sdk'
import { RouterProvider } from 'react-router-dom'
import { UserProvider } from '@/providers/UserProvider'
import { Toaster } from 'sonner'
import { router } from '@/routes'

function App() {
	return (
		<FrappeProvider>
			<UserProvider>
				<Toaster richColors />
				<RouterProvider router={router} />
			</UserProvider>
		</FrappeProvider>
	)
}

export default App
