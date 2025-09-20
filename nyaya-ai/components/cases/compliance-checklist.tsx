"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  CheckCircle,
  Clock,
  AlertTriangle,
  FileText,
  User,
  MapPin,
  Shield,
  Scale,
  Calendar,
  Upload,
  Eye,
} from "lucide-react"

interface ComplianceChecklistProps {
  caseId: string
  caseData: any
}

interface ChecklistItem {
  id: string
  title: string
  description: string
  category: string
  priority: "critical" | "high" | "medium"
  status: "completed" | "pending" | "overdue"
  deadline: string
  timeRemaining: string
  requiredDocuments: string[]
  sopReference: string
  icon: React.ElementType
}

export function ComplianceChecklist({ caseId, caseData }: ComplianceChecklistProps) {
  const [selectedItem, setSelectedItem] = useState<ChecklistItem | null>(null)

  // Mock checklist data - would come from AI-generated roadmap
  const checklistItems: ChecklistItem[] = [
    {
      id: "victim-statement",
      title: "Victim Statement u/s 183 BNSS",
      description: "Record detailed statement from victim under Section 183 of BNSS",
      category: "Victim Procedures",
      priority: "critical",
      status: "completed",
      deadline: "2025-01-21 15:00",
      timeRemaining: "Completed",
      requiredDocuments: ["Victim Statement", "Identity Verification"],
      sopReference: "SOP-VS-001",
      icon: User,
    },
    {
      id: "medical-exam",
      title: "Medical Examination",
      description: "Immediate medical examination as per POCSO Act requirements",
      category: "Medical Procedures",
      priority: "critical",
      status: "completed",
      deadline: "2025-01-20 18:00",
      timeRemaining: "Completed",
      requiredDocuments: ["Medical Report", "Consent Form"],
      sopReference: "SOP-ME-002",
      icon: Shield,
    },
    {
      id: "crime-scene",
      title: "Crime Scene Investigation",
      description: "Detailed examination and documentation of crime scene",
      category: "Investigation",
      priority: "high",
      status: "pending",
      deadline: "2025-01-22 12:00",
      timeRemaining: "18 hours",
      requiredDocuments: ["Scene Photos", "Sketch Map", "Seizure Memo"],
      sopReference: "SOP-CS-003",
      icon: MapPin,
    },
    {
      id: "accused-arrest",
      title: "Arrest of Accused",
      description: "Locate and arrest the accused persons",
      category: "Accused Procedures",
      priority: "high",
      status: "pending",
      deadline: "2025-01-23 10:00",
      timeRemaining: "2 days",
      requiredDocuments: ["Arrest Memo", "Search Warrant"],
      sopReference: "SOP-AR-004",
      icon: Scale,
    },
    {
      id: "forensic-evidence",
      title: "Forensic Evidence Collection",
      description: "Collect and preserve forensic evidence for laboratory analysis",
      category: "Evidence",
      priority: "high",
      status: "overdue",
      deadline: "2025-01-21 09:00",
      timeRemaining: "12 hours overdue",
      requiredDocuments: ["Evidence Bags", "Chain of Custody"],
      sopReference: "SOP-FE-005",
      icon: FileText,
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-500"
      case "pending":
        return "text-amber-500"
      case "overdue":
        return "text-red-500"
      default:
        return "text-gray-500"
    }
  }

  const getStatusBgColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-500/10"
      case "pending":
        return "bg-amber-500/10"
      case "overdue":
        return "bg-red-500/10"
      default:
        return "bg-gray-500/10"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return CheckCircle
      case "pending":
        return Clock
      case "overdue":
        return AlertTriangle
      default:
        return Clock
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "critical":
        return "bg-red-500/10 text-red-500"
      case "high":
        return "bg-amber-500/10 text-amber-500"
      case "medium":
        return "bg-blue-500/10 text-blue-500"
      default:
        return "bg-gray-500/10 text-gray-500"
    }
  }

  const completedItems = checklistItems.filter((item) => item.status === "completed").length
  const totalItems = checklistItems.length
  const completionPercentage = (completedItems / totalItems) * 100

  return (
    <div className="grid lg:grid-cols-3 gap-6">
      {/* Checklist Items */}
      <div className="lg:col-span-2 space-y-4">
        <Card className="bg-card border-border">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-foreground">Investigation Roadmap</CardTitle>
              <div className="text-sm text-muted-foreground">
                {completedItems}/{totalItems} completed ({Math.round(completionPercentage)}%)
              </div>
            </div>
            <Progress value={completionPercentage} className="mt-2" />
          </CardHeader>
        </Card>

        {/* Overdue Items Alert */}
        {checklistItems.some((item) => item.status === "overdue") && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              You have {checklistItems.filter((item) => item.status === "overdue").length} overdue task(s) that require
              immediate attention.
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-3">
          {checklistItems.map((item) => {
            const StatusIcon = getStatusIcon(item.status)
            return (
              <Card
                key={item.id}
                className={`bg-card border-border cursor-pointer transition-all hover:shadow-md ${
                  selectedItem?.id === item.id ? "ring-2 ring-primary" : ""
                }`}
                onClick={() => setSelectedItem(item)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start space-x-4">
                    <div className={`p-2 rounded-lg ${getStatusBgColor(item.status)}`}>
                      <StatusIcon className={`w-5 h-5 ${getStatusColor(item.status)}`} />
                    </div>

                    <div className="flex-1 space-y-2">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-semibold text-foreground">{item.title}</h3>
                          <p className="text-sm text-muted-foreground">{item.description}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getPriorityColor(item.priority)}>{item.priority}</Badge>
                          <item.icon className="w-4 h-4 text-muted-foreground" />
                        </div>
                      </div>

                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center space-x-4">
                          <span className="text-muted-foreground">Category: {item.category}</span>
                          <span className="text-muted-foreground">•</span>
                          <span className="text-muted-foreground">SOP: {item.sopReference}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Calendar className="w-4 h-4 text-muted-foreground" />
                          <span className={getStatusColor(item.status)}>{item.timeRemaining}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Task Details Panel */}
      <div className="space-y-4">
        {selectedItem ? (
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <selectedItem.icon className="w-5 h-5" />
                <span>Task Details</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold text-foreground mb-2">{selectedItem.title}</h3>
                <p className="text-sm text-muted-foreground">{selectedItem.description}</p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Status:</span>
                  <Badge className={getStatusBgColor(selectedItem.status) + " " + getStatusColor(selectedItem.status)}>
                    {selectedItem.status}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Priority:</span>
                  <Badge className={getPriorityColor(selectedItem.priority)}>{selectedItem.priority}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Deadline:</span>
                  <span className="text-sm text-muted-foreground">{selectedItem.deadline}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Time Remaining:</span>
                  <span className={`text-sm ${getStatusColor(selectedItem.status)}`}>{selectedItem.timeRemaining}</span>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-foreground mb-2">Required Documents:</h4>
                <div className="space-y-1">
                  {selectedItem.requiredDocuments.map((doc) => (
                    <div key={doc} className="flex items-center space-x-2 text-sm">
                      <FileText className="w-3 h-3 text-muted-foreground" />
                      <span className="text-muted-foreground">{doc}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground">
                  <Upload className="w-4 h-4 mr-2" />
                  Upload Documents
                </Button>
                <Button variant="outline" className="w-full bg-transparent">
                  <Eye className="w-4 h-4 mr-2" />
                  View SOP Guidelines
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card className="bg-card border-border">
            <CardContent className="p-8 text-center">
              <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="font-semibold text-foreground mb-2">Select a Task</h3>
              <p className="text-sm text-muted-foreground">
                Click on any task from the checklist to view detailed information and required actions.
              </p>
            </CardContent>
          </Card>
        )}

        {/* Quick Stats */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-foreground">Quick Stats</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Completed Tasks</span>
              <span className="text-sm font-semibold text-green-500">{completedItems}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Pending Tasks</span>
              <span className="text-sm font-semibold text-amber-500">
                {checklistItems.filter((item) => item.status === "pending").length}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Overdue Tasks</span>
              <span className="text-sm font-semibold text-red-500">
                {checklistItems.filter((item) => item.status === "overdue").length}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Critical Priority</span>
              <span className="text-sm font-semibold text-red-500">
                {checklistItems.filter((item) => item.priority === "critical").length}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
