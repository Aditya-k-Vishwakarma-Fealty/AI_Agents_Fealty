"use client"

import { useEffect, useState, use } from "react"
import { useRouter } from "next/navigation"
import { getCandidate, updateCandidateStage, getCandidateScores } from "@/api/candidates"
import { getCandidateInterviews } from "@/api/interviews"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { ArrowLeft, User, Mail, Phone, FileText, CheckCircle, XCircle, Clock, Calendar } from "lucide-react"
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
        <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${colorClass}`}>
            {status}
        </span>
    )
}

export default function CandidateDetailPage({ params }) {
    // Unwrap params using React.use() for Next.js 15+ compatibility
    // checking if params is a promise (Next.js 15) or object (older) to be safe, though Next 15 requires awaiting params in server components or unwrapping in client
    // In client components, params is passed as a promise in recent Next.js versions but let's handle standard prop access first or use `use` hook if available/needed.
    // Actually, for client components in Next.js 15, we should unwrap it.
    // The safest way in a client component for [id] is effectively to use `use` if it's a promise,
    // or just access it if it's already resolved (which it sometimes is in older versions).
    // Let's assume standard behavior for now.

    // NOTE: In Next.js 15, params is a Promise. We need to unwrap it using `use` hook from React.
    const { id } = use(params)

    const router = useRouter()
    const [candidate, setCandidate] = useState(null)
    const [scores, setScores] = useState([])
    const [interviews, setInterviews] = useState([])
    const [loading, setLoading] = useState(true)
    const [activeTab, setActiveTab] = useState('overview')

    useEffect(() => {
        if (id) {
            fetchData(id)
        }
    }, [id])

    const fetchData = async (candidateId) => {
        try {
            setLoading(true)
            const [candidateData, scoresData, interviewsData] = await Promise.all([
                getCandidate(candidateId),
                getCandidateScores(candidateId),
                getCandidateInterviews(candidateId)
            ])
            setCandidate(candidateData)
            setScores(scoresData || [])
            setInterviews(interviewsData || [])
        } catch (error) {
            console.error("Failed to fetch candidate details:", error)
        } finally {
            setLoading(false)
        }
    }

    const handleStageUpdate = async (newStage) => {
        if (!confirm(`Are you sure you want to move candidate to ${newStage}?`)) return

        try {
            const result = await updateCandidateStage(candidate.id, newStage)
            if (result.status === "success") {
                setCandidate({ ...candidate, current_stage: newStage })
                alert(`Candidate moved to ${newStage}`)
            }
        } catch (error) {
            alert("Failed to update status")
        }
    }

    if (loading) return <div className="p-8 flex justify-center">Loading candidate details...</div>
    if (!candidate) return <div className="p-8">Candidate not found</div>

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" onClick={() => router.back()}>
                    <ArrowLeft className="h-4 w-4" />
                </Button>
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{candidate.name}</h2>
                    <p className="text-muted-foreground">ID: {candidate.id}</p>
                </div>
                <div className="ml-auto flex items-center gap-2">
                    <StatusBadge status={candidate.current_stage} />
                    {candidate.current_stage !== 'Rejected' && candidate.current_stage !== 'Hired' && (
                        <div className="flex gap-2">
                            <Button variant="destructive" size="sm" onClick={() => handleStageUpdate('Rejected')}>
                                Reject
                            </Button>
                            {candidate.current_stage === 'Applied' && (
                                <Button size="sm" onClick={() => handleStageUpdate('Shortlisted')}>
                                    Shortlist
                                </Button>
                            )}
                            {/* Add more transitions based on logic */}
                        </div>
                    )}
                </div>
            </div>

            {/* Tabs Navigation */}
            <div className="border-b">
                <div className="flex space-x-8">
                    {['overview', 'scores', 'interviews'].map((tab) => (
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

            {/* Content Area */}
            <div className="mt-6">
                {activeTab === 'overview' && (
                    <div className="grid gap-6 md:grid-cols-2">
                        <Card>
                            <CardHeader>
                                <CardTitle>Contact Information</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex items-center gap-3">
                                    <Mail className="h-4 w-4 text-muted-foreground" />
                                    <span>{candidate.email}</span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <Phone className="h-4 w-4 text-muted-foreground" />
                                    <span>{candidate.phone || 'No phone provided'}</span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <FileText className="h-4 w-4 text-muted-foreground" />
                                    <a
                                        href={`https://ai-agents-fealty.onrender.com/candidates/${candidate.id}/resume`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-blue-600 hover:underline"
                                    >
                                        View Resume
                                    </a>
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Application Details</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex justify-between border-b pb-2">
                                    <span className="text-muted-foreground">Applied Date</span>
                                    <span>{new Date().toLocaleDateString()}</span> {/* Mock date if not in DB */}
                                </div>
                                <div className="flex justify-between border-b pb-2">
                                    <span className="text-muted-foreground">Current Stage</span>
                                    <span>{candidate.current_stage}</span>
                                </div>
                                <div className="flex justify-between border-b pb-2">
                                    <span className="text-muted-foreground">Status</span>
                                    <span>{candidate.status}</span>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                )}

                {activeTab === 'scores' && (
                    <div className="space-y-6">
                        {scores.length === 0 ? (
                            <p className="text-muted-foreground">No scores available yet.</p>
                        ) : (
                            scores.map((score, index) => (
                                <Card key={index}>
                                    <CardHeader>
                                        <CardTitle>Role Evaluation</CardTitle>
                                        <CardDescription>Role ID: {score.role_id}</CardDescription>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="grid gap-6 md:grid-cols-3 mb-6">
                                            <div className="text-center p-4 bg-gray-50 rounded-lg">
                                                <div className="text-3xl font-bold text-blue-600">{score.resume_score}</div>
                                                <div className="text-sm text-muted-foreground">Resume Score</div>
                                            </div>
                                            <div className="text-center p-4 bg-gray-50 rounded-lg">
                                                <div className="text-3xl font-bold text-purple-600">{score.match_percentage}%</div>
                                                <div className="text-sm text-muted-foreground">Match %</div>
                                            </div>
                                        </div>

                                        <div className="space-y-4">
                                            <div>
                                                <h4 className="font-semibold mb-2 flex items-center gap-2">
                                                    <CheckCircle className="h-4 w-4 text-green-600" /> Strengths
                                                </h4>
                                                <ul className="list-disc list-inside text-sm text-gray-700 ml-2">
                                                    {Array.isArray(score.strengths)
                                                        ? score.strengths.map((s, i) => <li key={i}>{s}</li>)
                                                        : <li>{score.strengths}</li>
                                                    }
                                                </ul>
                                            </div>
                                            <div>
                                                <h4 className="font-semibold mb-2 flex items-center gap-2">
                                                    <XCircle className="h-4 w-4 text-red-600" /> Gaps
                                                </h4>
                                                <ul className="list-disc list-inside text-sm text-gray-700 ml-2">
                                                    {Array.isArray(score.gaps)
                                                        ? score.gaps.map((g, i) => <li key={i}>{g}</li>)
                                                        : <li>{score.gaps}</li>
                                                    }
                                                </ul>
                                            </div>
                                            <div className="bg-muted p-4 rounded-md">
                                                <h4 className="font-semibold mb-2">AI Reasoning</h4>
                                                <p className="text-sm text-gray-700">{score.ai_reasoning}</p>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))
                        )}
                    </div>
                )}

                {activeTab === 'interviews' && (
                    <div className="space-y-6">
                        {interviews.length === 0 ? (
                            <Card>
                                <CardContent className="p-8 text-center">
                                    <p className="text-muted-foreground mb-4">No interviews conducted yet.</p>
                                    <Button asChild>
                                        <Link href={`/interviews/schedule?candidateId=${candidate.id}&roleId=${scores[0]?.role_id || ''}`}>
                                            Schedule Interview
                                        </Link>
                                    </Button>
                                </CardContent>
                            </Card>
                        ) : (
                            interviews.map((interview) => (
                                <Card key={interview.id}>
                                    <CardHeader className="flex flex-row items-center justify-between">
                                        <div>
                                            <CardTitle>Interview #{interview.id}</CardTitle>
                                            <CardDescription>
                                                {new Date(interview.interview_date).toLocaleDateString()} • {interview.interviewer_name || 'AI Interviewer'}
                                            </CardDescription>
                                        </div>
                                        <Button variant="outline" asChild>
                                            <Link href={`/interviews/${interview.id}`}>View Details</Link>
                                        </Button>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="grid grid-cols-4 gap-4 mb-4">
                                            <div className="p-3 bg-gray-50 rounded text-center">
                                                <div className="font-bold text-lg">{interview.overall_score}</div>
                                                <div className="text-xs text-muted-foreground">Overall</div>
                                            </div>
                                            <div className="p-3 bg-gray-50 rounded text-center">
                                                <div className="font-bold text-lg">{interview.communication_score}</div>
                                                <div className="text-xs text-muted-foreground">Comm.</div>
                                            </div>
                                            <div className="p-3 bg-gray-50 rounded text-center">
                                                <div className="font-bold text-lg">{interview.knowledge_score}</div>
                                                <div className="text-xs text-muted-foreground">Knowledge</div>
                                            </div>
                                            <div className="p-3 bg-gray-50 rounded text-center">
                                                <div className="font-bold text-lg">{interview.confidence_score}</div>
                                                <div className="text-xs text-muted-foreground">Confidence</div>
                                            </div>
                                        </div>
                                        {interview.feedback && (
                                            <div>
                                                <h4 className="text-sm font-semibold mb-1">Feedback</h4>
                                                <p className="text-sm text-gray-700 line-clamp-2">{interview.feedback}</p>
                                            </div>
                                        )}
                                    </CardContent>
                                </Card>
                            ))
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}
