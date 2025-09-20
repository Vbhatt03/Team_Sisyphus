"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { AlertCircle, LogIn, Shield } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

export function LoginForm() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [formData, setFormData] = useState({
    employeeId: "",
    password: "",
    role: "",
    district: "",
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    // Simulate authentication
    setTimeout(() => {
      if (formData.employeeId && formData.password && formData.role) {
        // Redirect to dashboard (would be handled by auth system)
        window.location.href = "/dashboard"
      } else {
        setError("Please fill in all required fields")
      }
      setIsLoading(false)
    }, 1000)
  }

  return (
    <Card className="w-full max-w-md bg-card border-border">
      <CardHeader className="space-y-4">
        <div className="flex items-center justify-center">
          <div className="flex items-center justify-center w-12 h-12 bg-primary rounded-lg">
            <Shield className="w-6 h-6 text-primary-foreground" />
          </div>
        </div>
        <div className="text-center">
          <CardTitle className="text-2xl font-bold text-foreground">Secure Access</CardTitle>
          <CardDescription className="text-muted-foreground">Login to NYAYA AI Investigation Platform</CardDescription>
        </div>
        <div className="flex justify-center">
          <Badge variant="outline" className="text-xs">
            Government Authorized Personnel Only
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="employeeId" className="text-foreground">
              Employee ID
            </Label>
            <Input
              id="employeeId"
              type="text"
              placeholder="Enter your employee ID"
              value={formData.employeeId}
              onChange={(e) => setFormData({ ...formData, employeeId: e.target.value })}
              className="bg-background border-border"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-foreground">
              Password
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="bg-background border-border"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="role" className="text-foreground">
              Role
            </Label>
            <Select value={formData.role} onValueChange={(value) => setFormData({ ...formData, role: value })}>
              <SelectTrigger className="bg-background border-border">
                <SelectValue placeholder="Select your role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="investigating-officer">Investigating Officer (IO)</SelectItem>
                <SelectItem value="acp">Assistant Commissioner of Police (ACP)</SelectItem>
                <SelectItem value="dcp">Deputy Commissioner of Police (DCP)</SelectItem>
                <SelectItem value="supervisor">Supervisory Officer</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="district" className="text-foreground">
              District/Jurisdiction
            </Label>
            <Select value={formData.district} onValueChange={(value) => setFormData({ ...formData, district: value })}>
              <SelectTrigger className="bg-background border-border">
                <SelectValue placeholder="Select your district" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="delhi-central">Delhi Central</SelectItem>
                <SelectItem value="delhi-north">Delhi North</SelectItem>
                <SelectItem value="delhi-south">Delhi South</SelectItem>
                <SelectItem value="mumbai-central">Mumbai Central</SelectItem>
                <SelectItem value="mumbai-south">Mumbai South</SelectItem>
                <SelectItem value="bangalore-city">Bangalore City</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button
            type="submit"
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
            disabled={isLoading}
          >
            {isLoading ? (
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                <span>Authenticating...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <LogIn className="w-4 h-4" />
                <span>Secure Login</span>
              </div>
            )}
          </Button>
        </form>

        <div className="text-center space-y-2">
          <p className="text-xs text-muted-foreground">This system is monitored and logged for security purposes.</p>
          <p className="text-xs text-muted-foreground">Unauthorized access is strictly prohibited.</p>
        </div>
      </CardContent>
    </Card>
  )
}
