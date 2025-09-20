"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Upload, FileText, CheckCircle, AlertCircle, Brain, User, MapPin, Scale } from "lucide-react"

interface CaseData {
  firNumber: string
  victimAge: string
  incidentDate: string
  location: string
  accusedCount: string
  sections: string[]
  summary: string
  victimName: string
  accusedNames: string
}

export function CaseIntakeWizard() {
  const [currentStep, setCurrentStep] = useState(1)
  const [isProcessing, setIsProcessing] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [extractedData, setExtractedData] = useState<CaseData | null>(null)
  const [isVerified, setIsVerified] = useState(false)

  const steps = [
    { id: 1, title: "Upload FIR", description: "Upload FIR document for AI processing" },
    { id: 2, title: "AI Extraction", description: "AI extracts key information" },
    { id: 3, title: "Verify Data", description: "Review and verify extracted data" },
    { id: 4, title: "Case Creation", description: "Create investigation roadmap" },
  ]

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setUploadedFile(file)
    }
  }

  const processDocument = async () => {
    if (!uploadedFile) return

    setIsProcessing(true)
    setCurrentStep(2)

    // Simulate AI processing
    setTimeout(() => {
      setExtractedData({
        firNumber: "FIR/2025/004",
        victimAge: "17",
        incidentDate: "2025-01-15",
        location: "Sector 15, Noida, UP",
        accusedCount: "2",
        sections: ["376", "506", "POCSO Act 2012"],
        summary:
          "Alleged sexual assault of minor victim by two known individuals at residential premises. Victim's statement recorded. Medical examination conducted.",
        victimName: "Protected Identity (Minor)",
        accusedNames: "Accused 1: [Name Redacted], Accused 2: [Name Redacted]",
      })
      setIsProcessing(false)
      setCurrentStep(3)
    }, 3000)
  }

  const verifyAndProceed = () => {
    setIsVerified(true)
    setCurrentStep(4)
  }

  const createCase = () => {
    // Simulate case creation
    setTimeout(() => {
      window.location.href = "/cases/FIR-2025-004"
    }, 1000)
  }

  return (
    <div className="space-y-6">
      {/* Progress Indicator */}
      <Card className="bg-card border-border">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between mb-4">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div
                  className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                    currentStep >= step.id
                      ? "bg-primary border-primary text-primary-foreground"
                      : "border-muted-foreground text-muted-foreground"
                  }`}
                >
                  {currentStep > step.id ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : (
                    <span className="text-sm font-semibold">{step.id}</span>
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-16 h-0.5 mx-2 ${currentStep > step.id ? "bg-primary" : "bg-muted"}`} />
                )}
              </div>
            ))}
          </div>
          <div className="text-center">
            <h3 className="font-semibold text-foreground">{steps[currentStep - 1].title}</h3>
            <p className="text-sm text-muted-foreground">{steps[currentStep - 1].description}</p>
          </div>
        </CardContent>
      </Card>

      {/* Step 1: Upload FIR */}
      {currentStep === 1 && (
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Upload className="w-5 h-5" />
              <span>Upload FIR Document</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
              <div className="space-y-4">
                <div className="flex justify-center">
                  <FileText className="w-12 h-12 text-muted-foreground" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">Upload FIR Document</h3>
                  <p className="text-sm text-muted-foreground">
                    Supports PDF, JPG, PNG formats. AI will extract key information automatically.
                  </p>
                </div>
                <div>
                  <Input
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={handleFileUpload}
                    className="max-w-xs mx-auto"
                  />
                </div>
                {uploadedFile && (
                  <div className="flex items-center justify-center space-x-2 text-sm text-green-600">
                    <CheckCircle className="w-4 h-4" />
                    <span>File uploaded: {uploadedFile.name}</span>
                  </div>
                )}
              </div>
            </div>

            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                All uploaded documents are encrypted and stored securely. Only authorized personnel can access case
                files.
              </AlertDescription>
            </Alert>

            <div className="flex justify-end">
              <Button
                onClick={processDocument}
                disabled={!uploadedFile}
                className="bg-primary hover:bg-primary/90 text-primary-foreground"
              >
                Process with AI
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: AI Processing */}
      {currentStep === 2 && (
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="w-5 h-5" />
              <span>AI Processing Document</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-center space-y-4">
              <div className="flex justify-center">
                <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">Analyzing FIR Document</h3>
                <p className="text-sm text-muted-foreground">
                  AI is extracting victim details, accused information, sections of law, and incident summary...
                </p>
              </div>
              <Progress value={65} className="max-w-md mx-auto" />
            </div>

            <div className="space-y-3">
              <div className="flex items-center space-x-2 text-sm">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>OCR text extraction completed</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Legal sections identified</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                <span>Extracting victim and accused details...</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Verify Extracted Data */}
      {currentStep === 3 && extractedData && (
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5" />
              <span>Verify Extracted Information</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <Alert>
              <Brain className="h-4 w-4" />
              <AlertDescription>
                AI has successfully extracted the following information. Please review and verify accuracy before
                proceeding.
              </AlertDescription>
            </Alert>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <Label className="text-foreground">FIR Number</Label>
                  <Input value={extractedData.firNumber} className="bg-background border-border" />
                </div>

                <div>
                  <Label className="text-foreground">Victim Age</Label>
                  <div className="flex items-center space-x-2">
                    <Input value={extractedData.victimAge} className="bg-background border-border" />
                    {Number.parseInt(extractedData.victimAge) < 18 && (
                      <Badge className="bg-amber-500/10 text-amber-500">POCSO Applicable</Badge>
                    )}
                  </div>
                </div>

                <div>
                  <Label className="text-foreground">Incident Date</Label>
                  <Input type="date" value={extractedData.incidentDate} className="bg-background border-border" />
                </div>

                <div>
                  <Label className="text-foreground">Location</Label>
                  <Input value={extractedData.location} className="bg-background border-border" />
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <Label className="text-foreground">Number of Accused</Label>
                  <Input value={extractedData.accusedCount} className="bg-background border-border" />
                </div>

                <div>
                  <Label className="text-foreground">Legal Sections</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {extractedData.sections.map((section) => (
                      <Badge key={section} variant="outline">
                        {section}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <Label className="text-foreground">Case Summary</Label>
                  <Textarea value={extractedData.summary} className="bg-background border-border min-h-[100px]" />
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <Button variant="outline" onClick={() => setCurrentStep(1)}>
                Back to Upload
              </Button>
              <Button onClick={verifyAndProceed} className="bg-primary hover:bg-primary/90 text-primary-foreground">
                Verify & Continue
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 4: Case Creation */}
      {currentStep === 4 && (
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Scale className="w-5 h-5" />
              <span>Generate Investigation Roadmap</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                Based on the case details, NYAYA AI will generate a customized investigation roadmap with all required
                procedures and deadlines.
              </AlertDescription>
            </Alert>

            <div className="space-y-4">
              <h3 className="font-semibold text-foreground">Investigation Plan Preview:</h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3 p-3 bg-muted/50 rounded-lg">
                  <User className="w-5 h-5 text-primary" />
                  <div>
                    <p className="font-medium">Victim Statement u/s 183 BNSS</p>
                    <p className="text-sm text-muted-foreground">Deadline: Within 24 hours</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-muted/50 rounded-lg">
                  <FileText className="w-5 h-5 text-primary" />
                  <div>
                    <p className="font-medium">Medical Examination</p>
                    <p className="text-sm text-muted-foreground">Deadline: Immediate (POCSO case)</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-muted/50 rounded-lg">
                  <MapPin className="w-5 h-5 text-primary" />
                  <div>
                    <p className="font-medium">Crime Scene Investigation</p>
                    <p className="text-sm text-muted-foreground">Deadline: Within 48 hours</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-end">
              <Button onClick={createCase} className="bg-primary hover:bg-primary/90 text-primary-foreground">
                Create Case & Start Investigation
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
