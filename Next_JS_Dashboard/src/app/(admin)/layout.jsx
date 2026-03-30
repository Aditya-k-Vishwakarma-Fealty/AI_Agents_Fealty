import { Sidebar } from "@/components/Sidebar"

export default function AdminLayout({ children }) {
  return (
    <div className="flex min-h-screen overflow-hidden bg-[radial-gradient(ellipse_120%_80%_at_50%_-20%,rgba(37,99,235,0.08),transparent)]">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 md:px-8 md:py-8">
          {children}
        </div>
      </main>
    </div>
  )
}
