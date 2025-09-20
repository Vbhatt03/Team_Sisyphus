"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ComplianceChecklist } from "@/components/cases/compliance-checklist"
import { CaseOverview } from "@/components/cases/case-overview"
import { EvidenceLocker } from "@/components/cases/evidence-locker"
import { CaseDiary } from "@/components/cases/case-diary"
import { AlertTriangle, CheckCircle, Clock, FileText, Shield } from "lucide-react"

interface InvestigationWorkspaceProps {
  caseId: string
}

export function InvestigationWorkspace({ caseId }: InvestigationWorkspaceProps) {
  const [activeTab, setActiveTab] = useState("overview")

  // Mock case data - in real app, this would come from API
  const caseData = {
    id: "FIR/2025/004",
    title: "Sexual Assault Case - Minor Victim",
    status: "active",
    priority: "high",
    createdDate: "2025-01-20",
    lastUpdated: "2 hours ago",
    victimAge: 17,
    accusedCount: 2,
    sections: ["376", "506", "POCSO Act 2012"],
    location: "Sector 15, Noida, UP",
    assignedOfficer: "IO Sharma",
    complianceScore: 75,
    totalTasks: 12,
    completedTasks: 9,
    pendingDeadlines: 2,
    criticalDeadlines: 1,
  }

  const getComplianceColor = (score: number) => {
    if (score >= 90) return "text-green-500"
    if (score >= 70) return "text-amber-500"
    return "text-red-500"
  }

  const getComplianceBgColor = (score: number) => {
    if (score >= 90) return "bg-green-500/10"
    if (score >= 70) return "bg-amber-500/10"
    return "bg-red-500/10"
  }

  return (
    <div className="space-y-6">
      {/* Case Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div className="space-y-2">
          <div className="flex items-center space-x-3">
            <h1 className="text-3xl font-bold text-foreground">{caseData.title}</h1>
            <Badge className="bg-blue-500/10 text-blue-500">{caseData.status}</Badge>
            <Badge className="bg-red-500/10 text-red-500">{caseData.priority}</Badge>
          </div>
          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
            <span>{caseData.id}</span>
            <span>•</span>
            <span>Created: {caseData.createdDate}</span>
            <span>•</span>
            <span>Last updated: {caseData.lastUpdated}</span>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <Button variant="outline" size="sm">
            <FileText className="w-4 h-4 mr-2" />
            Generate Report
          </Button>
          <Button size="sm" className="bg-primary hover:bg-primary/90 text-primary-foreground">
            <Shield className="w-4 h-4 mr-2" />
            Update Case
          </Button>
        </div>
      </div>

      {/* Compliance Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-card border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Compliance Score</p>
                <p className={`text-2xl font-bold ${getComplianceColor(caseData.complianceScore)}`}>
                  {caseData.complianceScore}%
                </p>
              </div>
              <div className={`p-3 rounded-lg ${getComplianceBgColor(caseData.complianceScore)}`}>
                <CheckCircle className={`w-5 h-5 ${getComplianceColor(caseData.complianceScore)}`} />
              </div>
            </div>
            <Progress value={caseData.complianceScore} className="mt-3" />
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Tasks Completed</p>
                <p className="text-2xl font-bold text-foreground">
                  {caseData.completedTasks}/{caseData.totalTasks}
                </p>
              </div>
              <div className="p-3 rounded-lg bg-blue-500/10">
                <FileText className="w-5 h-5 text-blue-500" />
              </div>
            </div>
            <Progress value={(caseData.completedTasks / caseData.totalTasks) * 100} className="mt-3" />
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Pending Deadlines</p>
                <p className="text-2xl font-bold text-amber-500">{caseData.pendingDeadlines}</p>
              </div>
              <div className="p-3 rounded-lg bg-amber-500/10">
                <Clock className="w-5 h-5 text-amber-500" />
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-3">Require attention</p>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Critical Deadlines</p>
                <p className="text-2xl font-bold text-red-500">{caseData.criticalDeadlines}</p>
              </div>
              <div className="p-3 rounded-lg bg-red-500/10">
                <AlertTriangle className="w-5 h-5 text-red-500" />
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-3">Immediate action needed</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Workspace Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 lg:w-auto lg:grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="checklist">Compliance</TabsTrigger>
          <TabsTrigger value="evidence">Evidence</TabsTrigger>
          <TabsTrigger value="diary">Case Diary</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <CaseOverview caseData={caseData} />
        </TabsContent>

        <TabsContent value="checklist" className="space-y-6">
          <ComplianceChecklist caseId={caseId} caseData={caseData} />
        </TabsContent>

        <TabsContent value="evidence" className="space-y-6">
          <EvidenceLocker caseId={caseId} />
        </TabsContent>

        <TabsContent value="diary" className="space-y-6">
          <CaseDiary caseId={caseId} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
