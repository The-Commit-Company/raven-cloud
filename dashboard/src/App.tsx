import './App.css'
import { FrappeProvider } from 'frappe-react-sdk'
import { Button } from '@/components/ui/button'
function App() {

	return (
		<div className="App">
			<FrappeProvider>
				<div className="flex flex-col items-center justify-center min-h-svh">
					<Button variant="default">Click me</Button>
				</div>
			</FrappeProvider>
		</div>
	)
}

export default App
