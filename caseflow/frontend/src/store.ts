import { create } from 'zustand'
import axios from 'axios'

// Optional explicit API URL; if not set we will attempt detection across common ports.
const ENV_API = import.meta.env.VITE_API_URL as string | undefined

// Types
interface User {
  id: number
  username: string
}

interface Case {
  id: number
  name: string
  created_at: string
}

interface UploadStatus {
  fir: boolean
  statement: boolean
  victim_med: boolean | 'skipped'
  accused_med: boolean | 'skipped'
}

interface ChecklistItem {
  id: number
  section: string
  text: string
  checked: boolean
  updated_at: string
}

interface CaseDiaryPage {
  page_number: number
  content: string
  updated_at: string
  total_pages: number
}

// API Client
class ApiClient {
  private token: string | null = localStorage.getItem('token')
  public baseUrl: string

  constructor() {
    // Start with env override, stored preference, or common default.
    this.baseUrl = ENV_API || localStorage.getItem('caseflow_base_url') || 'http://localhost:8000'
  }

  setBaseUrl(url: string) {
    this.baseUrl = url
    localStorage.setItem('caseflow_base_url', url)
  }

  async detectBaseUrl(): Promise<string | null> {
    const candidates: string[] = []
    if (ENV_API) candidates.push(ENV_API)
    const stored = localStorage.getItem('caseflow_base_url')
    if (stored && !candidates.includes(stored)) candidates.push(stored)
    for (const c of ['http://localhost:8000','http://127.0.0.1:8000','http://localhost:8001','http://127.0.0.1:8001']) {
      if (!candidates.includes(c)) candidates.push(c)
    }
    for (const candidate of candidates) {
      try {
        const res = await axios.get(candidate + '/health', { timeout: 1200 })
        if (res.status === 200) {
          this.setBaseUrl(candidate)
          return candidate
        }
      } catch (_) { /* ignore and continue */ }
    }
    return null
  }

  setToken(token: string) {
    this.token = token
    localStorage.setItem('token', token)
  }

  clearToken() {
    this.token = null
    localStorage.removeItem('token')
  }

  private getHeaders() {
    return this.token ? { Authorization: `Bearer ${this.token}` } : {}
  }

  async login(username: string, password: string) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    const response = await axios.post(`${this.baseUrl}/api/auth/login`, formData)
    return response.data
  }

  async health() {
    const response = await axios.get(`${this.baseUrl}/health`)
    return response.data
  }

  async getMe() {
    const response = await axios.get(`${this.baseUrl}/api/auth/me`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async createCase(name: string) {
    const formData = new FormData()
    formData.append('name', name)
    
    const response = await axios.post(`${this.baseUrl}/api/cases`, formData, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getCases() {
    const response = await axios.get(`${this.baseUrl}/api/cases`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async uploadFile(caseId: number, type: string, file: File | null, skip: boolean = false) {
    const formData = new FormData()
    formData.append('case_id', caseId.toString())
    formData.append('type', type)
    formData.append('skip', skip.toString())
    if (file) {
      formData.append('file', file)
    }
    
    const response = await axios.post(`${this.baseUrl}/api/upload`, formData, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async parseDocuments(caseId: number) {
    const formData = new FormData()
    formData.append('case_id', caseId.toString())
    
    const response = await axios.post(`${this.baseUrl}/api/parse`, formData, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async runCompliance(caseId: number) {
    const formData = new FormData()
    formData.append('case_id', caseId.toString())
    
    const response = await axios.post(`${this.baseUrl}/api/compliance/run`, formData, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getCompliance(caseId: number) {
    const response = await axios.get(`${this.baseUrl}/api/compliance?case_id=${caseId}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async updateComplianceItem(itemId: number, checked?: boolean, text?: string) {
    const data: any = {}
    if (checked !== undefined) data.checked = checked
    if (text !== undefined) data.text = text
    
    const response = await axios.patch(`${this.baseUrl}/api/compliance/${itemId}`, data, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async generateCaseDiary(caseId: number) {
    const formData = new FormData()
    formData.append('case_id', caseId.toString())
    
    const response = await axios.post(`${this.baseUrl}/api/case-diary/generate`, formData, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getCaseDiaryPage(caseId: number, pageNumber: number = 1) {
    const response = await axios.get(
      `${this.baseUrl}/api/case-diary?case_id=${caseId}&page_number=${pageNumber}`,
      { headers: this.getHeaders() }
    )
    return response.data
  }

  async saveCaseDiaryPage(caseId: number, pageNumber: number, content: string) {
    const formData = new FormData()
    formData.append('case_id', caseId.toString())
    formData.append('page_number', pageNumber.toString())
    formData.append('content', content)
    
    const response = await axios.put(`${this.baseUrl}/api/case-diary`, formData, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getNextDiaryPage(caseId: number, currentPageNumber: number) {
    const formData = new FormData()
    formData.append('case_id', caseId.toString())
    formData.append('current_page_number', currentPageNumber.toString())
    
    const response = await axios.post(`${this.baseUrl}/api/case-diary/next`, formData, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async generateChargesheet(caseId: number) {
    const formData = new FormData()
    formData.append('case_id', caseId.toString())
    
    const response = await axios.post(`${this.baseUrl}/api/chargesheet/generate`, formData, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getFiles(caseId: number, kind: string) {
    const response = await axios.get(
      `${this.baseUrl}/api/files?case_id=${caseId}&kind=${kind}`,
      { headers: this.getHeaders() }
    )
    return response.data
  }

  getDownloadUrl(caseId: number, path: string) {
    return `${this.baseUrl}/api/files/download?case_id=${caseId}&path=${path}`
  }
}

const apiClient = new ApiClient()

// Store
interface AppState {
  // Auth
  user: User | null
  isAuthenticated: boolean
  
  // Current case
  currentCaseId: number | null
  currentCase: Case | null
  
  // Upload wizard state
  uploadStatus: UploadStatus
  uploadLogs: string[]
  
  // Compliance state
  checklistItems: ChecklistItem[]
  
  // Case diary state
  currentDiaryPage: CaseDiaryPage | null
  
  // Actions
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  setCurrentCase: (caseId: number) => void
  createCase: (name: string) => Promise<Case>
  
  uploadFile: (type: string, file: File | null, skip?: boolean) => Promise<void>
  parseDocuments: () => Promise<void>
  
  loadCompliance: () => Promise<void>
  updateChecklistItem: (itemId: number, checked?: boolean, text?: string) => Promise<void>
  
  loadCaseDiaryPage: (pageNumber?: number) => Promise<void>
  saveDiaryPage: (content: string) => Promise<void>
  nextDiaryPage: () => Promise<void>
  
  generateFinalReports: () => Promise<void>
  checkHealth: () => Promise<any>
  autoDetectApi: () => Promise<string | null>
  setApiBase: (url: string) => void
  getApiBase: () => string
  resetApiBase: () => void
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial state
  user: null,
  isAuthenticated: false,
  currentCaseId: null,
  currentCase: null,
  uploadStatus: {
    fir: false,
    statement: false,
    victim_med: false,
    accused_med: false,
  },
  uploadLogs: [],
  checklistItems: [],
  currentDiaryPage: null,

  // Auth actions
  login: async (username: string, password: string) => {
    // If health fails, try auto-detect before attempting login
    try {
      await apiClient.health()
    } catch {
      await apiClient.detectBaseUrl()
    }
    const tried: string[] = []
    const attemptLogin = async () => {
      try {
        console.log('[CaseFlow] Attempting login via', apiClient.baseUrl)
        const response = await apiClient.login(username, password)
        apiClient.setToken(response.access_token)
        set({ user: response.user, isAuthenticated: true })
        console.log('[CaseFlow] Login success on', apiClient.baseUrl)
        return true
      } catch (err: any) {
        const status = err?.response?.status
        if (status === 401) throw err // invalid credentials; don't retry
        // Network or other issue: mark tried and explore other candidates
        tried.push(apiClient.baseUrl)
        console.warn('[CaseFlow] Login attempt failed on', apiClient.baseUrl, err?.message || err)
        return false
      }
    }

    if (await attemptLogin()) return

    // Build candidate list excluding already tried
    const candidates = ['http://localhost:8000','http://127.0.0.1:8000','http://localhost:8001','http://127.0.0.1:8001']
      .filter(u => !tried.includes(u) && u !== apiClient.baseUrl)

    for (const candidate of candidates) {
      apiClient.setBaseUrl(candidate)
      try {
        const ok = await attemptLogin()
        if (ok) return
      } catch (e) {
        throw e // 401 bubbled
      }
    }
    throw new Error('All API base URL login attempts failed. Last tried: ' + apiClient.baseUrl)
  },

  // Health / connectivity check
  checkHealth: async () => {
    try {
      return await apiClient.health()
    } catch (e) {
      return null
    }
  },
  autoDetectApi: async () => {
    console.log('[CaseFlow] Attempting API auto-detect...')
    const url = await apiClient.detectBaseUrl()
    if (url) {
      console.log('[CaseFlow] API detected at', url)
    } else {
      console.warn('[CaseFlow] API auto-detect failed: no reachable candidate ports')
    }
    return url
  },
  setApiBase: (url: string) => {
    apiClient.setBaseUrl(url)
    console.log('[CaseFlow] API base URL manually set to', url)
  },
  getApiBase: () => apiClient.baseUrl,
  resetApiBase: () => {
    localStorage.removeItem('caseflow_base_url')
    apiClient.setBaseUrl('http://localhost:8000')
    console.log('[CaseFlow] API base URL reset to default http://localhost:8000')
  },

  logout: () => {
    apiClient.clearToken()
    set({ 
      user: null, 
      isAuthenticated: false, 
      currentCaseId: null, 
      currentCase: null,
      uploadStatus: { fir: false, statement: false, victim_med: false, accused_med: false },
      uploadLogs: [],
      checklistItems: [],
      currentDiaryPage: null
    })
  },

  // Case actions
  setCurrentCase: (caseId: number) => {
    set({ 
      currentCaseId: caseId,
      uploadStatus: { fir: false, statement: false, victim_med: false, accused_med: false },
      uploadLogs: [],
      checklistItems: [],
      currentDiaryPage: null
    })
  },

  createCase: async (name: string) => {
    const newCase = await apiClient.createCase(name)
    set({ currentCaseId: newCase.id, currentCase: newCase })
    return newCase
  },

  // Upload actions
  uploadFile: async (type: string, file: File | null, skip = false) => {
    const { currentCaseId } = get()
    if (!currentCaseId) throw new Error('No case selected')

    const result = await apiClient.uploadFile(currentCaseId, type, file, skip)
    
    set((state) => ({
      uploadStatus: {
        ...state.uploadStatus,
        [type]: skip ? 'skipped' : true
      },
      uploadLogs: [...state.uploadLogs, `${type}: ${result.status}`]
    }))
  },

  parseDocuments: async () => {
    const { currentCaseId } = get()
    if (!currentCaseId) throw new Error('No case selected')

    const result = await apiClient.parseDocuments(currentCaseId)
    
    set((state) => ({
      uploadLogs: [...state.uploadLogs, ...result.logs]
    }))

    if (result.errors.length > 0) {
      throw new Error(result.errors.join(', '))
    }
  },

  // Compliance actions
  loadCompliance: async () => {
    const { currentCaseId } = get()
    if (!currentCaseId) throw new Error('No case selected')

    const items = await apiClient.getCompliance(currentCaseId)
    set({ checklistItems: items })
  },

  updateChecklistItem: async (itemId: number, checked?: boolean, text?: string) => {
    await apiClient.updateComplianceItem(itemId, checked, text)
    
    // Update local state
    set((state) => ({
      checklistItems: state.checklistItems.map(item =>
        item.id === itemId ? { ...item, checked: checked ?? item.checked, text: text ?? item.text } : item
      )
    }))
  },

  // Case diary actions
  loadCaseDiaryPage: async (pageNumber = 1) => {
    const { currentCaseId } = get()
    if (!currentCaseId) throw new Error('No case selected')

    const page = await apiClient.getCaseDiaryPage(currentCaseId, pageNumber)
    set({ currentDiaryPage: page })
  },

  saveDiaryPage: async (content: string) => {
    const { currentCaseId, currentDiaryPage } = get()
    if (!currentCaseId || !currentDiaryPage) throw new Error('No case or page selected')

    await apiClient.saveCaseDiaryPage(currentCaseId, currentDiaryPage.page_number, content)
    
    set((state) => ({
      currentDiaryPage: state.currentDiaryPage ? {
        ...state.currentDiaryPage,
        content,
        updated_at: new Date().toISOString()
      } : null
    }))
  },

  nextDiaryPage: async () => {
    const { currentCaseId, currentDiaryPage } = get()
    if (!currentCaseId || !currentDiaryPage) throw new Error('No case or page selected')

    const nextPage = await apiClient.getNextDiaryPage(currentCaseId, currentDiaryPage.page_number)
    set({ currentDiaryPage: nextPage })
  },

  // Final report generation
  generateFinalReports: async () => {
    const { currentCaseId } = get()
    if (!currentCaseId) throw new Error('No case selected')

    await apiClient.generateChargesheet(currentCaseId)
  }
}))

export { apiClient }