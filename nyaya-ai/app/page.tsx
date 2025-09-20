import { LoginForm } from "@/components/auth/login-form"
import { Shield, Scale, FileText } from "lucide-react"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-lg">
                <Shield className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">NYAYA AI</h1>
                <p className="text-sm text-muted-foreground">Intelligent Investigation Platform</p>
              </div>
            </div>
            <div className="text-sm text-muted-foreground">Government of India | Ministry of Home Affairs</div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Side - Information */}
          <div className="space-y-8">
            <div className="space-y-4">
              <h2 className="text-4xl font-bold text-foreground leading-tight">
                Empowering Justice Through
                <span className="text-primary block">Intelligent Investigation</span>
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed">
                NYAYA AI transforms sexual offense investigations with AI-powered compliance tracking, automated
                documentation, and intelligent case management to ensure 100% procedural accuracy.
              </p>
            </div>

            <div className="grid gap-6">
              <div className="flex items-start space-x-4">
                <div className="flex items-center justify-center w-12 h-12 bg-success/10 rounded-lg">
                  <FileText className="w-6 h-6 text-success" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-2">Automated Compliance</h3>
                  <p className="text-muted-foreground">
                    Real-time tracking of legal deadlines and procedural requirements with intelligent alerts.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="flex items-center justify-center w-12 h-12 bg-primary/10 rounded-lg">
                  <Scale className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-2">Legal Intelligence</h3>
                  <p className="text-muted-foreground">
                    AI-powered insights from Supreme Court and High Court precedents to strengthen cases.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="flex items-center justify-center w-12 h-12 bg-warning/10 rounded-lg">
                  <Shield className="w-6 h-6 text-warning" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-2">Secure Evidence Management</h3>
                  <p className="text-muted-foreground">
                    End-to-end encrypted digital evidence locker with immutable audit trails.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Login Form */}
          <div className="flex justify-center lg:justify-end">
            <LoginForm />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card mt-16">
        <div className="container mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-sm text-muted-foreground">© 2025 NYAYA AI. Developed for the Government of India.</div>
            <div className="flex items-center space-x-6 text-sm text-muted-foreground">
              <span>Secure • Compliant • Intelligent</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
