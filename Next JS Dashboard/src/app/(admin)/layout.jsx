import { Sidebar } from "@/components/Sidebar"

export default function AdminLayout({ children }) {
    return (
        <div className="flex h-screen overflow-hidden bg-gray-50/50">
            <Sidebar />
            <main className="flex-1 overflow-y-auto">
                <div className="container mx-auto p-6 md:p-8 max-w-7xl">
                    {children}
                </div>
            </main>
        </div>
    )
}
