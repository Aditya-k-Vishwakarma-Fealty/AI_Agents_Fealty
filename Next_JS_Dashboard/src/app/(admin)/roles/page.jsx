"use client"

import { useEffect, useState } from "react"
import { getRoles, createRole } from "@/api/roles"
import { Card, CardContent, CardHeader, CardTitle, CardFooter, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Plus, Users } from "lucide-react"
import Link from "next/link"

export default function RolesPage() {
    const [roles, setRoles] = useState([])
    const [isCreating, setIsCreating] = useState(false)
    const [formData, setFormData] = useState({
        title: "",
        description: "",
        required_skills: "",
        experience_required: 0,
    })

    const fetchRoles = async () => {
        try {
            const data = await getRoles()
            setRoles(data)
        } catch (error) {
            console.error("Failed to fetch roles:", error)
        }
    }

    useEffect(() => {
        let cancelled = false
        getRoles()
            .then((data) => {
                if (!cancelled) setRoles(Array.isArray(data) ? data : [])
            })
            .catch((error) => {
                console.error("Failed to fetch roles:", error)
            })
        return () => {
            cancelled = true
        }
    }, [])

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            // Convert comma-separated skills to array if backend expects array, 
            // or keep as string if backend parses it. 
            // Plan says: "Required Skills (Tag Input / Comma separated)"
            // Let's assume backend expects a list or we send as is? 
            // The curl example in README shows: "required_skills": ["Python", ...]
            const payload = {
                ...formData,
                required_skills: formData.required_skills.split(',').map(s => s.trim()),
                experience_required: Number(formData.experience_required)
            }

            await createRole(payload)
            setIsCreating(false)
            setFormData({ title: "", description: "", required_skills: "", experience_required: 0 })
            fetchRoles() // Refresh list
        } catch (error) {
            console.error("Failed to create role:", error)
            alert("Failed to create role")
        }
    }

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold tracking-tight">Job Roles</h2>
                <Button onClick={() => setIsCreating(!isCreating)}>
                    {isCreating ? "Cancel" : <><Plus className="mr-2 h-4 w-4" /> Create Role</>}
                </Button>
            </div>

            {isCreating && (
                <Card>
                    <CardHeader>
                        <CardTitle>Create New Role</CardTitle>
                        <CardDescription>Define the requirements for the new position.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="grid gap-2">
                                <label className="text-sm font-medium">Job Title</label>
                                <input
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    required
                                    value={formData.title}
                                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                />
                            </div>
                            <div className="grid gap-2">
                                <label className="text-sm font-medium">Description</label>
                                <textarea
                                    className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    required
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="grid gap-2">
                                    <label className="text-sm font-medium">Required Skills (comma separated)</label>
                                    <input
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                        placeholder="Python, React, SQL"
                                        required
                                        value={formData.required_skills}
                                        onChange={(e) => setFormData({ ...formData, required_skills: e.target.value })}
                                    />
                                </div>
                                <div className="grid gap-2">
                                    <label className="text-sm font-medium">Experience (Years)</label>
                                    <input
                                        type="number"
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                        required
                                        value={formData.experience_required}
                                        onChange={(e) => setFormData({ ...formData, experience_required: e.target.value })}
                                    />
                                </div>
                            </div>
                            <Button type="submit">Save Role</Button>
                        </form>
                    </CardContent>
                </Card>
            )}

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {roles.map((role) => (
                    <Card key={role.id}>
                        <CardHeader>
                            <CardTitle>{role.title}</CardTitle>
                            <CardDescription>{role.experience_required} years exp.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground line-clamp-3 mb-4">
                                {role.description}
                            </p>
                            <div className="flex flex-wrap gap-2">
                                {role.required_skills?.map((skill, i) => (
                                    <span key={i} className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80">
                                        {skill}
                                    </span>
                                ))}
                            </div>
                        </CardContent>
                        <CardFooter className="flex justify-between">
                            <Button variant="outline" size="sm" asChild>
                                <Link href={`/roles/${role.id}`}>View Candidates</Link>
                            </Button>
                        </CardFooter>
                    </Card>
                ))}
                {roles.length === 0 && !isCreating && (
                    <div className="col-span-full text-center text-muted-foreground py-12">
                        No roles found. Create one to get started.
                    </div>
                )}
            </div>
        </div>
    )
}
