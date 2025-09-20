"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Progress } from "@/components/ui/progress"
import { Brain, FileText, Download, CheckCircle, AlertTriangle, Zap } from "lucide-react"

interface CaseReportGeneratorProps {
  caseId: string
}

export function CaseReportGenerator({ caseId }: CaseReportGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  const [reportReady, setReportReady] = useState(false)

  const generateChargesheet = async () => {
    setIsGenerating(true)
    setGenerationProgress(0)

    // Simulate AI generation process
    const steps = [
      { progress: 15, message: "Analyzing case diary entries..." },
      { progress: 30, message: "Compiling evidence inventory..." },
      { progress: 50, message: "Cross-referencing witness statements..." },
      { progress: 70, message: "Generating legal narrative..." },
      { progress: 85, message: "Performing compliance checks..." },
      { progress: 100, message: "Finalizing chargesheet..." },
    ]

    for (const step of steps) {
      await new Promise((resolve) => setTimeout(resolve, 1000))
      setGenerationProgress(step.progress)
    }

    setIsGenerating(false)
    setReportReady(true)
  }

  return (
    <div className="space-y-6">
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="w-5 h-5" />
            <span>AI Chargesheet Builder</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <Alert>
            <Zap className="h-4 w-4" />
            <AlertDescription>
              AI will compile all case data including diary entries, evidence, compliance records, and witness
              statements to generate a comprehensive chargesheet ready for court filing.
            </AlertDescription>
          </Alert>

          {!isGenerating && !reportReady && (
            <div className="text-center">
              <Button
                onClick={generateChargesheet}
                className="bg-primary hover:bg-primary/90 text-primary-foreground px-8"
              >
                <Brain className="w-4 h-4 mr-2" />
                Generate Chargesheet
              </Button>
            </div>
          )}

          {isGenerating && (
            <div className="space-y-4">
              <div className="flex items-center justify-between text-sm">
                <span>AI Processing Progress</span>
                <span>{generationProgress}%</span>
              </div>
              <Progress value={generationProgress} />
              <div className="text-center text-sm text-muted-foreground">
                {generationProgress < 20 && "Analyzing case diary entries..."}
                {generationProgress >= 20 && generationProgress < 40 && "Compiling evidence inventory..."}
                {generationProgress >= 40 && generationProgress < 60 && "Cross-referencing witness statements..."}
                {generationProgress >= 60 && generationProgress < 80 && "Generating legal narrative..."}
                {generationProgress >= 80 && generationProgress < 95 && "Performing compliance checks..."}
                {generationProgress >= 95 && "Finalizing chargesheet..."}
              </div>
            </div>
          )}

          {reportReady && (
            <div className="space-y-4">
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Chargesheet generated successfully! The document includes all required sections and has passed
                  compliance validation.
                </AlertDescription>
              </Alert>

              <div className="grid md:grid-cols-2 gap-4">
                <Card className="bg-muted/50 border-border">
                  <CardContent className="pt-6">
                    <div className="space-y-2">
                      <h3 className="font-semibold text-foreground">Document Statistics</h3>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span>Total Pages:</span>
                          <span>24</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Word Count:</span>
                          <span>4,567</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Evidence Items:</span>
                          <span>12</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Witness Statements:</span>
                          <span>5</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-muted/50 border-border">
                  <CardContent className="pt-6">
                    <div className="space-y-2">
                      <h3 className="font-semibold text-foreground">Compliance Status</h3>
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <CheckCircle className="w-4 h-4 text-green-500" />
                          <span className="text-sm">All POCSO requirements met</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <CheckCircle className="w-4 h-4 text-green-500" />
                          <span className="text-sm">Evidence chain verified</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <CheckCircle className="w-4 h-4 text-green-500" />
                          <span className="text-sm">Legal sections validated</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <AlertTriangle className="w-4 h-4 text-amber-500" />
                          <span className="text-sm">1 minor formatting issue</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="flex justify-center space-x-4">
                <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">
                  <Download className="w-4 h-4 mr-2" />
                  Download PDF
                </Button>
                <Button variant="outline" className="bg-transparent">
                  <FileText className="w-4 h-4 mr-2" />
                  Preview Document
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
