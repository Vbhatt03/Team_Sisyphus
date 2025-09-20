import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { User, MapPin, Calendar, Scale, FileText, Shield } from "lucide-react"

interface CaseOverviewProps {
  caseData: any
}

export function CaseOverview({ caseData }: CaseOverviewProps) {
  return (
    <div className="grid lg:grid-cols-2 gap-6">
      {/* Case Information */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="w-5 h-5" />
            <span>Case Information</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">FIR Number</p>
              <p className="text-foreground">{caseData.id}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Status</p>
              <Badge className="bg-blue-500/10 text-blue-500">{caseData.status}</Badge>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Priority</p>
              <Badge className="bg-red-500/10 text-red-500">{caseData.priority}</Badge>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Assigned Officer</p>
              <p className="text-foreground">{caseData.assignedOfficer}</p>
            </div>
          </div>

          <div>
            <p className="text-sm font-medium text-muted-foreground mb-2">Legal Sections</p>
            <div className="flex flex-wrap gap-2">
              {caseData.sections.map((section: string) => (
                <Badge key={section} variant="outline">
                  {section}
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <p className="text-sm font-medium text-muted-foreground">Location</p>
            <div className="flex items-center space-x-2 mt-1">
              <MapPin className="w-4 h-4 text-muted-foreground" />
              <p className="text-foreground">{caseData.location}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Victim & Accused Information */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <User className="w-5 h-5" />
            <span>Parties Involved</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm font-medium text-muted-foreground mb-2">Victim Information</p>
            <div className="p-3 bg-muted/50 rounded-lg space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Age:</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium">{caseData.victimAge} years</span>
                  {caseData.victimAge < 18 && <Badge className="bg-amber-500/10 text-amber-500 text-xs">Minor</Badge>}
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Identity:</span>
                <span className="text-sm font-medium">Protected (POCSO Case)</span>
              </div>
            </div>
          </div>

          <div>
            <p className="text-sm font-medium text-muted-foreground mb-2">Accused Information</p>
            <div className="p-3 bg-muted/50 rounded-lg space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Number of Accused:</span>
                <span className="text-sm font-medium">{caseData.accusedCount}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Status:</span>
                <Badge className="bg-amber-500/10 text-amber-500 text-xs">Investigation Ongoing</Badge>
              </div>
            </div>
          </div>

          <div>
            <p className="text-sm font-medium text-muted-foreground mb-2">Special Considerations</p>
            <div className="space-y-2">
              <div className="flex items-center space-x-2 p-2 bg-amber-500/10 rounded-lg">
                <Shield className="w-4 h-4 text-amber-500" />
                <span className="text-sm text-amber-700">POCSO Act applicable (Minor victim)</span>
              </div>
              <div className="flex items-center space-x-2 p-2 bg-red-500/10 rounded-lg">
                <Scale className="w-4 h-4 text-red-500" />
                <span className="text-sm text-red-700">High priority case</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Timeline */}
      <Card className="bg-card border-border lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Calendar className="w-5 h-5" />
            <span>Case Timeline</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-start space-x-4">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />
              <div className="flex-1">
                <p className="text-sm font-medium text-foreground">Case Created</p>
                <p className="text-xs text-muted-foreground">January 20, 2025 - 10:30 AM</p>
                <p className="text-xs text-muted-foreground">FIR uploaded and AI processing completed</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />
              <div className="flex-1">
                <p className="text-sm font-medium text-foreground">Victim Statement Recorded</p>
                <p className="text-xs text-muted-foreground">January 20, 2025 - 2:15 PM</p>
                <p className="text-xs text-muted-foreground">Statement recorded under Section 183 BNSS</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />
              <div className="flex-1">
                <p className="text-sm font-medium text-foreground">Medical Examination Completed</p>
                <p className="text-xs text-muted-foreground">January 20, 2025 - 4:45 PM</p>
                <p className="text-xs text-muted-foreground">Medical report submitted to evidence locker</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <div className="w-2 h-2 bg-amber-500 rounded-full mt-2" />
              <div className="flex-1">
                <p className="text-sm font-medium text-foreground">Crime Scene Investigation</p>
                <p className="text-xs text-muted-foreground">Scheduled: January 22, 2025 - 12:00 PM</p>
                <p className="text-xs text-muted-foreground">Pending - 18 hours remaining</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
