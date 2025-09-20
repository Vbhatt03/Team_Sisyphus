import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Eye, Clock, AlertCircle } from "lucide-react"

export function RecentCases() {
  const cases = [
    {
      id: "FIR/2025/001",
      title: "Sexual Assault Case - Victim Age 16",
      status: "active",
      priority: "high",
      deadline: "2 days",
      compliance: "amber",
      lastUpdated: "2 hours ago",
    },
    {
      id: "FIR/2025/002",
      title: "Rape Case - Multiple Accused",
      status: "active",
      priority: "critical",
      deadline: "1 day",
      compliance: "red",
      lastUpdated: "4 hours ago",
    },
    {
      id: "FIR/2025/003",
      title: "POCSO Case - Minor Victim",
      status: "active",
      priority: "high",
      deadline: "3 days",
      compliance: "green",
      lastUpdated: "1 day ago",
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-blue-500/10 text-blue-500"
      case "completed":
        return "bg-green-500/10 text-green-500"
      default:
        return "bg-gray-500/10 text-gray-500"
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

  const getComplianceColor = (compliance: string) => {
    switch (compliance) {
      case "green":
        return "text-green-500"
      case "amber":
        return "text-amber-500"
      case "red":
        return "text-red-500"
      default:
        return "text-gray-500"
    }
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Recent Cases</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {cases.map((case_) => (
          <div key={case_.id} className="border border-border rounded-lg p-4 space-y-3">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <h3 className="font-semibold text-foreground">{case_.title}</h3>
                <p className="text-sm text-muted-foreground">{case_.id}</p>
              </div>
              <Button variant="ghost" size="sm">
                <Eye className="w-4 h-4" />
              </Button>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Badge className={getStatusColor(case_.status)}>{case_.status}</Badge>
                <Badge className={getPriorityColor(case_.priority)}>{case_.priority}</Badge>
              </div>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Clock className="w-4 h-4" />
                <span>Deadline: {case_.deadline}</span>
                <AlertCircle className={`w-4 h-4 ${getComplianceColor(case_.compliance)}`} />
              </div>
            </div>

            <p className="text-xs text-muted-foreground">Last updated: {case_.lastUpdated}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
