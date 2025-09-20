import { SupervisoryDashboard } from "@/components/supervisor/supervisory-dashboard"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"

export default function SupervisorPage() {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />

      <main className="container mx-auto px-6 py-8">
        <SupervisoryDashboard />
      </main>
    </div>
  )
}
