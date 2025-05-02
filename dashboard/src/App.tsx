import './App.css'
import { FrappeProvider } from 'frappe-react-sdk'
import { RouterProvider } from 'react-router-dom'
import { router } from './routes'

function App() {
	return (
		<FrappeProvider>
			<RouterProvider router={router} />
		</FrappeProvider>
	)
}

export default App
