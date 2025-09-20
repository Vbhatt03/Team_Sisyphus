import { InvestigationWorkspace } from "@/components/cases/investigation-workspace"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"

interface CasePageProps {
  params: {
    id: string
  }
}

export default function CasePage({ params }: CasePageProps) {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />

      <main className="container mx-auto px-6 py-8">
        <InvestigationWorkspace caseId={params.id} />
      </main>
    </div>
  )
}
