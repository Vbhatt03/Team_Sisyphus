import { ReportGenerator } from "@/components/reports/report-generator"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"

export default function ReportsPage() {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />

      <main className="container mx-auto px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground">AI-Assisted Report Generation</h1>
            <p className="text-muted-foreground mt-2">
              Generate comprehensive, court-ready reports with AI-powered compilation and analysis
            </p>
          </div>

          <ReportGenerator />
        </div>
      </main>
    </div>
  )
}
