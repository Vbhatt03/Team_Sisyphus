import { CaseIntakeWizard } from "@/components/cases/case-intake-wizard"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"

export default function NewCasePage() {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />

      <main className="container mx-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground">Create New Case</h1>
            <p className="text-muted-foreground mt-2">Upload FIR and let AI extract case details automatically</p>
          </div>

          <CaseIntakeWizard />
        </div>
      </main>
    </div>
  )
}
