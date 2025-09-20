"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, Filter, Eye, AlertTriangle, Clock, CheckCircle, User, MapPin, Calendar } from "lucide-react"
import { useState } from "react"

interface CaseMonitoringProps {
  selectedDistrict: string
  selectedTimeframe: string
}

export function CaseMonitoring({ selectedDistrict, selectedTimeframe }: CaseMonitoringProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [priorityFilter, setPriorityFilter] = useState("all")

  // Mock case data for monitoring
  const cases = [
    {
      id: "FIR/2025/045",
      title: "Sexual Assault Case - Minor Victim",
      officer: "IO Rajesh Kumar",
      district: "Central District",
      status: "overdue",
      priority: "critical",
      compliance: 65,
      lastUpdate: "2 days ago",
      nextDeadline: "Medical exam overdue",
      daysActive: 8,
    },
    {
      id: "FIR/2025/046",
      title: "POCSO Case - School Premises",
      officer: "IO Priya Sharma",
      district: "North District",
      status: "on-track",
      priority: "high",
      compliance: 92,
      lastUpdate: "4 hours ago",
      nextDeadline: "Crime scene visit - 2 days",
      daysActive: 3,
    },
    {
      id: "FIR/2025/047",
      title: "Rape Case - Multiple Accused",
      officer: "IO Amit Singh",
      district: "South District",
      status: "at-risk",
      priority: "high",
      compliance: 78,
      lastUpdate: "1 day ago",
      nextDeadline: "Accused arrest - 1 day",
      daysActive: 12,
    },
    {
      id: "FIR/2025/048",
      title: "Sexual Harassment Case",
      officer: "IO Sunita Verma",
      district: "East District",
      status: "completed",
      priority: "medium",
      compliance: 95,
      lastUpdate: "3 hours ago",
      nextDeadline: "Chargesheet filed",
      daysActive: 25,
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "overdue":
        return "bg-red-500/10 text-red-500"
      case "at-risk":
        return "bg-amber-500/10 text-amber-500"
      case "on-track":
        return "bg-blue-500/10 text-blue-500"
      case "completed":
        return "bg-green-500/10 text-green-500"
      default:
        return "bg-gray-500/10 text-gray-500"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "overdue":
        return AlertTriangle
      case "at-risk":
        return Clock
      case "on-track":
        return Clock
      case "completed":
        return CheckCircle
      default:
        return Clock
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
      case "low":
        return "bg-gray-500/10 text-gray-500"
      default:
        return "bg-gray-500/10 text-gray-500"
    }
  }

  const filteredCases = cases.filter((case_) => {
    const matchesSearch =
      case_.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      case_.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      case_.officer.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || case_.status === statusFilter
    const matchesPriority = priorityFilter === "all" || case_.priority === priorityFilter
    return matchesSearch && matchesStatus && matchesPriority
  })

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card className="bg-card border-border">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search cases by ID, title, or officer..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-background border-border"
                />
              </div>
            </div>
            <div className="md:w-40">
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="bg-background border-border">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="overdue">Overdue</SelectItem>
                  <SelectItem value="at-risk">At Risk</SelectItem>
                  <SelectItem value="on-track">On Track</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="md:w-40">
              <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                <SelectTrigger className="bg-background border-border">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Priority</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Case List */}
      <div className="space-y-4">
        {filteredCases.map((case_) => {
          const StatusIcon = getStatusIcon(case_.status)
          return (
            <Card key={case_.id} className="bg-card border-border">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    <div className={`p-3 rounded-lg ${getStatusColor(case_.status)}`}>
                      <StatusIcon className="w-5 h-5" />
                    </div>

                    <div className="space-y-2">
                      <div>
                        <h3 className="font-semibold text-foreground">{case_.title}</h3>
                        <p className="text-sm text-muted-foreground">{case_.id}</p>
                      </div>

                      <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                        <div className="flex items-center space-x-1">
                          <User className="w-4 h-4" />
                          <span>{case_.officer}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <MapPin className="w-4 h-4" />
                          <span>{case_.district}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-4 h-4" />
                          <span>{case_.daysActive} days active</span>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(case_.status)}>{case_.status}</Badge>
                        <Badge className={getPriorityColor(case_.priority)}>{case_.priority}</Badge>
                        <span className="text-sm text-muted-foreground">Compliance: {case_.compliance}%</span>
                      </div>

                      <div className="text-sm">
                        <span className="text-muted-foreground">Next deadline: </span>
                        <span
                          className={
                            case_.status === "overdue" ? "text-red-500 font-medium" : "text-foreground font-medium"
                          }
                        >
                          {case_.nextDeadline}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-muted-foreground">Updated {case_.lastUpdate}</span>
                    <Button variant="ghost" size="sm">
                      <Eye className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {filteredCases.length === 0 && (
        <Card className="bg-card border-border">
          <CardContent className="p-12 text-center">
            <Search className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-foreground mb-2">No Cases Found</h3>
            <p className="text-muted-foreground">Try adjusting your search criteria or filters.</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
