"use client"

import { useEffect, useState } from "react"
import { getCandidates } from "@/api/candidates"
import { getRoles } from "@/api/roles"
import { getCandidate } from "@/api/candidates"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "lucide-react"

// Simple Badge component since I didn't create one in ui/badge.jsx
function StatusBadge({ status }) {
    const colors = {
        'Applied': 'bg-blue-100 text-blue-800',
        'Shortlisted': 'bg-green-100 text-green-800',
        'Interview': 'bg-purple-100 text-purple-800',
        'Rejected': 'bg-red-100 text-red-800',
        'Hired': 'bg-emerald-100 text-emerald-800',
    }
    const colorClass = colors[status] || 'bg-gray-100 text-gray-800'

    return (
        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${colorClass}`}>
            {status}
        </span>
    )
}

export default function CandidatesPage() {
    const [candidates, setCandidates] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchCandidates()
    }, [])

    const fetchCandidates = async () => {
        try {
            const data = await getCandidates()
            setCandidates(data)
        } catch (error) {
            console.error("Failed to fetch candidates:", error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) return <div className="p-8">Loading candidates...</div>

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold tracking-tight">Candidates</h2>
                <Button asChild>
                    {/* Direct link to public portal for manual entry? Or maybe a separate admin add? */}
                    {/* For now, just a refresh button or link to careers page */}
                    <Link href="/careers" target="_blank">View Public Portal</Link>
                </Button>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>All Applications</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="relative w-full overflow-auto">
                        <table className="w-full caption-bottom text-sm text-left">
                            <thead className="[&_tr]:border-b">
                                <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                                    <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Name</th>
                                    <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Title</th>
                                    <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Score</th>
                                    <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Stage</th>
                                    <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="[&_tr:last-child]:border-0">
                                {candidates.map((candidate) => (
                                    <tr key={candidate.id} className="border-b transition-colors hover:bg-muted/50">
                                        <td className="p-4 align-middle font-medium">{candidate.name}</td>
                                        <td className="p-4 align-middle">{candidate.role_id}</td>
                                        {/* Ideally fetch role name, but ID is fine for MVP */}
                                        <td className="p-4 align-middle">
                                            {/* Assuming candidate has a score field or we need to fetch it? */}
                                            {candidate.score ? candidate.score.toFixed(1) : '-'}
                                        </td>
                                        <td className="p-4 align-middle">
                                            <StatusBadge status={candidate.stage || 'Applied'} />
                                        </td>
                                        <td className="p-4 align-middle">
                                            <Button variant="outline" size="sm" asChild>
                                                <Link href={`/candidates/${candidate.id}`}>View</Link>
                                            </Button>
                                        </td>
                                    </tr>
                                ))}
                                {candidates.length === 0 && (
                                    <tr>
                                        <td colSpan={5} className="p-4 text-center text-muted-foreground">
                                            No candidates found.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
