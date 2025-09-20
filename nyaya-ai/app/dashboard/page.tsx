import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { CaseStats } from "@/components/dashboard/case-stats"
import { RecentCases } from "@/components/dashboard/recent-cases"
import { QuickActions } from "@/components/dashboard/quick-actions"

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />

      <main className="container mx-auto px-6 py-8">
        <div className="space-y-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Investigation Dashboard</h1>
              <p className="text-muted-foreground mt-2">Manage your cases and track compliance status</p>
            </div>
          </div>

          <CaseStats />

          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <RecentCases />
            </div>
            <div>
              <QuickActions />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
