"use client"

import { useEffect, useState } from "react"
import { submitFeedback } from "@/api/interviews"
import { getCandidates } from "@/api/candidates"
import { getRoles } from "@/api/roles"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"

export default function InterviewsPage() {
    const [interviews, setInterviews] = useState([])
    const [candidates, setCandidates] = useState([])
    const [roles, setRoles] = useState([])
    const [isSubmitting, setIsSubmitting] = useState(false)

    // Feedback Form State
    const [showFeedbackForm, setShowFeedbackForm] = useState(false)
    const [formData, setFormData] = useState({
        candidate_id: "",
        role_id: "",
        interviewer_name: "",
        communication_score: 5,
        knowledge_score: 5,
        confidence_score: 5,
        feedback: ""
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
            console.error("Failed to fetch interview data:", error)
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setIsSubmitting(true)
        try {
            await submitFeedback({
                ...formData,
                communication_score: Number(formData.communication_score),
                knowledge_score: Number(formData.knowledge_score),
                confidence_score: Number(formData.confidence_score),
                candidate_id: Number(formData.candidate_id),
                role_id: Number(formData.role_id)
            })
            setShowFeedbackForm(false)
            setFormData({
                candidate_id: "",
                role_id: "",
                interviewer_name: "",
                communication_score: 5,
                knowledge_score: 5,
                confidence_score: 5,
                feedback: ""
            })
            alert("Feedback submitted successfully!")
            fetchData()
        } catch (error) {
            console.error("Failed to submit feedback:", error)
            alert("Failed to submit feedback")
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold tracking-tight">Interview Management</h2>
                <Button onClick={() => setShowFeedbackForm(!showFeedbackForm)}>
                    {showFeedbackForm ? "Cancel" : <><Plus className="mr-2 h-4 w-4" /> Submit Feedback</>}
                </Button>
            </div>

            {showFeedbackForm && (
                <Card>
                    <CardHeader>
                        <CardTitle>Submit Interview Feedback</CardTitle>
                        <CardDescription>Record your evaluation of a candidate.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="grid gap-2">
                                    <label className="text-sm font-medium">Candidate</label>
                                    <select
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                        required
                                        value={formData.candidate_id}
                                        onChange={(e) => setFormData({ ...formData, candidate_id: e.target.value })}
                                    >
                                        <option value="">Select Candidate</option>
                                        {candidates.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                    </select>
                                </div>
                                <div className="grid gap-2">
                                    <label className="text-sm font-medium">Role</label>
                                    <select
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                        required
                                        value={formData.role_id}
                                        onChange={(e) => setFormData({ ...formData, role_id: e.target.value })}
                                    >
                                        <option value="">Select Role</option>
                                        {roles.map(r => <option key={r.id} value={r.id}>{r.title}</option>)}
                                    </select>
                                </div>
                            </div>

                            <div className="grid gap-2">
                                <label className="text-sm font-medium">Interviewer Name</label>
                                <input
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    required
                                    value={formData.interviewer_name}
                                    onChange={(e) => setFormData({ ...formData, interviewer_name: e.target.value })}
                                />
                            </div>

                            <div className="grid grid-cols-3 gap-4">
                                <div className="grid gap-2">
                                    <label className="text-sm font-medium">Communication (1-10)</label>
                                    <input type="number" min="1" max="10" className="flex h-10 w-full rounded-md border border-input px-3" value={formData.communication_score} onChange={(e) => setFormData({ ...formData, communication_score: e.target.value })} />
                                </div>
                                <div className="grid gap-2">
                                    <label className="text-sm font-medium">Knowledge (1-10)</label>
                                    <input type="number" min="1" max="10" className="flex h-10 w-full rounded-md border border-input px-3" value={formData.knowledge_score} onChange={(e) => setFormData({ ...formData, knowledge_score: e.target.value })} />
                                </div>
                                <div className="grid gap-2">
                                    <label className="text-sm font-medium">Confidence (1-10)</label>
                                    <input type="number" min="1" max="10" className="flex h-10 w-full rounded-md border border-input px-3" value={formData.confidence_score} onChange={(e) => setFormData({ ...formData, confidence_score: e.target.value })} />
                                </div>
                            </div>

                            <div className="grid gap-2">
                                <label className="text-sm font-medium">Feedback Notes</label>
                                <textarea
                                    className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                    required
                                    value={formData.feedback}
                                    onChange={(e) => setFormData({ ...formData, feedback: e.target.value })}
                                />
                            </div>

                            <Button type="submit" disabled={isSubmitting}>Submit Evaluation</Button>
                        </form>
                    </CardContent>
                </Card>
            )}

            {/* List existing interviews if API supports it */}
            <h3 className="text-lg font-semibold">Recent Interviews</h3>
            {interviews.length === 0 ? (
                <p className="text-muted-foreground">No interviews recorded yet.</p>
            ) : (
                <div className="grid gap-4">
                    {/* Map over interviews and display cards */}
                    {interviews.map((interview) => (
                        <Card key={interview.id}>
                            <CardHeader>
                                <CardTitle>Interview #{interview.id}</CardTitle>
                                <CardDescription>Interviewer: {interview.interviewer_name}</CardDescription>
                            </CardHeader>
                            {/* Add content if needed */}
                        </Card>
                    ))}
                </div>
            )}
        </div>
    )
}
