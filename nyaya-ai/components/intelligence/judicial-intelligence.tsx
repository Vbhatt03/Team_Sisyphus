"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Search, Brain, Scale, TrendingUp, AlertCircle, CheckCircle, Clock, Target, Lightbulb } from "lucide-react"

export function JudicialIntelligence() {
  const [searchQuery, setSearchQuery] = useState("")
  const [caseAnalysis, setCaseAnalysis] = useState("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  // Mock data for judicial intelligence
  const caseInsights = {
    strengthScore: 78,
    weaknesses: [
      "Insufficient corroborative evidence",
      "Potential timeline inconsistencies",
      "Missing expert testimony",
    ],
    strengths: ["Strong victim testimony", "Digital evidence available", "Witness statements consistent"],
    recommendations: [
      "Obtain additional forensic evidence",
      "Interview secondary witnesses",
      "Request expert psychological evaluation",
    ],
  }

  const similarCases = [
    {
      id: "SC2024-089",
      title: "State vs. Defendant - Similar POCSO Case",
      court: "Delhi High Court",
      outcome: "Conviction",
      relevance: 92,
      keyPoints: ["Digital evidence crucial", "Timeline establishment", "Expert testimony"],
      citation: "2024 DLT 456",
    },
    {
      id: "SC2023-156",
      title: "State vs. Accused - Evidence Chain",
      court: "Mumbai Sessions Court",
      outcome: "Acquittal",
      relevance: 87,
      keyPoints: ["Chain of custody issues", "Procedural lapses", "Witness reliability"],
      citation: "2023 MSC 234",
    },
    {
      id: "SC2024-023",
      title: "State vs. Respondent - POCSO Compliance",
      court: "Chennai High Court",
      outcome: "Conviction",
      relevance: 85,
      keyPoints: ["POCSO procedures followed", "Medical evidence", "Child-friendly court"],
      citation: "2024 CHC 123",
    },
  ]

  const legalPrecedents = [
    {
      case: "Sakshi vs. Union of India",
      year: "2004",
      court: "Supreme Court",
      principle: "In-camera proceedings for sexual offense cases",
      relevance: "High",
      impact: "Mandatory for all sexual offense trials",
    },
    {
      case: "State of Punjab vs. Gurmit Singh",
      year: "1996",
      court: "Supreme Court",
      principle: "Victim's testimony sufficient for conviction",
      relevance: "High",
      impact: "Corroboration not always necessary",
    },
    {
      case: "Bharwada Bhoginbhai vs. State of Gujarat",
      year: "1983",
      court: "Supreme Court",
      principle: "Medical evidence not mandatory",
      relevance: "Medium",
      impact: "Other evidence can establish the offense",
    },
  ]

  const predictiveAnalytics = {
    convictionProbability: 73,
    timeToTrial: "8-12 months",
    criticalFactors: [
      { factor: "Evidence Quality", weight: 35, score: 78 },
      { factor: "Witness Reliability", weight: 25, score: 82 },
      { factor: "Procedural Compliance", weight: 20, score: 65 },
      { factor: "Legal Precedents", weight: 20, score: 88 },
    ],
    riskFactors: ["Delayed medical examination", "Incomplete evidence documentation", "Witness availability concerns"],
  }

  const handleAnalyzeCase = () => {
    setIsAnalyzing(true)
    // Simulate AI analysis
    setTimeout(() => {
      setIsAnalyzing(false)
    }, 3000)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Judicial Intelligence Engine</h1>
          <p className="text-muted-foreground mt-2">
            AI-powered legal insights and case analysis for informed decision making
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Brain className="w-8 h-8 text-primary" />
          <Scale className="w-8 h-8 text-primary" />
        </div>
      </div>

      <Tabs defaultValue="analysis" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="analysis">Case Analysis</TabsTrigger>
          <TabsTrigger value="precedents">Legal Precedents</TabsTrigger>
          <TabsTrigger value="similar">Similar Cases</TabsTrigger>
          <TabsTrigger value="predictions">Predictive Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="analysis" className="space-y-6">
          {/* Case Analysis Input */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="w-5 h-5" />
                <span>AI Case Analysis</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Case Details</label>
                <Textarea
                  placeholder="Enter case details, evidence summary, and specific questions for AI analysis..."
                  value={caseAnalysis}
                  onChange={(e) => setCaseAnalysis(e.target.value)}
                  className="min-h-[120px]"
                />
              </div>
              <Button onClick={handleAnalyzeCase} disabled={isAnalyzing || !caseAnalysis.trim()} className="w-full">
                {isAnalyzing ? (
                  <>
                    <Clock className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing Case...
                  </>
                ) : (
                  <>
                    <Brain className="w-4 h-4 mr-2" />
                    Analyze Case
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Case Insights */}
          <div className="grid lg:grid-cols-2 gap-6">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Target className="w-5 h-5" />
                  <span>Case Strength Analysis</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-foreground">Overall Strength</span>
                    <span className="text-2xl font-bold text-primary">{caseInsights.strengthScore}%</span>
                  </div>
                  <Progress value={caseInsights.strengthScore} className="h-3" />
                </div>

                <div className="space-y-3">
                  <div>
                    <h4 className="text-sm font-semibold text-green-500 mb-2 flex items-center">
                      <CheckCircle className="w-4 h-4 mr-1" />
                      Strengths
                    </h4>
                    <ul className="space-y-1">
                      {caseInsights.strengths.map((strength, index) => (
                        <li key={index} className="text-sm text-muted-foreground flex items-start">
                          <span className="w-1 h-1 bg-green-500 rounded-full mt-2 mr-2 flex-shrink-0" />
                          {strength}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold text-amber-500 mb-2 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      Areas of Concern
                    </h4>
                    <ul className="space-y-1">
                      {caseInsights.weaknesses.map((weakness, index) => (
                        <li key={index} className="text-sm text-muted-foreground flex items-start">
                          <span className="w-1 h-1 bg-amber-500 rounded-full mt-2 mr-2 flex-shrink-0" />
                          {weakness}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Lightbulb className="w-5 h-5" />
                  <span>AI Recommendations</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {caseInsights.recommendations.map((recommendation, index) => (
                    <div key={index} className="p-3 rounded-lg bg-primary/5 border border-primary/20">
                      <div className="flex items-start space-x-2">
                        <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                          <span className="text-xs font-semibold text-primary">{index + 1}</span>
                        </div>
                        <p className="text-sm text-foreground">{recommendation}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="precedents" className="space-y-6">
          {/* Legal Precedents Search */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Search className="w-5 h-5" />
                <span>Search Legal Precedents</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex space-x-2">
                <Input
                  placeholder="Search by case name, legal principle, or keywords..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1"
                />
                <Button>
                  <Search className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Precedents List */}
          <div className="space-y-4">
            {legalPrecedents.map((precedent, index) => (
              <Card key={index} className="bg-card border-border">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-foreground">{precedent.case}</h3>
                      <p className="text-sm text-muted-foreground">
                        {precedent.court} • {precedent.year}
                      </p>
                    </div>
                    <Badge variant={precedent.relevance === "High" ? "default" : "secondary"}>
                      {precedent.relevance} Relevance
                    </Badge>
                  </div>
                  <p className="text-sm text-foreground mb-2">{precedent.principle}</p>
                  <p className="text-xs text-muted-foreground">{precedent.impact}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="similar" className="space-y-6">
          {/* Similar Cases */}
          <div className="space-y-4">
            {similarCases.map((case_item, index) => (
              <Card key={index} className="bg-card border-border">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-foreground">{case_item.title}</h3>
                      <p className="text-sm text-muted-foreground">
                        {case_item.court} • {case_item.citation}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant={case_item.outcome === "Conviction" ? "default" : "destructive"}>
                        {case_item.outcome}
                      </Badge>
                      <span className="text-sm font-medium text-primary">{case_item.relevance}% match</span>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {case_item.keyPoints.map((point, pointIndex) => (
                      <Badge key={pointIndex} variant="outline" className="text-xs">
                        {point}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="predictions" className="space-y-6">
          {/* Predictive Analytics */}
          <div className="grid lg:grid-cols-2 gap-6">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="w-5 h-5" />
                  <span>Case Outcome Prediction</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center">
                  <div className="text-4xl font-bold text-primary mb-2">
                    {predictiveAnalytics.convictionProbability}%
                  </div>
                  <p className="text-sm text-muted-foreground">Conviction Probability</p>
                  <Progress value={predictiveAnalytics.convictionProbability} className="mt-3" />
                </div>

                <div className="pt-4 border-t border-border">
                  <p className="text-sm font-medium text-foreground mb-2">Estimated Time to Trial</p>
                  <p className="text-lg font-semibold text-primary">{predictiveAnalytics.timeToTrial}</p>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Critical Success Factors</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {predictiveAnalytics.criticalFactors.map((factor, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-foreground">{factor.factor}</span>
                      <span className="text-sm text-muted-foreground">{factor.weight}% weight</span>
                    </div>
                    <Progress value={factor.score} className="h-2" />
                    <p className="text-xs text-muted-foreground">Score: {factor.score}%</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Risk Factors */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-amber-500" />
                <span>Risk Factors</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                {predictiveAnalytics.riskFactors.map((risk, index) => (
                  <div key={index} className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
                    <div className="flex items-center space-x-2">
                      <AlertCircle className="w-4 h-4 text-amber-500 flex-shrink-0" />
                      <p className="text-sm text-foreground">{risk}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
