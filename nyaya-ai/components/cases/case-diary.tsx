"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Plus, FileText, User, MapPin, Scale, Shield, Calendar, Clock, Link, Search, Filter } from "lucide-react"

interface DiaryEntry {
  id: string
  date: string
  time: string
  activityType: string
  title: string
  summary: string
  officer: string
  location: string
  linkedChecklistItem?: string
  linkedEvidence?: string[]
  witnesses?: string[]
  followUpRequired: boolean
  followUpDate?: string
}

interface CaseDiaryProps {
  caseId: string
}

export function CaseDiary({ caseId }: CaseDiaryProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedActivityType, setSelectedActivityType] = useState("all")
  const [isNewEntryDialogOpen, setIsNewEntryDialogOpen] = useState(false)

  // Mock diary entries
  const diaryEntries: DiaryEntry[] = [
    {
      id: "diary-001",
      date: "2025-01-20",
      time: "10:30",
      activityType: "Case Registration",
      title: "FIR Registration and Initial Assessment",
      summary:
        "FIR registered under sections 376, 506 IPC and POCSO Act 2012. Initial assessment completed. Victim is a 17-year-old minor. Case assigned high priority due to POCSO applicability. AI processing of FIR completed successfully.",
      officer: "IO Sharma",
      location: "Police Station - Front Desk",
      linkedChecklistItem: "case-registration",
      linkedEvidence: ["ev-fir-001"],
      witnesses: [],
      followUpRequired: false,
    },
    {
      id: "diary-002",
      date: "2025-01-20",
      time: "14:15",
      activityType: "Victim Interrogation",
      title: "Victim Statement Recording u/s 183 BNSS",
      summary:
        "Detailed statement recorded from victim in presence of support person as per POCSO guidelines. Victim provided comprehensive account of incident. Statement audio recorded and transcribed. Victim appeared consistent and credible. Medical examination arranged immediately.",
      officer: "IO Sharma",
      location: "Police Station - Interview Room 1",
      linkedChecklistItem: "victim-statement",
      linkedEvidence: ["ev-001", "ev-statement-transcript"],
      witnesses: ["Support Person - Ms. Priya Counselor"],
      followUpRequired: false,
    },
    {
      id: "diary-003",
      date: "2025-01-20",
      time: "16:45",
      activityType: "Evidence Collection",
      title: "Medical Examination Report Received",
      summary:
        "Medical examination report received from Dr. Priya Singh, District Hospital. Report confirms physical evidence consistent with victim's statement. All POCSO Act medical examination protocols followed. Report immediately uploaded to evidence locker with proper chain of custody documentation.",
      officer: "IO Sharma",
      location: "District Hospital",
      linkedChecklistItem: "medical-exam",
      linkedEvidence: ["ev-002"],
      witnesses: ["Dr. Priya Singh"],
      followUpRequired: false,
    },
    {
      id: "diary-004",
      date: "2025-01-21",
      time: "09:00",
      activityType: "Investigation Planning",
      title: "Crime Scene Visit Planning",
      summary:
        "Coordinated with forensic team for crime scene examination. Scene preserved and secured. Forensic team briefed on case details and evidence requirements. Visit scheduled for 12:00 PM today. Local area inquiry to be conducted simultaneously.",
      officer: "IO Sharma",
      location: "Police Station - Investigation Room",
      linkedChecklistItem: "crime-scene",
      linkedEvidence: [],
      witnesses: [],
      followUpRequired: true,
      followUpDate: "2025-01-21",
    },
  ]

  const activityTypes = [
    "all",
    "Case Registration",
    "Victim Interrogation",
    "Accused Interrogation",
    "Witness Interrogation",
    "Evidence Collection",
    "Crime Scene Visit",
    "Investigation Planning",
    "Court Proceedings",
    "Other",
  ]

  const getActivityIcon = (activityType: string) => {
    switch (activityType) {
      case "Case Registration":
        return FileText
      case "Victim Interrogation":
      case "Accused Interrogation":
      case "Witness Interrogation":
        return User
      case "Evidence Collection":
        return Shield
      case "Crime Scene Visit":
        return MapPin
      case "Court Proceedings":
        return Scale
      default:
        return FileText
    }
  }

  const getActivityColor = (activityType: string) => {
    switch (activityType) {
      case "Case Registration":
        return "text-blue-500"
      case "Victim Interrogation":
        return "text-green-500"
      case "Accused Interrogation":
        return "text-red-500"
      case "Witness Interrogation":
        return "text-purple-500"
      case "Evidence Collection":
        return "text-amber-500"
      case "Crime Scene Visit":
        return "text-orange-500"
      case "Court Proceedings":
        return "text-indigo-500"
      default:
        return "text-gray-500"
    }
  }

  const filteredEntries = diaryEntries.filter((entry) => {
    const matchesSearch =
      entry.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.summary.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesActivity = selectedActivityType === "all" || entry.activityType === selectedActivityType
    return matchesSearch && matchesActivity
  })

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Case Diary</h2>
          <p className="text-muted-foreground">Structured documentation of all investigation activities</p>
        </div>

        <Dialog open={isNewEntryDialogOpen} onOpenChange={setIsNewEntryDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">
              <Plus className="w-4 h-4 mr-2" />
              New Entry
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Add New Diary Entry</DialogTitle>
              <DialogDescription>Record a new investigation activity with structured details</DialogDescription>
            </DialogHeader>
            <NewDiaryEntryForm onClose={() => setIsNewEntryDialogOpen(false)} />
          </DialogContent>
        </Dialog>
      </div>

      {/* Search and Filter */}
      <Card className="bg-card border-border">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search diary entries by title or content..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-background border-border"
                />
              </div>
            </div>
            <div className="md:w-48">
              <Select value={selectedActivityType} onValueChange={setSelectedActivityType}>
                <SelectTrigger className="bg-background border-border">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {activityTypes.map((type) => (
                    <SelectItem key={type} value={type}>
                      {type === "all" ? "All Activities" : type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Diary Entries Timeline */}
      <div className="space-y-4">
        {filteredEntries.map((entry, index) => {
          const ActivityIcon = getActivityIcon(entry.activityType)
          return (
            <Card key={entry.id} className="bg-card border-border">
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  {/* Timeline indicator */}
                  <div className="flex flex-col items-center">
                    <div className={`p-3 rounded-lg bg-muted/50`}>
                      <ActivityIcon className={`w-5 h-5 ${getActivityColor(entry.activityType)}`} />
                    </div>
                    {index < filteredEntries.length - 1 && <div className="w-0.5 h-8 bg-border mt-2" />}
                  </div>

                  {/* Entry content */}
                  <div className="flex-1 space-y-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold text-foreground">{entry.title}</h3>
                        <div className="flex items-center space-x-4 text-sm text-muted-foreground mt-1">
                          <div className="flex items-center space-x-1">
                            <Calendar className="w-4 h-4" />
                            <span>{entry.date}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Clock className="w-4 h-4" />
                            <span>{entry.time}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <User className="w-4 h-4" />
                            <span>{entry.officer}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <MapPin className="w-4 h-4" />
                            <span>{entry.location}</span>
                          </div>
                        </div>
                      </div>
                      <Badge className={`${getActivityColor(entry.activityType)} bg-opacity-10`}>
                        {entry.activityType}
                      </Badge>
                    </div>

                    <p className="text-muted-foreground leading-relaxed">{entry.summary}</p>

                    {/* Linked items */}
                    <div className="flex flex-wrap gap-4 text-sm">
                      {entry.linkedChecklistItem && (
                        <div className="flex items-center space-x-1">
                          <Link className="w-4 h-4 text-blue-500" />
                          <span className="text-blue-500">Linked to checklist item</span>
                        </div>
                      )}
                      {entry.linkedEvidence && entry.linkedEvidence.length > 0 && (
                        <div className="flex items-center space-x-1">
                          <Shield className="w-4 h-4 text-green-500" />
                          <span className="text-green-500">{entry.linkedEvidence.length} evidence item(s)</span>
                        </div>
                      )}
                      {entry.witnesses && entry.witnesses.length > 0 && (
                        <div className="flex items-center space-x-1">
                          <User className="w-4 h-4 text-purple-500" />
                          <span className="text-purple-500">{entry.witnesses.length} witness(es)</span>
                        </div>
                      )}
                    </div>

                    {/* Follow-up indicator */}
                    {entry.followUpRequired && (
                      <div className="p-3 bg-amber-500/10 rounded-lg border border-amber-500/20">
                        <div className="flex items-center space-x-2">
                          <Clock className="w-4 h-4 text-amber-500" />
                          <span className="text-sm font-medium text-amber-700">Follow-up Required</span>
                          {entry.followUpDate && (
                            <span className="text-sm text-amber-600">by {entry.followUpDate}</span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}

function NewDiaryEntryForm({ onClose }: { onClose: () => void }) {
  const [formData, setFormData] = useState({
    activityType: "",
    title: "",
    summary: "",
    location: "",
    linkedChecklistItem: "",
    witnesses: "",
    followUpRequired: false,
    followUpDate: "",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle form submission logic here
    console.log("Creating diary entry:", formData)
    onClose()
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="activityType">Activity Type</Label>
          <Select
            value={formData.activityType}
            onValueChange={(value) => setFormData({ ...formData, activityType: value })}
          >
            <SelectTrigger className="bg-background border-border">
              <SelectValue placeholder="Select activity type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Victim Interrogation">Victim Interrogation</SelectItem>
              <SelectItem value="Accused Interrogation">Accused Interrogation</SelectItem>
              <SelectItem value="Witness Interrogation">Witness Interrogation</SelectItem>
              <SelectItem value="Evidence Collection">Evidence Collection</SelectItem>
              <SelectItem value="Crime Scene Visit">Crime Scene Visit</SelectItem>
              <SelectItem value="Investigation Planning">Investigation Planning</SelectItem>
              <SelectItem value="Court Proceedings">Court Proceedings</SelectItem>
              <SelectItem value="Other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="location">Location</Label>
          <Input
            id="location"
            placeholder="Where did this activity take place?"
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
            className="bg-background border-border"
            required
          />
        </div>
      </div>

      <div>
        <Label htmlFor="title">Entry Title</Label>
        <Input
          id="title"
          placeholder="Brief title describing the activity"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="bg-background border-border"
          required
        />
      </div>

      <div>
        <Label htmlFor="summary">Detailed Summary</Label>
        <Textarea
          id="summary"
          placeholder="Provide a comprehensive description of the activity, findings, and outcomes"
          value={formData.summary}
          onChange={(e) => setFormData({ ...formData, summary: e.target.value })}
          className="bg-background border-border min-h-[120px]"
          required
        />
      </div>

      <div>
        <Label htmlFor="witnesses">Witnesses Present (comma-separated)</Label>
        <Input
          id="witnesses"
          placeholder="Names of witnesses or persons present during activity"
          value={formData.witnesses}
          onChange={(e) => setFormData({ ...formData, witnesses: e.target.value })}
          className="bg-background border-border"
        />
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="followUpRequired"
          checked={formData.followUpRequired}
          onChange={(e) => setFormData({ ...formData, followUpRequired: e.target.checked })}
          className="rounded border-border"
        />
        <Label htmlFor="followUpRequired">Follow-up action required</Label>
      </div>

      {formData.followUpRequired && (
        <div>
          <Label htmlFor="followUpDate">Follow-up Date</Label>
          <Input
            id="followUpDate"
            type="date"
            value={formData.followUpDate}
            onChange={(e) => setFormData({ ...formData, followUpDate: e.target.value })}
            className="bg-background border-border"
          />
        </div>
      )}

      <div className="flex justify-end space-x-2">
        <Button type="button" variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button type="submit" className="bg-primary hover:bg-primary/90 text-primary-foreground">
          Create Entry
        </Button>
      </div>
    </form>
  )
}
