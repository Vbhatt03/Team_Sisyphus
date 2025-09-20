import { CaseReportGenerator } from "@/components/cases/case-report-generator"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"

interface CaseReportPageProps {
  params: {
    id: string
  }
}

export default function CaseReportPage({ params }: CaseReportPageProps) {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />

      <main className="container mx-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground">Generate Case Report</h1>
            <p className="text-muted-foreground mt-2">Case ID: {params.id}</p>
          </div>

          <CaseReportGenerator caseId={params.id} />
        </div>
      </main>
    </div>
  )
}
