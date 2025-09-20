"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { JurisdictionOverview } from "@/components/supervisor/jurisdiction-overview"
import { CaseMonitoring } from "@/components/supervisor/case-monitoring"
import { PerformanceAnalytics } from "@/components/supervisor/performance-analytics"
import { ComplianceReports } from "@/components/supervisor/compliance-reports"
import { AlertTriangle, CheckCircle, Clock, TrendingUp, TrendingDown, FileText } from "lucide-react"

export function SupervisoryDashboard() {
  const [selectedDistrict, setSelectedDistrict] = useState("all")
  const [selectedTimeframe, setSelectedTimeframe] = useState("30d")
  const [activeTab, setActiveTab] = useState("overview")

  // Mock supervisory data
  const jurisdictionStats = {
    totalCases: 156,
    activeCases: 89,
    completedCases: 67,
    overdueDeadlines: 12,
    complianceScore: 87,
    averageResolutionTime: 45, // days
    totalOfficers: 24,
    highPriorityCases: 18,
  }

  const districts = [
    { id: "all", name: "All Districts" },
    { id: "central", name: "Central District" },
    { id: "north", name: "North District" },
    { id: "south", name: "South District" },
    { id: "east", name: "East District" },
  ]

  const timeframes = [
    { id: "7d", name: "Last 7 days" },
    { id: "30d", name: "Last 30 days" },
    { id: "90d", name: "Last 3 months" },
    { id: "1y", name: "Last year" },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Supervisory Command Center</h1>
          <p className="text-muted-foreground mt-2">Monitor cases, track compliance, and analyze performance</p>
        </div>

        <div className="flex items-center space-x-4">
          <Select value={selectedDistrict} onValueChange={setSelectedDistrict}>
            <SelectTrigger className="w-48 bg-background border-border">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {districts.map((district) => (
                <SelectItem key={district.id} value={district.id}>
                  {district.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={selectedTimeframe} onValueChange={setSelectedTimeframe}>
            <SelectTrigger className="w-40 bg-background border-border">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {timeframes.map((timeframe) => (
                <SelectItem key={timeframe.id} value={timeframe.id}>
                  {timeframe.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Key Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-card border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Cases</p>
                <p className="text-3xl font-bold text-foreground">{jurisdictionStats.totalCases}</p>
                <div className="flex items-center space-x-1 mt-1">
                  <TrendingUp className="w-3 h-3 text-green-500" />
                  <span className="text-xs text-green-500">+12% from last month</span>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-blue-500/10">
                <FileText className="w-6 h-6 text-blue-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active Cases</p>
                <p className="text-3xl font-bold text-foreground">{jurisdictionStats.activeCases}</p>
                <div className="flex items-center space-x-1 mt-1">
                  <Clock className="w-3 h-3 text-amber-500" />
                  <span className="text-xs text-amber-500">{jurisdictionStats.highPriorityCases} high priority</span>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-amber-500/10">
                <Clock className="w-6 h-6 text-amber-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Compliance Score</p>
                <p className="text-3xl font-bold text-foreground">{jurisdictionStats.complianceScore}%</p>
                <div className="flex items-center space-x-1 mt-1">
                  <TrendingUp className="w-3 h-3 text-green-500" />
                  <span className="text-xs text-green-500">+5% improvement</span>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-green-500/10">
                <CheckCircle className="w-6 h-6 text-green-500" />
              </div>
            </div>
            <Progress value={jurisdictionStats.complianceScore} className="mt-3" />
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Overdue Items</p>
                <p className="text-3xl font-bold text-red-500">{jurisdictionStats.overdueDeadlines}</p>
                <div className="flex items-center space-x-1 mt-1">
                  <TrendingDown className="w-3 h-3 text-red-500" />
                  <span className="text-xs text-red-500">Requires attention</span>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-red-500/10">
                <AlertTriangle className="w-6 h-6 text-red-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Dashboard Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Jurisdiction Overview</TabsTrigger>
          <TabsTrigger value="monitoring">Case Monitoring</TabsTrigger>
          <TabsTrigger value="analytics">Performance Analytics</TabsTrigger>
          <TabsTrigger value="compliance">Compliance Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <JurisdictionOverview
            stats={jurisdictionStats}
            selectedDistrict={selectedDistrict}
            selectedTimeframe={selectedTimeframe}
          />
        </TabsContent>

        <TabsContent value="monitoring" className="space-y-6">
          <CaseMonitoring selectedDistrict={selectedDistrict} selectedTimeframe={selectedTimeframe} />
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <PerformanceAnalytics selectedDistrict={selectedDistrict} selectedTimeframe={selectedTimeframe} />
        </TabsContent>

        <TabsContent value="compliance" className="space-y-6">
          <ComplianceReports selectedDistrict={selectedDistrict} selectedTimeframe={selectedTimeframe} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
