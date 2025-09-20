import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { BarChart3, TrendingUp, Users, Clock, Target, Award } from "lucide-react"

interface PerformanceAnalyticsProps {
  selectedDistrict: string
  selectedTimeframe: string
}

export function PerformanceAnalytics({ selectedDistrict, selectedTimeframe }: PerformanceAnalyticsProps) {
  // Mock analytics data
  const performanceMetrics = {
    averageResolutionTime: 42,
    caseCompletionRate: 78,
    complianceScore: 87,
    officerEfficiency: 85,
    convictionRate: 72,
    timelyCompletions: 89,
  }

  const topPerformers = [
    { name: "IO Rajesh Kumar", score: 95, cases: 12, efficiency: "Excellent" },
    { name: "IO Priya Sharma", score: 92, cases: 10, efficiency: "Very Good" },
    { name: "IO Amit Singh", score: 89, cases: 8, efficiency: "Good" },
    { name: "IO Sunita Verma", score: 87, cases: 9, efficiency: "Good" },
    { name: "IO Ravi Patel", score: 84, cases: 7, efficiency: "Satisfactory" },
  ]

  const complianceBreakdown = [
    { category: "POCSO Compliance", score: 92, trend: "up" },
    { category: "Evidence Management", score: 88, trend: "up" },
    { category: "Timeline Adherence", score: 85, trend: "stable" },
    { category: "Documentation Quality", score: 90, trend: "up" },
    { category: "Legal Procedures", score: 86, trend: "down" },
  ]

  const getEfficiencyColor = (efficiency: string) => {
    switch (efficiency) {
      case "Excellent":
        return "bg-green-500/10 text-green-500"
      case "Very Good":
        return "bg-blue-500/10 text-blue-500"
      case "Good":
        return "bg-amber-500/10 text-amber-500"
      case "Satisfactory":
        return "bg-orange-500/10 text-orange-500"
      default:
        return "bg-gray-500/10 text-gray-500"
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "up":
        return <TrendingUp className="w-4 h-4 text-green-500" />
      case "down":
        return <TrendingUp className="w-4 h-4 text-red-500 rotate-180" />
      default:
        return <div className="w-4 h-4 bg-gray-400 rounded-full" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Key Performance Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="w-5 h-5" />
              <span>Resolution Metrics</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Avg. Resolution Time</span>
                <span className="text-2xl font-bold text-foreground">
                  {performanceMetrics.averageResolutionTime} days
                </span>
              </div>
              <Progress value={75} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">Target: 35 days</p>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Completion Rate</span>
                <span className="text-2xl font-bold text-foreground">{performanceMetrics.caseCompletionRate}%</span>
              </div>
              <Progress value={performanceMetrics.caseCompletionRate} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">Target: 85%</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="w-5 h-5" />
              <span>Quality Metrics</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Compliance Score</span>
                <span className="text-2xl font-bold text-foreground">{performanceMetrics.complianceScore}%</span>
              </div>
              <Progress value={performanceMetrics.complianceScore} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">Target: 90%</p>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Conviction Rate</span>
                <span className="text-2xl font-bold text-foreground">{performanceMetrics.convictionRate}%</span>
              </div>
              <Progress value={performanceMetrics.convictionRate} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">Target: 80%</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="w-5 h-5" />
              <span>Team Performance</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Officer Efficiency</span>
                <span className="text-2xl font-bold text-foreground">{performanceMetrics.officerEfficiency}%</span>
              </div>
              <Progress value={performanceMetrics.officerEfficiency} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">24 active officers</p>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Timely Completions</span>
                <span className="text-2xl font-bold text-foreground">{performanceMetrics.timelyCompletions}%</span>
              </div>
              <Progress value={performanceMetrics.timelyCompletions} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">Within deadlines</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Top Performers */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Award className="w-5 h-5" />
              <span>Top Performing Officers</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topPerformers.map((officer, index) => (
                <div key={officer.name} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground text-sm font-semibold">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium text-foreground">{officer.name}</p>
                      <p className="text-sm text-muted-foreground">{officer.cases} cases handled</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-foreground">{officer.score}</p>
                    <Badge className={getEfficiencyColor(officer.efficiency)} variant="outline">
                      {officer.efficiency}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Compliance Breakdown */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5" />
              <span>Compliance Breakdown</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {complianceBreakdown.map((item) => (
                <div key={item.category} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-foreground">{item.category}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-bold">{item.score}%</span>
                      {getTrendIcon(item.trend)}
                    </div>
                  </div>
                  <Progress value={item.score} className="h-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
