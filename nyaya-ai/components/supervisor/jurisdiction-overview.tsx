import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Users, MapPin, TrendingUp, Eye, AlertTriangle, CheckCircle } from "lucide-react"

interface JurisdictionOverviewProps {
  stats: any
  selectedDistrict: string
  selectedTimeframe: string
}

export function JurisdictionOverview({ stats, selectedDistrict, selectedTimeframe }: JurisdictionOverviewProps) {
  // Mock district performance data
  const districtPerformance = [
    {
      name: "Central District",
      officer: "ACP Rajesh Kumar",
      activeCases: 23,
      completedCases: 18,
      complianceScore: 92,
      overdueItems: 2,
      trend: "up",
    },
    {
      name: "North District",
      officer: "ACP Priya Sharma",
      activeCases: 19,
      completedCases: 15,
      complianceScore: 88,
      overdueItems: 3,
      trend: "up",
    },
    {
      name: "South District",
      officer: "ACP Amit Singh",
      activeCases: 25,
      completedCases: 20,
      complianceScore: 85,
      overdueItems: 4,
      trend: "down",
    },
    {
      name: "East District",
      officer: "ACP Sunita Verma",
      activeCases: 22,
      completedCases: 14,
      complianceScore: 83,
      overdueItems: 3,
      trend: "stable",
    },
  ]

  const recentAlerts = [
    {
      id: 1,
      type: "critical",
      message: "FIR/2025/045 - POCSO deadline missed in North District",
      time: "2 hours ago",
      officer: "IO Rajesh",
    },
    {
      id: 2,
      type: "warning",
      message: "Medical examination pending for FIR/2025/048",
      time: "4 hours ago",
      officer: "IO Priya",
    },
    {
      id: 3,
      type: "info",
      message: "Chargesheet filed successfully for FIR/2025/042",
      time: "6 hours ago",
      officer: "IO Amit",
    },
  ]

  const getAlertColor = (type: string) => {
    switch (type) {
      case "critical":
        return "text-red-500 bg-red-500/10"
      case "warning":
        return "text-amber-500 bg-amber-500/10"
      case "info":
        return "text-blue-500 bg-blue-500/10"
      default:
        return "text-gray-500 bg-gray-500/10"
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
    <div className="grid lg:grid-cols-3 gap-6">
      {/* District Performance */}
      <div className="lg:col-span-2 space-y-6">
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MapPin className="w-5 h-5" />
              <span>District Performance Overview</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {districtPerformance.map((district) => (
                <div key={district.name} className="border border-border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-foreground">{district.name}</h3>
                      <p className="text-sm text-muted-foreground">{district.officer}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getTrendIcon(district.trend)}
                      <Button variant="ghost" size="sm">
                        <Eye className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-4 gap-4 mb-3">
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground">Active</p>
                      <p className="text-lg font-semibold text-foreground">{district.activeCases}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground">Completed</p>
                      <p className="text-lg font-semibold text-green-500">{district.completedCases}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground">Compliance</p>
                      <p className="text-lg font-semibold text-foreground">{district.complianceScore}%</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground">Overdue</p>
                      <p className="text-lg font-semibold text-red-500">{district.overdueItems}</p>
                    </div>
                  </div>

                  <Progress value={district.complianceScore} className="h-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Officer Performance Summary */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="w-5 h-5" />
              <span>Top Performing Officers</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { name: "IO Rajesh Kumar", cases: 8, compliance: 95, efficiency: "Excellent" },
                { name: "IO Priya Sharma", cases: 6, compliance: 92, efficiency: "Very Good" },
                { name: "IO Amit Singh", cases: 7, compliance: 89, efficiency: "Good" },
                { name: "IO Sunita Verma", cases: 5, compliance: 87, efficiency: "Good" },
              ].map((officer, index) => (
                <div key={officer.name} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground text-sm font-semibold">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium text-foreground">{officer.name}</p>
                      <p className="text-sm text-muted-foreground">{officer.cases} active cases</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-foreground">{officer.compliance}% compliance</p>
                    <Badge variant="outline" className="text-xs">
                      {officer.efficiency}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Alerts and Notifications */}
      <div className="space-y-6">
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5" />
              <span>Recent Alerts</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentAlerts.map((alert) => (
                <div key={alert.id} className={`p-3 rounded-lg ${getAlertColor(alert.type)}`}>
                  <p className="text-sm font-medium">{alert.message}</p>
                  <div className="flex items-center justify-between mt-2 text-xs opacity-75">
                    <span>{alert.officer}</span>
                    <span>{alert.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5" />
              <span>Quick Actions</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start bg-primary hover:bg-primary/90 text-primary-foreground">
              <AlertTriangle className="w-4 h-4 mr-2" />
              Review Overdue Cases
            </Button>
            <Button variant="outline" className="w-full justify-start bg-transparent">
              <Users className="w-4 h-4 mr-2" />
              Officer Performance Review
            </Button>
            <Button variant="outline" className="w-full justify-start bg-transparent">
              <TrendingUp className="w-4 h-4 mr-2" />
              Generate Monthly Report
            </Button>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle>System Health</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">Database Status</span>
              <Badge className="bg-green-500/10 text-green-500">Online</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">AI Services</span>
              <Badge className="bg-green-500/10 text-green-500">Operational</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Backup Status</span>
              <Badge className="bg-green-500/10 text-green-500">Up to date</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Security</span>
              <Badge className="bg-green-500/10 text-green-500">Secure</Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
