
export const Login = () => {
    const handleLoginRedirect = () => {
        // Redirect to Frappe's login page
        window.location.href = `${import.meta.env.VITE_FRAPPE_PATH}/login`
    }
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-sm text-center">
                <div>
                    <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        Raven Cloud Development
                    </h2>
                    <p className="text-gray-600 mb-6">
                       Login page is in development, please use the Frappe login page.
                    </p>
                </div>
                
                <button className="w-full bg-black text-white font-medium py-2 px-4 rounded-md cursor-pointer" onClick={handleLoginRedirect}>
                    Go to Frappe Login
                </button>
            </div>
        </div>
    )
}