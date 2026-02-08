"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { getRole } from "@/api/roles"
import { createCandidate } from "@/api/candidates"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { ArrowLeft, Upload, CheckCircle } from "lucide-react"
import Link from "next/link"

export default function ApplyPage() {
    const params = useParams()
    const router = useRouter()
    const roleId = params.roleId

    const [role, setRole] = useState(null)
    const [loading, setLoading] = useState(true)
    const [submitting, setSubmitting] = useState(false)
    const [success, setSuccess] = useState(false)

    const [formData, setFormData] = useState({
        name: "",
        email: "",
        phone: "",
    })
    const [resume, setResume] = useState(null)

    useEffect(() => {
        async function fetchRole() {
            if (!roleId) return
            try {
                const data = await getRole(roleId)
                setRole(data)
            } catch (error) {
                console.error("Failed to fetch role:", error)
            } finally {
                setLoading(false)
            }
        }
        fetchRole()
    }, [roleId])

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!resume) {
            alert("Please upload a resume")
            return
        }

        setSubmitting(true)
        try {
            const data = new FormData()
            data.append("name", formData.name)
            data.append("email", formData.email)
            data.append("phone", formData.phone)
            data.append("resume", resume)
            // The backend now accepts role_id to trigger specific role evaluation/scoring
            data.append("role_id", roleId)

            await createCandidate(data)
            setSuccess(true)
        } catch (error) {
            console.error("Failed to submit application:", error)
            const message = error.response?.data?.detail || "Failed to submit application. Please try again."
            alert(message)
        } finally {
            setSubmitting(false)
        }
    }

    if (loading) return <div className="py-12 text-center">Loading role details...</div>
    if (!role) return <div className="py-12 text-center">Role not found</div>

    if (success) {
        return (
            <div className="max-w-md mx-auto py-12 text-center space-y-4">
                <div className="flex justify-center">
                    <CheckCircle className="h-16 w-16 text-green-500" />
                </div>
                <h2 className="text-2xl font-bold">Application Submitted!</h2>
                <p className="text-muted-foreground">
                    Thanks for applying to the <strong>{role.title}</strong> position.
                    We have received your application and will be in touch soon.
                </p>
                <Button asChild className="mt-4">
                    <Link href="/careers">Back to Careers</Link>
                </Button>
            </div>
        )
    }

    return (
        <div className="max-w-3xl mx-auto space-y-8">
            <Button variant="ghost" size="sm" asChild className="pl-0 hover:bg-transparent">
                <Link href="/careers" className="flex items-center gap-2 text-muted-foreground hover:text-foreground">
                    <ArrowLeft className="h-4 w-4" /> Back to Jobs
                </Link>
            </Button>

            <div className="space-y-4">
                <h1 className="text-3xl font-bold">{role.title}</h1>
                <div className="flex gap-2">
                    <span className="inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80">
                        {role.experience_required} Years Experience
                    </span>
                </div>
                <div className="prose prose-gray max-w-none text-muted-foreground">
                    {role.description}
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Apply for this position</CardTitle>
                    <CardDescription>Fill out the form below to submit your application.</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="grid gap-4 md:grid-cols-2">
                            <div className="grid gap-2">
                                <label className="text-sm font-medium">Full Name</label>
                                <input
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    required
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                />
                            </div>
                            <div className="grid gap-2">
                                <label className="text-sm font-medium">Email</label>
                                <input
                                    type="email"
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    required
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                />
                            </div>
                        </div>

                        <div className="grid gap-2">
                            <label className="text-sm font-medium">Phone</label>
                            <input
                                type="tel"
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                required
                                value={formData.phone}
                                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                            />
                        </div>

                        <div className="grid gap-2">
                            <label className="text-sm font-medium">Resume (PDF or DOCX)</label>
                            <div className="flex items-center justify-center w-full">
                                <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 border-gray-300">
                                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                        <Upload className="w-8 h-8 mb-4 text-gray-500" />
                                        <p className="mb-2 text-sm text-gray-500"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                                        <p className="text-xs text-gray-500">
                                            {resume ? resume.name : "PDF or DOCX (MAX. 5MB)"}
                                        </p>
                                    </div>
                                    <input
                                        type="file"
                                        className="hidden"
                                        accept=".pdf,.docx,.doc"
                                        onChange={(e) => setResume(e.target.files[0])}
                                    />
                                </label>
                            </div>
                        </div>

                        <Button type="submit" className="w-full" disabled={submitting}>
                            {submitting ? "Submitting..." : "Submit Application"}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    )
}
