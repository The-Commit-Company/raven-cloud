import { FrappeProvider } from 'frappe-react-sdk'
import { RouterProvider } from 'react-router-dom'
import { UserProvider } from '@/providers/UserProvider'
import { Toaster } from 'sonner'
import { router } from '@/routes'

function App() {

	const getSiteName = () => {
		// @ts-ignore
		if (window.frappe?.boot?.versions?.frappe.startsWith('14')) {
			return import.meta.env.VITE_SITE_NAME
		}
		// @ts-ignore
		else {
			// @ts-ignore
			return window.frappe?.boot?.sitename ?? import.meta.env.VITE_SITE_NAME
		}
	}

	return (
		<FrappeProvider siteName={getSiteName()} url={import.meta.env.VITE_FRAPPE_PATH ?? ''}
			socketPort={import.meta.env.VITE_SOCKET_PORT ? import.meta.env.VITE_SOCKET_PORT : undefined}>
			<UserProvider>
				<Toaster richColors />
				<RouterProvider router={router} />
			</UserProvider>
		</FrappeProvider>
	)
}

export default App
