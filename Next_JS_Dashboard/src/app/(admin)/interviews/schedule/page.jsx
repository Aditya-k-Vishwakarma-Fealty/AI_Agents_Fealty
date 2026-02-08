"use client"

import { useEffect, useState, use } from "react"
import { useRouter } from "next/navigation"
import { scheduleInterview } from "@/api/interviews"
import { getCandidates } from "@/api/candidates"
import { getRoles } from "@/api/roles"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { ArrowLeft, Calendar, User, Briefcase } from "lucide-react"

export default function ScheduleInterviewPage({ searchParams }) {
    // In Next.js 15, searchParams is a Promise that needs to be unwrapped with React.use()
    const resolvedParams = use(searchParams)
    const initialCandidateId = resolvedParams?.candidateId || ""
    const initialRoleId = resolvedParams?.roleId || ""

    const router = useRouter()
    const [candidates, setCandidates] = useState([])
    const [roles, setRoles] = useState([])
    const [loading, setLoading] = useState(true)
    const [submitting, setSubmitting] = useState(false)

    const [formData, setFormData] = useState({
        candidate_id: initialCandidateId,
        role_id: initialRoleId,
        interview_datetime: "",
    })

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            const [candidatesData, rolesData] = await Promise.all([
                getCandidates(),
                getRoles()
            ])
            setCandidates(Array.isArray(candidatesData) ? candidatesData : [])
            setRoles(Array.isArray(rolesData) ? rolesData : [])
        } catch (error) {
            console.error("Failed to fetch data:", error)
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setSubmitting(true)

        try {
            // Format datetime if needed (backend expects "YYYY-MM-DD HH:MM:SS")
            // The input type="datetime-local" gives "YYYY-MM-DDTHH:MM"
            const formattedDate = formData.interview_datetime.replace("T", " ") + ":00"

            await scheduleInterview({
                candidate_id: Number(formData.candidate_id),
                role_id: Number(formData.role_id),
                interview_datetime: formattedDate
            })

            alert("Interview scheduled successfully! Invitation email sent.")
            router.push(`/candidates/${formData.candidate_id}`)
        } catch (error) {
            console.error("Failed to schedule interview:", error)
            const message = error.response?.data?.detail || "Failed to schedule interview"
            alert(message)
        } finally {
            setSubmitting(false)
        }
    }

    if (loading) return <div className="p-8 text-center">Loading...</div>

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <Button variant="ghost" size="sm" onClick={() => router.back()} className="pl-0">
                <ArrowLeft className="h-4 w-4 mr-2" /> Back
            </Button>

            <Card>
                <CardHeader>
                    <CardTitle>Schedule Interview</CardTitle>
                    <CardDescription>Select a candidate and time for the interview.</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="grid gap-2">
                            <label className="text-sm font-medium flex items-center gap-2">
                                <User className="h-4 w-4" /> Candidate
                            </label>
                            <select
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                required
                                value={formData.candidate_id}
                                onChange={(e) => setFormData({ ...formData, candidate_id: e.target.value })}
                            >
                                <option value="">Select Candidate</option>
                                {candidates.map(c => (
                                    <option key={c.id} value={c.id}>{c.name} ({c.email})</option>
                                ))}
                            </select>
                        </div>

                        <div className="grid gap-2">
                            <label className="text-sm font-medium flex items-center gap-2">
                                <Briefcase className="h-4 w-4" /> Role
                            </label>
                            <select
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                required
                                value={formData.role_id}
                                onChange={(e) => setFormData({ ...formData, role_id: e.target.value })}
                            >
                                <option value="">Select Role</option>
                                {roles.map(r => (
                                    <option key={r.id} value={r.id}>{r.title}</option>
                                ))}
                            </select>
                        </div>

                        <div className="grid gap-2">
                            <label className="text-sm font-medium flex items-center gap-2">
                                <Calendar className="h-4 w-4" /> Date & Time
                            </label>
                            <input
                                type="datetime-local"
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                required
                                value={formData.interview_datetime}
                                onChange={(e) => setFormData({ ...formData, interview_datetime: e.target.value })}
                            />
                            <p className="text-xs text-muted-foreground">
                                Select the time agreed upon with the candidate.
                            </p>
                        </div>

                        <Button type="submit" className="w-full" disabled={submitting}>
                            {submitting ? "Scheduling..." : "Confirm Schedule"}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    )
}
