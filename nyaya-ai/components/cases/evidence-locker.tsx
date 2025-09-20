"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Upload,
  FileText,
  ImageIcon,
  Video,
  Mic,
  Shield,
  Download,
  Eye,
  Search,
  Filter,
  Calendar,
  Lock,
  CheckCircle,
} from "lucide-react"

interface EvidenceItem {
  id: string
  name: string
  type: "document" | "image" | "video" | "audio" | "other"
  category: string
  uploadDate: string
  uploadedBy: string
  size: string
  description: string
  tags: string[]
  chainOfCustody: ChainOfCustodyEntry[]
  verified: boolean
  encrypted: boolean
}

interface ChainOfCustodyEntry {
  timestamp: string
  action: string
  officer: string
  location: string
  notes: string
}

interface EvidenceLockerProps {
  caseId: string
}

export function EvidenceLocker({ caseId }: EvidenceLockerProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceItem | null>(null)
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false)

  // Mock evidence data
  const evidenceItems: EvidenceItem[] = [
    {
      id: "ev-001",
      name: "Victim_Statement_Recording.mp3",
      type: "audio",
      category: "Victim Statement",
      uploadDate: "2025-01-20 14:30",
      uploadedBy: "IO Sharma",
      size: "12.5 MB",
      description: "Audio recording of victim's statement under Section 183 BNSS",
      tags: ["victim", "statement", "audio", "section-183"],
      chainOfCustody: [
        {
          timestamp: "2025-01-20 14:30",
          action: "Initial Upload",
          officer: "IO Sharma",
          location: "Police Station - Interview Room 1",
          notes: "Original recording uploaded immediately after statement",
        },
      ],
      verified: true,
      encrypted: true,
    },
    {
      id: "ev-002",
      name: "Medical_Report_Victim.pdf",
      type: "document",
      category: "Medical Evidence",
      uploadDate: "2025-01-20 16:45",
      uploadedBy: "Dr. Priya Singh",
      size: "2.8 MB",
      description: "Complete medical examination report as per POCSO Act requirements",
      tags: ["medical", "report", "pocso", "examination"],
      chainOfCustody: [
        {
          timestamp: "2025-01-20 16:45",
          action: "Medical Report Submitted",
          officer: "Dr. Priya Singh",
          location: "District Hospital",
          notes: "Report submitted directly by examining doctor",
        },
        {
          timestamp: "2025-01-20 17:00",
          action: "Verified and Archived",
          officer: "IO Sharma",
          location: "Police Station",
          notes: "Report verified and added to case file",
        },
      ],
      verified: true,
      encrypted: true,
    },
    {
      id: "ev-003",
      name: "Crime_Scene_Photos.zip",
      type: "image",
      category: "Crime Scene",
      uploadDate: "2025-01-21 10:15",
      uploadedBy: "Forensic Team",
      size: "45.2 MB",
      description: "Comprehensive crime scene photographs and documentation",
      tags: ["crime-scene", "photos", "forensic", "documentation"],
      chainOfCustody: [
        {
          timestamp: "2025-01-21 10:15",
          action: "Forensic Photos Uploaded",
          officer: "Inspector Forensics",
          location: "Crime Scene - Sector 15",
          notes: "Complete photographic documentation of crime scene",
        },
      ],
      verified: false,
      encrypted: true,
    },
    {
      id: "ev-004",
      name: "CCTV_Footage_Location.mp4",
      type: "video",
      category: "CCTV Evidence",
      uploadDate: "2025-01-21 12:30",
      uploadedBy: "Tech Team",
      size: "128.7 MB",
      description: "CCTV footage from nearby location showing suspect movement",
      tags: ["cctv", "video", "suspect", "movement"],
      chainOfCustody: [
        {
          timestamp: "2025-01-21 12:30",
          action: "CCTV Footage Acquired",
          officer: "Tech Constable Raj",
          location: "Local CCTV Control Room",
          notes: "Footage obtained from local security cameras",
        },
      ],
      verified: false,
      encrypted: true,
    },
  ]

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "document":
        return FileText
      case "image":
        return ImageIcon
      case "video":
        return Video
      case "audio":
        return Mic
      default:
        return FileText
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case "document":
        return "text-blue-500"
      case "image":
        return "text-green-500"
      case "video":
        return "text-purple-500"
      case "audio":
        return "text-orange-500"
      default:
        return "text-gray-500"
    }
  }

  const filteredEvidence = evidenceItems.filter((item) => {
    const matchesSearch =
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.tags.some((tag) => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesCategory = selectedCategory === "all" || item.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const categories = ["all", ...Array.from(new Set(evidenceItems.map((item) => item.category)))]

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Digital Evidence Locker</h2>
          <p className="text-muted-foreground">Secure, encrypted storage for all case evidence</p>
        </div>

        <Dialog open={isUploadDialogOpen} onOpenChange={setIsUploadDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">
              <Upload className="w-4 h-4 mr-2" />
              Upload Evidence
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Upload New Evidence</DialogTitle>
              <DialogDescription>Add new evidence to the secure digital locker</DialogDescription>
            </DialogHeader>
            <EvidenceUploadForm onClose={() => setIsUploadDialogOpen(false)} />
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
                  placeholder="Search evidence by name, description, or tags..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-background border-border"
                />
              </div>
            </div>
            <div className="md:w-48">
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="bg-background border-border">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category === "all" ? "All Categories" : category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Evidence Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="grid gap-4">
            {filteredEvidence.map((item) => {
              const TypeIcon = getTypeIcon(item.type)
              return (
                <Card
                  key={item.id}
                  className={`bg-card border-border cursor-pointer transition-all hover:shadow-md ${
                    selectedEvidence?.id === item.id ? "ring-2 ring-primary" : ""
                  }`}
                  onClick={() => setSelectedEvidence(item)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start space-x-4">
                      <div className={`p-3 rounded-lg bg-muted/50`}>
                        <TypeIcon className={`w-6 h-6 ${getTypeColor(item.type)}`} />
                      </div>

                      <div className="flex-1 space-y-2">
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="font-semibold text-foreground">{item.name}</h3>
                            <p className="text-sm text-muted-foreground">{item.description}</p>
                          </div>
                          <div className="flex items-center space-x-2">
                            {item.verified && (
                              <Badge className="bg-green-500/10 text-green-500">
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Verified
                              </Badge>
                            )}
                            {item.encrypted && (
                              <Badge className="bg-blue-500/10 text-blue-500">
                                <Lock className="w-3 h-3 mr-1" />
                                Encrypted
                              </Badge>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center space-x-4">
                            <span className="text-muted-foreground">Category: {item.category}</span>
                            <span className="text-muted-foreground">•</span>
                            <span className="text-muted-foreground">Size: {item.size}</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Calendar className="w-4 h-4 text-muted-foreground" />
                            <span className="text-muted-foreground">{item.uploadDate}</span>
                          </div>
                        </div>

                        <div className="flex flex-wrap gap-1">
                          {item.tags.slice(0, 3).map((tag) => (
                            <Badge key={tag} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                          {item.tags.length > 3 && (
                            <Badge variant="outline" className="text-xs">
                              +{item.tags.length - 3} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>

        {/* Evidence Details Panel */}
        <div>
          {selectedEvidence ? (
            <Card className="bg-card border-border sticky top-6">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="w-5 h-5" />
                  <span>Evidence Details</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="font-semibold text-foreground mb-2">{selectedEvidence.name}</h3>
                  <p className="text-sm text-muted-foreground">{selectedEvidence.description}</p>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Type:</span>
                    <Badge variant="outline">{selectedEvidence.type}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Category:</span>
                    <span className="text-sm text-muted-foreground">{selectedEvidence.category}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Size:</span>
                    <span className="text-sm text-muted-foreground">{selectedEvidence.size}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Uploaded By:</span>
                    <span className="text-sm text-muted-foreground">{selectedEvidence.uploadedBy}</span>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-foreground mb-2">Tags:</h4>
                  <div className="flex flex-wrap gap-1">
                    {selectedEvidence.tags.map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-foreground mb-2">Chain of Custody:</h4>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {selectedEvidence.chainOfCustody.map((entry, index) => (
                      <div key={index} className="p-2 bg-muted/50 rounded text-xs">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium">{entry.action}</span>
                          <span className="text-muted-foreground">{entry.timestamp}</span>
                        </div>
                        <div className="text-muted-foreground">
                          <p>Officer: {entry.officer}</p>
                          <p>Location: {entry.location}</p>
                          {entry.notes && <p>Notes: {entry.notes}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground">
                    <Eye className="w-4 h-4 mr-2" />
                    View Evidence
                  </Button>
                  <Button variant="outline" className="w-full bg-transparent">
                    <Download className="w-4 h-4 mr-2" />
                    Download Copy
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="bg-card border-border">
              <CardContent className="p-8 text-center">
                <Shield className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="font-semibold text-foreground mb-2">Select Evidence</h3>
                <p className="text-sm text-muted-foreground">
                  Click on any evidence item to view detailed information and chain of custody.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Security Notice */}
      <Alert>
        <Lock className="h-4 w-4" />
        <AlertDescription>
          All evidence is encrypted at rest and in transit. Access is logged and monitored. Only authorized personnel
          can view or download evidence files.
        </AlertDescription>
      </Alert>
    </div>
  )
}

function EvidenceUploadForm({ onClose }: { onClose: () => void }) {
  const [formData, setFormData] = useState({
    file: null as File | null,
    category: "",
    description: "",
    tags: "",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle upload logic here
    console.log("Uploading evidence:", formData)
    onClose()
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="file">Evidence File</Label>
        <Input
          id="file"
          type="file"
          onChange={(e) => setFormData({ ...formData, file: e.target.files?.[0] || null })}
          className="bg-background border-border"
          required
        />
      </div>

      <div>
        <Label htmlFor="category">Category</Label>
        <Select value={formData.category} onValueChange={(value) => setFormData({ ...formData, category: value })}>
          <SelectTrigger className="bg-background border-border">
            <SelectValue placeholder="Select category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Victim Statement">Victim Statement</SelectItem>
            <SelectItem value="Medical Evidence">Medical Evidence</SelectItem>
            <SelectItem value="Crime Scene">Crime Scene</SelectItem>
            <SelectItem value="CCTV Evidence">CCTV Evidence</SelectItem>
            <SelectItem value="Forensic Evidence">Forensic Evidence</SelectItem>
            <SelectItem value="Other">Other</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          placeholder="Describe the evidence and its relevance to the case"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="bg-background border-border"
          required
        />
      </div>

      <div>
        <Label htmlFor="tags">Tags (comma-separated)</Label>
        <Input
          id="tags"
          placeholder="e.g., victim, statement, audio, section-183"
          value={formData.tags}
          onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
          className="bg-background border-border"
        />
      </div>

      <div className="flex justify-end space-x-2">
        <Button type="button" variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button type="submit" className="bg-primary hover:bg-primary/90 text-primary-foreground">
          Upload Evidence
        </Button>
      </div>
    </form>
  )
}
