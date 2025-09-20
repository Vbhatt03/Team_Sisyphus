import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Plus, Upload, Search, BarChart3 } from "lucide-react"
import Link from "next/link"

export function QuickActions() {
  const actions = [
    {
      title: "New Case",
      description: "Start a new investigation",
      icon: Plus,
      href: "/cases/new",
      color: "bg-primary hover:bg-primary/90 text-primary-foreground",
    },
    {
      title: "Upload Evidence",
      description: "Add documents to existing case",
      icon: Upload,
      href: "/evidence/upload",
      color: "bg-secondary hover:bg-secondary/90 text-secondary-foreground",
    },
    {
      title: "Search Cases",
      description: "Find specific case files",
      icon: Search,
      href: "/cases/search",
      color: "bg-secondary hover:bg-secondary/90 text-secondary-foreground",
    },
    {
      title: "Generate Report",
      description: "Create compliance reports",
      icon: BarChart3,
      href: "/reports",
      color: "bg-secondary hover:bg-secondary/90 text-secondary-foreground",
    },
  ]

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {actions.map((action) => (
          <Link key={action.title} href={action.href}>
            <Button className={`w-full justify-start space-x-3 h-auto p-4 ${action.color}`}>
              <action.icon className="w-5 h-5" />
              <div className="text-left">
                <div className="font-semibold">{action.title}</div>
                <div className="text-sm opacity-90">{action.description}</div>
              </div>
            </Button>
          </Link>
        ))}
      </CardContent>
    </Card>
  )
}
