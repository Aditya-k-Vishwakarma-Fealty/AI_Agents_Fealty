"use client"

import { useEffect, useState, use } from "react"
import { useRouter } from "next/navigation"
import { getInterview, getEvaluation, syncVoiceCall } from "@/api/interviews"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { ArrowLeft, Mic, RefreshCw, FileText, BarChart } from "lucide-react"

export default function InterviewDetailPage({ params }) {
    const { id } = use(params)
    const router = useRouter()

    const [interview, setInterview] = useState(null)
    const [evaluation, setEvaluation] = useState(null)
    const [loading, setLoading] = useState(true)
    const [syncing, setSyncing] = useState(false)

    useEffect(() => {
        if (id) {
            fetchData(id)
        }
    }, [id])

    const fetchData = async (interviewId) => {
        try {
            setLoading(true)
            const [interviewData, evaluationData] = await Promise.all([
                getInterview(interviewId),
                getEvaluation(interviewId).catch(() => null) // Handle 404 if no eval yet
            ])
            setInterview(interviewData)
            setEvaluation(evaluationData)
        } catch (error) {
            console.error("Failed to fetch interview details:", error)
        } finally {
            setLoading(false)
        }
    }

    const handleSync = async () => {
        if (!interview.voice_session_id) return

        setSyncing(true)
        try {
            const result = await syncVoiceCall(interview.voice_session_id)
            if (result.status === "success") {
                alert("Interview synced successfully")
                fetchData(id)
            } else {
                alert(`Sync failed: ${result.message || 'Unknown error'}`)
            }
        } catch (error) {
            alert("Sync failed")
        } finally {
            setSyncing(false)
        }
    }

    if (loading) return <div className="p-8 flex justify-center">Loading interview details...</div>
    if (!interview) return <div className="p-8">Interview not found</div>

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" onClick={() => router.back()}>
                    <ArrowLeft className="h-4 w-4" />
                </Button>
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Interview #{interview.id}</h2>
                    <p className="text-muted-foreground">{new Date(interview.interview_date).toLocaleString()}</p>
                </div>
                {interview.is_voice_interview && (
                    <div className="ml-auto">
                        <Button variant="outline" onClick={handleSync} disabled={syncing}>
                            <RefreshCw className={`mr-2 h-4 w-4 ${syncing ? 'animate-spin' : ''}`} />
                            Sync with Retell AI
                        </Button>
                    </div>
                )}
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Scores</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 bg-gray-50 rounded-lg text-center">
                                    <div className="text-3xl font-bold text-primary">{interview.overall_score}</div>
                                    <div className="text-sm text-muted-foreground">Overall Score</div>
                                </div>
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span>Communication</span>
                                        <span className="font-bold">{interview.communication_score}</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span>Knowledge</span>
                                        <span className="font-bold">{interview.knowledge_score}</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span>Confidence</span>
                                        <span className="font-bold">{interview.confidence_score}</span>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {evaluation && evaluation.ai_evaluation && (
                        <Card>
                            <CardHeader>
                                <CardTitle>AI Analysis</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="space-y-2">
                                    <h4 className="font-semibold text-sm">Summary</h4>
                                    <p className="text-sm text-gray-700">{evaluation.ai_evaluation.summary}</p>
                                </div>
                                <div className="space-y-2">
                                    <h4 className="font-semibold text-sm">Key Takeaways</h4>
                                    <ul className="list-disc list-inside text-sm text-gray-700">
                                        {/* Assuming structure, handle safely */}
                                        {evaluation.ai_evaluation.key_points && evaluation.ai_evaluation.key_points.map((p, i) => (
                                            <li key={i}>{p}</li>
                                        ))}
                                    </ul>
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </div>

                <div className="space-y-6">
                    {interview.is_voice_interview ? (
                        <Card className="h-full flex flex-col">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Mic className="h-5 w-5" /> Transcript
                                </CardTitle>
                                <CardDescription>
                                    Duration: {interview.voice_duration_seconds ? `${Math.floor(interview.voice_duration_seconds / 60)}m ${interview.voice_duration_seconds % 60}s` : 'Unknown'}
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="flex-1 overflow-auto max-h-[600px]">
                                {interview.voice_transcript ? (
                                    <div className="whitespace-pre-wrap text-sm leading-relaxed p-4 bg-gray-50 rounded-md">
                                        {interview.voice_transcript}
                                    </div>
                                ) : (
                                    <div className="flex flex-col items-center justify-center h-40 text-muted-foreground">
                                        <p>No transcript available.</p>
                                        <p className="text-xs mt-2">Try syncing if the call just finished.</p>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    ) : (
                        <Card>
                            <CardHeader>
                                <CardTitle>Interviewer Feedback</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="whitespace-pre-wrap text-sm">{interview.feedback || "No written feedback provided."}</p>
                            </CardContent>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    )
}
