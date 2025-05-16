import { Link } from "react-router-dom"

export default function NotFound() {
    return (
        <div className="container py-8 flex flex-col items-center justify-center min-h-[60vh]">
            <h1 className="text-4xl font-bold mb-4">404</h1>
            <p className="text-xl mb-6">Page not found</p>
            <Link to="/" className="underline text-blue-500">
                Go back home
            </Link>
        </div>
    )
} 