"use client"

import { useEffect, useState } from "react"
import { getRoles } from "@/api/roles"
import Link from "next/link"
import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Briefcase } from "lucide-react"

export default function CareersPage() {
    const [roles, setRoles] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function fetchRoles() {
            try {
                const data = await getRoles()
                setRoles(data)
            } catch (error) {
                console.error("Failed to fetch roles:", error)
            } finally {
                setLoading(false)
            }
        }
        fetchRoles()
    }, [])

    if (loading) return <div className="py-12 text-center">Loading open positions...</div>

    return (
        <div className="space-y-8">
            <div className="text-center space-y-4">
                <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">
                    Join Our Team
                </h1>
                <p className="text-xl text-muted-foreground w-full max-w-2xl mx-auto">
                    Explore exciting opportunities and be part of our mission to revolutionize HR tech.
                </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 pt-8">
                {roles.map((role) => (
                    <Card key={role.id} className="flex flex-col">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Briefcase className="h-5 w-5 text-primary" />
                                {role.title}
                            </CardTitle>
                            <CardDescription>{role.experience_required} years experience</CardDescription>
                        </CardHeader>
                        <CardContent className="flex-1">
                            <p className="text-muted-foreground line-clamp-3">
                                {role.description}
                            </p>
                            <div className="mt-4 flex flex-wrap gap-2">
                                {role.required_skills?.map((skill, i) => (
                                    <span key={i} className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80">
                                        {skill}
                                    </span>
                                ))}
                            </div>
                        </CardContent>
                        <CardFooter>
                            <Button className="w-full" asChild>
                                <Link href={`/careers/apply/${role.id}`}>Apply Now</Link>
                            </Button>
                        </CardFooter>
                    </Card>
                ))}
                {roles.length === 0 && (
                    <div className="col-span-full text-center py-12 text-muted-foreground">
                        No open positions at the moment. Check back later!
                    </div>
                )}
            </div>
        </div>
    )
}
