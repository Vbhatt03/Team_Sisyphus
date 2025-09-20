"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import {
  FileText,
  Brain,
  Download,
  Eye,
  CheckCircle,
  AlertTriangle,
  Clock,
  Scale,
  Shield,
  Zap,
  RefreshCw,
} from "lucide-react"

interface ReportSection {
  id: string
  title: string
  status: "completed" | "processing" | "pending" | "error"
  content?: string
  wordCount?: number
  aiConfidence?: number
  issues?: string[]
}

export function ReportGenerator() {
  const [selectedCase, setSelectedCase] = useState("")
  const [reportType, setReportType] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  const [reportSections, setReportSections] = useState<ReportSection[]>([])
  const [activeTab, setActiveTab] = useState("generator")

  // Mock case data
  const availableCases = [
    { id: "FIR/2025/004", title: "Sexual Assault Case - Minor Victim", status: "ready" },
    { id: "FIR/2025/003", title: "POCSO Case - Multiple Accused", status: "ready" },
    { id: "FIR/2025/002", title: "Rape Case - Investigation Complete", status: "ready" },
  ]

  const reportTypes = [
    { id: "chargesheet", title: "Final Chargesheet", description: "Complete chargesheet for court filing" },
    { id: "progress", title: "Progress Report", description: "Investigation progress summary" },
    { id: "compliance", title: "Compliance Report", description: "Procedural compliance analysis" },
    { id: "summary", title: "Case Summary", description: "Executive summary for supervisors" },
  ]

  const mockReportSections: ReportSection[] = [
    {
      id: "case-details",
      title: "Case Details & Registration",
      status: "completed",
      content:
        "FIR No. FIR/2025/004 was registered on 20th January 2025 at 10:30 AM under Sections 376, 506 of BNS and relevant sections of POCSO Act 2012. The case involves alleged sexual assault of a 17-year-old minor victim by two known accused persons at a residential premises in Sector 15, Noida, UP.",
      wordCount: 156,
      aiConfidence: 95,
    },
    {
      id: "investigation-narrative",
      title: "Investigation Conducted",
      status: "completed",
      content:
        "Upon registration of the FIR, immediate action was taken as per POCSO Act guidelines. The victim's statement was recorded under Section 183 BNSS on the same day at 14:15 hours in the presence of a support person. Medical examination was conducted immediately at District Hospital by Dr. Priya Singh, and the report confirms physical evidence consistent with the victim's statement. Crime scene was examined on 21st January 2025 with forensic team assistance.",
      wordCount: 287,
      aiConfidence: 92,
    },
    {
      id: "evidence-analysis",
      title: "Evidence Collected & Analysis",
      status: "completed",
      content:
        "The following evidence has been collected and preserved: (1) Audio recording of victim's statement, (2) Medical examination report from District Hospital, (3) Crime scene photographs and forensic evidence, (4) CCTV footage from nearby locations. All evidence has been properly documented with chain of custody maintained as per legal requirements.",
      wordCount: 198,
      aiConfidence: 88,
      issues: ["CCTV footage analysis pending", "Forensic report awaited"],
    },
    {
      id: "accused-details",
      title: "Details of Accused Persons",
      status: "processing",
      aiConfidence: 75,
    },
    {
      id: "witness-statements",
      title: "Witness Statements",
      status: "pending",
    },
    {
      id: "legal-analysis",
      title: "Legal Analysis & Sections",
      status: "pending",
    },
  ]

  const generateReport = async () => {
    if (!selectedCase || !reportType) return

    setIsGenerating(true)
    setGenerationProgress(0)
    setReportSections(mockReportSections)
    setActiveTab("preview")

    // Simulate AI generation process
    const progressSteps = [10, 25, 45, 65, 80, 95, 100]
    for (const step of progressSteps) {
      await new Promise((resolve) => setTimeout(resolve, 800))
      setGenerationProgress(step)
    }

    setIsGenerating(false)
  }

  const regenerateSection = (sectionId: string) => {
    setReportSections((prev) =>
      prev.map((section) => (section.id === sectionId ? { ...section, status: "processing" as const } : section)),
    )

    // Simulate regeneration
    setTimeout(() => {
      setReportSections((prev) =>
        prev.map((section) =>
          section.id === sectionId
            ? {
                ...section,
                status: "completed" as const,
                content: "Regenerated content with improved analysis and additional details...",
                aiConfidence: Math.min(100, (section.aiConfidence || 0) + 5),
              }
            : section,
        ),
      )
    }, 2000)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-500"
      case "processing":
        return "text-blue-500"
      case "pending":
        return "text-amber-500"
      case "error":
        return "text-red-500"
      default:
        return "text-gray-500"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return CheckCircle
      case "processing":
        return RefreshCw
      case "pending":
        return Clock
      case "error":
        return AlertTriangle
      default:
        return Clock
    }
  }

  return (
    <div className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="generator">Report Generator</TabsTrigger>
          <TabsTrigger value="preview">Preview & Edit</TabsTrigger>
          <TabsTrigger value="export">Export & Download</TabsTrigger>
        </TabsList>

        {/* Report Generator Tab */}
        <TabsContent value="generator" className="space-y-6">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="w-5 h-5" />
                <span>AI Report Configuration</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="case-select">Select Case</Label>
                  <Select value={selectedCase} onValueChange={setSelectedCase}>
                    <SelectTrigger className="bg-background border-border">
                      <SelectValue placeholder="Choose a case to generate report" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableCases.map((case_) => (
                        <SelectItem key={case_.id} value={case_.id}>
                          <div className="flex items-center justify-between w-full">
                            <span>{case_.title}</span>
                            <Badge className="ml-2 bg-green-500/10 text-green-500">{case_.status}</Badge>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="report-type">Report Type</Label>
                  <Select value={reportType} onValueChange={setReportType}>
                    <SelectTrigger className="bg-background border-border">
                      <SelectValue placeholder="Select report type" />
                    </SelectTrigger>
                    <SelectContent>
                      {reportTypes.map((type) => (
                        <SelectItem key={type.id} value={type.id}>
                          <div>
                            <div className="font-medium">{type.title}</div>
                            <div className="text-xs text-muted-foreground">{type.description}</div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {selectedCase && reportType && (
                <Alert>
                  <Zap className="h-4 w-4" />
                  <AlertDescription>
                    AI will analyze all case data including diary entries, evidence, compliance records, and witness
                    statements to generate a comprehensive {reportTypes.find((t) => t.id === reportType)?.title}.
                  </AlertDescription>
                </Alert>
              )}

              <div className="flex justify-center">
                <Button
                  onClick={generateReport}
                  disabled={!selectedCase || !reportType || isGenerating}
                  className="bg-primary hover:bg-primary/90 text-primary-foreground px-8"
                >
                  {isGenerating ? (
                    <div className="flex items-center space-x-2">
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Generating Report...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <Brain className="w-4 h-4" />
                      <span>Generate AI Report</span>
                    </div>
                  )}
                </Button>
              </div>

              {isGenerating && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span>AI Processing Progress</span>
                    <span>{generationProgress}%</span>
                  </div>
                  <Progress value={generationProgress} />
                  <div className="text-center text-sm text-muted-foreground">
                    {generationProgress < 30 && "Analyzing case data and evidence..."}
                    {generationProgress >= 30 && generationProgress < 60 && "Compiling investigation narrative..."}
                    {generationProgress >= 60 && generationProgress < 90 && "Generating legal analysis..."}
                    {generationProgress >= 90 && "Finalizing report structure..."}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* AI Features Overview */}
          <div className="grid md:grid-cols-3 gap-4">
            <Card className="bg-card border-border">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-blue-500/10 rounded-lg">
                    <Brain className="w-5 h-5 text-blue-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Smart Compilation</h3>
                    <p className="text-sm text-muted-foreground">Automatically organizes all case data</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-green-500/10 rounded-lg">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Compliance Check</h3>
                    <p className="text-sm text-muted-foreground">Ensures all legal requirements met</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-purple-500/10 rounded-lg">
                    <Scale className="w-5 h-5 text-purple-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Legal Analysis</h3>
                    <p className="text-sm text-muted-foreground">AI-powered legal insights</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Preview & Edit Tab */}
        <TabsContent value="preview" className="space-y-6">
          {reportSections.length > 0 ? (
            <div className="grid lg:grid-cols-4 gap-6">
              {/* Section Navigation */}
              <div className="lg:col-span-1">
                <Card className="bg-card border-border sticky top-6">
                  <CardHeader>
                    <CardTitle className="text-sm">Report Sections</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {reportSections.map((section) => {
                      const StatusIcon = getStatusIcon(section.status)
                      return (
                        <div
                          key={section.id}
                          className="flex items-center space-x-2 p-2 rounded-lg hover:bg-muted/50 cursor-pointer"
                        >
                          <StatusIcon className={`w-4 h-4 ${getStatusColor(section.status)}`} />
                          <span className="text-sm font-medium">{section.title}</span>
                        </div>
                      )
                    })}
                  </CardContent>
                </Card>
              </div>

              {/* Section Content */}
              <div className="lg:col-span-3 space-y-4">
                {reportSections.map((section) => {
                  const StatusIcon = getStatusIcon(section.status)
                  return (
                    <Card key={section.id} className="bg-card border-border">
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle className="flex items-center space-x-2">
                            <StatusIcon className={`w-5 h-5 ${getStatusColor(section.status)}`} />
                            <span>{section.title}</span>
                          </CardTitle>
                          <div className="flex items-center space-x-2">
                            {section.aiConfidence && (
                              <Badge variant="outline">AI Confidence: {section.aiConfidence}%</Badge>
                            )}
                            {section.status === "completed" && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => regenerateSection(section.id)}
                                className="bg-transparent"
                              >
                                <RefreshCw className="w-3 h-3 mr-1" />
                                Regenerate
                              </Button>
                            )}
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        {section.status === "completed" && section.content && (
                          <div>
                            <Textarea
                              value={section.content}
                              onChange={() => {}} // Handle content editing
                              className="bg-background border-border min-h-[120px]"
                            />
                            <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
                              <span>Word count: {section.wordCount}</span>
                              <span>AI Confidence: {section.aiConfidence}%</span>
                            </div>
                          </div>
                        )}

                        {section.status === "processing" && (
                          <div className="flex items-center space-x-2 p-4 bg-blue-500/10 rounded-lg">
                            <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />
                            <span className="text-blue-700">AI is generating this section...</span>
                          </div>
                        )}

                        {section.status === "pending" && (
                          <div className="flex items-center space-x-2 p-4 bg-amber-500/10 rounded-lg">
                            <Clock className="w-4 h-4 text-amber-500" />
                            <span className="text-amber-700">Waiting for previous sections to complete</span>
                          </div>
                        )}

                        {section.issues && section.issues.length > 0 && (
                          <Alert variant="destructive">
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription>
                              <div className="space-y-1">
                                <p className="font-medium">Issues detected:</p>
                                <ul className="list-disc list-inside text-sm">
                                  {section.issues.map((issue, index) => (
                                    <li key={index}>{issue}</li>
                                  ))}
                                </ul>
                              </div>
                            </AlertDescription>
                          </Alert>
                        )}
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            </div>
          ) : (
            <Card className="bg-card border-border">
              <CardContent className="p-12 text-center">
                <FileText className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-foreground mb-2">No Report Generated</h3>
                <p className="text-muted-foreground mb-4">
                  Generate a report from the Generator tab to preview and edit sections here.
                </p>
                <Button onClick={() => setActiveTab("generator")} variant="outline">
                  Go to Generator
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Export & Download Tab */}
        <TabsContent value="export" className="space-y-6">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Download className="w-5 h-5" />
                <span>Export Options</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="font-semibold text-foreground">Court-Ready Formats</h3>
                  <div className="space-y-2">
                    <Button className="w-full justify-start bg-primary hover:bg-primary/90 text-primary-foreground">
                      <FileText className="w-4 h-4 mr-2" />
                      Download PDF (Court Filing)
                    </Button>
                    <Button variant="outline" className="w-full justify-start bg-transparent">
                      <FileText className="w-4 h-4 mr-2" />
                      Download Word Document
                    </Button>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-semibold text-foreground">Internal Use</h3>
                  <div className="space-y-2">
                    <Button variant="outline" className="w-full justify-start bg-transparent">
                      <Eye className="w-4 h-4 mr-2" />
                      Print Preview
                    </Button>
                    <Button variant="outline" className="w-full justify-start bg-transparent">
                      <Shield className="w-4 h-4 mr-2" />
                      Encrypted Archive
                    </Button>
                  </div>
                </div>
              </div>

              <Alert>
                <Shield className="h-4 w-4" />
                <AlertDescription>
                  All exported reports are digitally signed and include metadata for authenticity verification. Court
                  filing format includes all required legal certifications.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
