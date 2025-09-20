import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertTriangle, CheckCircle, Shield } from "lucide-react"

interface ComplianceReportsProps {
  selectedDistrict: string
  selectedTimeframe: string
}

export function ComplianceReports({ selectedDistrict, selectedTimeframe }: ComplianceReportsProps) {
  // Mock compliance data
  const complianceOverview = {
    overallScore: 87,
    totalViolations: 8,
    resolvedViolations: 6,
    pendingViolations: 2,
    criticalIssues: 1,
    improvementTrend: 5, // percentage improvement
  }

  const complianceCategories = [
    {
      category: "POCSO Act Compliance",
      score: 92,
      violations: 2,
      status: "good",
      description: "Minor victim procedures and timelines",
    },
    {
      category: "Evidence Management",
      score: 88,
      violations: 1,
      status: "good",
      description: "Chain of custody and documentation",
    },
    {
      category: "Timeline Adherence",
      score: 85,
      violations: 3,
      status: "warning",
      description: "Legal deadlines and procedural timelines",
    },
    {
      category: "Documentation Quality",
      score: 90,
      violations: 1,
      status: "good",
      description: "Case diary and report completeness",
    },
    {
      category: "Legal Procedures",
      score: 82,
      violations: 1,
      status: "warning",
      description: "Arrest procedures and rights compliance",
    },
  ]

  const recentViolations = [
    {
      id: "V001",
      case: "FIR/2025/045",
      officer: "IO Rajesh Kumar",
      violation: "Medical examination deadline missed",
      severity: "critical",
      status: "pending",
      date: "2025-01-20",
    },
    {
      id: "V002",
      case: "FIR/2025/043",
      officer: "IO Priya Sharma",
      violation: "Incomplete evidence documentation",
      severity: "medium",
      status: "resolved",
      date: "2025-01-18",
    },
    {
      id: "V003",
      case: "FIR/2025/041",
      officer: "IO Amit Singh",
      violation: "Delayed victim statement recording",
      severity: "high",
      status: "resolved",
      date: "2025-01-15",
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "good":
        return "text-green-500"
      case "warning":
        return "text-amber-500"
      case "critical":
        return "text-red-500"
      default:
        return "text-gray-500"
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-500/10 text-red-500"
      case "high":
        return "bg-amber-500/10 text-amber-500"
      case "medium":
        return "bg-blue-500/10 text-blue-500"
      case "low":
        return "bg-gray-500/10 text-gray-500"
      default:
        return "bg-gray-500/10 text-gray-500"
    }
  }

  const getViolationStatusColor = (status: string) => {
    switch (status) {
      case "resolved":
        return "bg-green-500/10 text-green-500"
      case "pending":
        return "bg-amber-500/10 text-amber-500"
      case "investigating":
        return "bg-blue-500/10 text-blue-500"
      default:
        return "bg-gray-500/10 text-gray-500"
    }
  }

  return (
    <div className="space-y-6">
      {/* Compliance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-card border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Overall Score</p>
                <p className="text-3xl font-bold text-foreground">{complianceOverview.overallScore}%</p>
                <div className="flex items-center space-x-1 mt-1">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  <span className="text-xs text-green-500">+{complianceOverview.improvementTrend}% this month</span>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-green-500/10">
                <Shield className="w-6 h-6 text-green-500" />
              </div>
            </div>
            <Progress value={complianceOverview.overallScore} className="mt-3" />
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Violations</p>
                <p className="text-3xl font-bold text-foreground">{complianceOverview.totalViolations}</p>
                <p className="text-xs text-muted-foreground mt-1">This period</p>
              </div>
              <div className="p-3 rounded-lg bg-amber-500/10">
                <AlertTriangle className="w-6 h-6 text-amber-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Resolved</p>
                <p className="text-3xl font-bold text-green-500">{complianceOverview.resolvedViolations}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {Math.round((complianceOverview.resolvedViolations / complianceOverview.totalViolations) * 100)}%
                  resolution rate
                </p>
              </div>
              <div className="p-3 rounded-lg bg-green-500/10">
                <CheckCircle className="w-6 h-6 text-green-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Critical Issues</p>
                <p className="text-3xl font-bold text-red-500">{complianceOverview.criticalIssues}</p>
                <p className="text-xs text-muted-foreground mt-1">Require immediate action</p>
              </div>
              <div className="p-3 rounded-lg bg-red-500/10">
                <AlertTriangle className="w-6 h-6 text-red-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Critical Issues Alert */}
      {complianceOverview.criticalIssues > 0 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            There are {complianceOverview.criticalIssues} critical compliance issue(s) that require immediate
            supervisory intervention. Review the violations list below for details.
          </AlertDescription>
        </Alert>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Compliance Categories */}
        <Card className="bg-card border-border">
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Compliance by Category</h3>
            <div className="space-y-4">
              {complianceCategories.map((category, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-foreground">{category.category}</span>
                    <div className="flex items-center space-x-2">
                      <span className={`text-sm font-medium ${getStatusColor(category.status)}`}>
                        {category.score}%
                      </span>
                      {category.violations > 0 && (
                        <span className="text-xs px-2 py-1 rounded-full bg-amber-500/10 text-amber-500">
                          {category.violations} violations
                        </span>
                      )}
                    </div>
                  </div>
                  <Progress value={category.score} className="h-2" />
                  <p className="text-xs text-muted-foreground">{category.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Violations */}
        <Card className="bg-card border-border">
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Recent Violations</h3>
            <div className="space-y-3">
              {recentViolations.map((violation) => (
                <div key={violation.id} className="p-3 rounded-lg border border-border bg-muted/30">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="text-sm font-medium text-foreground">{violation.case}</span>
                        <span className={`text-xs px-2 py-1 rounded-full ${getSeverityColor(violation.severity)}`}>
                          {violation.severity}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded-full ${getViolationStatusColor(violation.status)}`}>
                          {violation.status}
                        </span>
                      </div>
                      <p className="text-sm text-foreground mb-1">{violation.violation}</p>
                      <p className="text-xs text-muted-foreground">Officer: {violation.officer}</p>
                    </div>
                    <span className="text-xs text-muted-foreground">{violation.date}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
