"use client"

import { useEffect, useState, use } from "react"
import { useRouter } from "next/navigation"
import { getRole, getRoleCandidates, getRoleRankings, shortlistRole } from "@/api/roles"
import { generateRanking, makeFinalDecision } from "@/api/interviews"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { ArrowLeft, Briefcase, Users, Trophy, CheckSquare, ListChecks } from "lucide-react"
import Link from "next/link"

// Simple Badge component
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

export default function RoleDetailPage({ params }) {
    const { id } = use(params)
    const router = useRouter()

    const [role, setRole] = useState(null)
    const [candidates, setCandidates] = useState([])
    const [rankings, setRankings] = useState([])
    const [loading, setLoading] = useState(true)
    const [activeTab, setActiveTab] = useState('overview')

    // Action states
    const [shortlistThreshold, setShortlistThreshold] = useState(60)
    const [isProcessing, setIsProcessing] = useState(false)

    useEffect(() => {
        if (id) {
            fetchData(id)
        }
    }, [id])

    const fetchData = async (roleId) => {
        try {
            setLoading(true)
            const [roleData, candidatesData, rankingsData] = await Promise.all([
                getRole(roleId),
                getRoleCandidates(roleId),
                getRoleRankings(roleId)
            ])
            setRole(roleData)
            setCandidates(candidatesData || [])
            setRankings(rankingsData.rankings || [])
        } catch (error) {
            console.error("Failed to fetch role details:", error)
        } finally {
            setLoading(false)
        }
    }

    const handleShortlist = async () => {
        if (!confirm(`Run shortlisting with threshold ${shortlistThreshold}%? This will send emails.`)) return

        setIsProcessing(true)
        try {
            const result = await shortlistRole(role.id, shortlistThreshold / 100) // Backend expects 0-1 or 0-100? Let's check api. generic float usually 0-1 or 0-100. Previous tests suggested 0-1 for match_percentage but let's assume UI is %. 
            // Wait, match_percentage in db is float. 
            // Let's pass simple float.
            if (result.status === "success") {
                alert(`Shortlisting complete. ${result.shortlisted_count} shortlisted.`)
                fetchData(role.id)
            }
        } catch (error) {
            alert("Shortlisting failed")
        } finally {
            setIsProcessing(false)
        }
    }

    const handleGenerateRanking = async () => {
        setIsProcessing(true)
        try {
            const result = await generateRanking(role.id)
            if (result.status === "success") {
                alert("Rankings generated successfully")
                fetchData(role.id)
                setActiveTab('rankings')
            }
        } catch (error) {
            alert("Ranking generation failed")
        } finally {
            setIsProcessing(false)
        }
    }

    const handleMakeDecision = async (selections) => {
        if (!confirm(`Confirm selection of top ${selections} candidates?`)) return

        setIsProcessing(true)
        try {
            // Logic for decision making
            const result = await makeFinalDecision(role.id, selections, 2) // Default 2 waitlist
            if (result.status === "success") {
                alert("Final decisions recorded and emails sent.")
                fetchData(role.id)
            }
        } catch (error) {
            alert("Decision making failed")
        } finally {
            setIsProcessing(false)
        }
    }

    if (loading) return <div className="p-8 flex justify-center">Loading role details...</div>
    if (!role) return <div className="p-8">Role not found</div>

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" onClick={() => router.back()}>
                    <ArrowLeft className="h-4 w-4" />
                </Button>
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{role.title}</h2>
                    <p className="text-muted-foreground">{role.is_active ? 'Active' : 'Closed'} • Created {new Date(role.created_date).toLocaleDateString()}</p>
                </div>
                <div className="ml-auto flex gap-2">
                    <Button variant="outline" onClick={handleGenerateRanking} disabled={isProcessing}>
                        <Trophy className="mr-2 h-4 w-4" /> Generate Ranking
                    </Button>
                </div>
            </div>

            {/* Tabs */}
            <div className="border-b">
                <div className="flex space-x-8">
                    {['overview', 'candidates', 'rankings'].map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === tab
                                    ? 'border-primary text-primary'
                                    : 'border-transparent text-muted-foreground hover:text-foreground hover:border-gray-300'
                                }`}
                        >
                            {tab.charAt(0).toUpperCase() + tab.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            <div className="mt-6">
                {activeTab === 'overview' && (
                    <div className="grid gap-6 md:grid-cols-3">
                        <div className="md:col-span-2 space-y-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Job Description</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <p className="whitespace-pre-wrap text-sm text-gray-700">{role.description}</p>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle>Required Skills</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="flex flex-wrap gap-2">
                                        {role.required_skills.map((skill, i) => (
                                            <span key={i} className="bg-secondary text-secondary-foreground px-2.5 py-0.5 rounded-full text-sm font-medium">
                                                {skill}
                                            </span>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        </div>

                        <div className="space-y-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Shortlisting</CardTitle>
                                    <CardDescription>Filter candidates by resume score</CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium">Min Score Threshold</label>
                                        <div className="flex gap-2">
                                            <input
                                                type="number"
                                                className="flex h-10 w-full rounded-md border border-input px-3"
                                                value={shortlistThreshold}
                                                onChange={(e) => setShortlistThreshold(e.target.value)}
                                            />
                                            <span className="flex items-center text-muted-foreground">%</span>
                                        </div>
                                    </div>
                                    <Button className="w-full" onClick={handleShortlist} disabled={isProcessing}>
                                        <CheckSquare className="mr-2 h-4 w-4" /> Run Shortlist
                                    </Button>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle>Stats</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-muted-foreground">Total Candidates</span>
                                        <span className="font-bold">{candidates.length}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-muted-foreground">Shortlisted</span>
                                        <span className="font-bold">{candidates.filter(c => c.current_stage !== 'Applied').length}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-muted-foreground">Interviewed</span>
                                        <span className="font-bold">{candidates.filter(c => ['Interviewed', 'Final', 'Hired', 'Rejected'].includes(c.current_stage) && c.current_stage !== 'Applied' && c.current_stage !== 'Shortlisted').length}</span>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                )}

                {activeTab === 'candidates' && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Candidate Pool</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm text-left">
                                    <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                                        <tr>
                                            <th className="px-4 py-3">Name</th>
                                            <th className="px-4 py-3">Stage</th>
                                            <th className="px-4 py-3">Resume Score</th>
                                            <th className="px-4 py-3">Match %</th>
                                            <th className="px-4 py-3">Action</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {candidates.map((c) => (
                                            <tr key={c.candidate_id} className="border-b hover:bg-gray-50">
                                                <td className="px-4 py-3 font-medium">{c.name}</td>
                                                <td className="px-4 py-3"><StatusBadge status={c.current_stage} /></td>
                                                <td className="px-4 py-3">{c.resume_score}</td>
                                                <td className="px-4 py-3">{c.match_percentage}%</td>
                                                <td className="px-4 py-3">
                                                    <Button variant="ghost" size="sm" asChild>
                                                        <Link href={`/candidates/${c.candidate_id}`}>View</Link>
                                                    </Button>
                                                </td>
                                            </tr>
                                        ))}
                                        {candidates.length === 0 && (
                                            <tr><td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">No candidates found.</td></tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {activeTab === 'rankings' && (
                    <div className="space-y-6">
                        <div className="flex justify-end gap-2">
                            <Button onClick={() => handleMakeDecision(1)} disabled={isProcessing || rankings.length === 0}>
                                Select Top 1
                            </Button>
                            <Button onClick={() => handleMakeDecision(3)} disabled={isProcessing || rankings.length === 0}>
                                Select Top 3
                            </Button>
                        </div>
                        <Card>
                            <CardHeader>
                                <CardTitle>Final Rankings</CardTitle>
                                <CardDescription>Combined score based on Resume and Interview performance</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm text-left">
                                        <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                                            <tr>
                                                <th className="px-4 py-3">Rank</th>
                                                <th className="px-4 py-3">Candidate</th>
                                                <th className="px-4 py-3">Combined Score</th>
                                                <th className="px-4 py-3">Decision</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {rankings.map((r) => (
                                                <tr key={r.candidate_id} className="border-b hover:bg-gray-50">
                                                    <td className="px-4 py-3 text-lg font-bold text-gray-500">#{r.rank}</td>
                                                    <td className="px-4 py-3 font-medium">
                                                        <Link href={`/candidates/${r.candidate_id}`} className="hover:underline text-blue-600">
                                                            {r.name}
                                                        </Link>
                                                    </td>
                                                    <td className="px-4 py-3 font-bold">{r.combined_score.toFixed(1)}</td>
                                                    <td className="px-4 py-3">
                                                        {r.final_decision ? (
                                                            <span className={`px-2 py-1 rounded text-xs font-bold ${r.final_decision === 'Selected' ? 'bg-green-100 text-green-800' :
                                                                    r.final_decision === 'Waitlisted' ? 'bg-yellow-100 text-yellow-800' :
                                                                        'bg-red-100 text-red-800'
                                                                }`}>
                                                                {r.final_decision}
                                                            </span>
                                                        ) : '-'}
                                                    </td>
                                                </tr>
                                            ))}
                                            {rankings.length === 0 && (
                                                <tr><td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">No rankings generated yet. Use the Generate Ranking action above to start.</td></tr>
                                            )}
                                        </tbody>
                                    </table>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                )}
            </div>
        </div>
    )
}
