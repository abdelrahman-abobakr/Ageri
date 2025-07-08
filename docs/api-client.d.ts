/**
 * TypeScript definitions for the API Client
 */

export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'moderator' | 'researcher';
  is_approved: boolean;
  institution?: string;
  department?: string;
  phone?: string;
}

export interface Publication {
  id: number;
  title: string;
  abstract: string;
  authors: User[];
  corresponding_author: User;
  journal?: string;
  publication_date?: string;
  doi?: string;
  status: 'draft' | 'submitted' | 'under_review' | 'published' | 'rejected';
  is_public: boolean;
  pdf_file?: string;
  created_at: string;
  updated_at: string;
}

export interface Department {
  id: number;
  name: string;
  code: string;
  description?: string;
  head?: User;
  established_date?: string;
  contact_email?: string;
  contact_phone?: string;
}

export interface Lab {
  id: number;
  name: string;
  code: string;
  department: Department;
  supervisor?: User;
  description?: string;
  location?: string;
  capacity?: number;
}

export interface Announcement {
  id: number;
  title: string;
  content: string;
  author: User;
  status: 'draft' | 'published' | 'archived';
  target_audience: 'all' | 'approved' | 'researchers' | 'moderators' | 'admins';
  is_featured: boolean;
  publish_at?: string;
  created_at: string;
}

export interface Course {
  id: number;
  title: string;
  description: string;
  instructor: User;
  department: Department;
  duration_weeks: number;
  max_participants: number;
  current_participants: number;
  start_date: string;
  end_date: string;
  status: 'draft' | 'open' | 'in_progress' | 'completed' | 'cancelled';
  prerequisites?: string;
  fee: number;
}

export interface TestService {
  id: number;
  name: string;
  service_code: string;
  description: string;
  category: string;
  department: Department;
  lab?: Lab;
  base_price: number;
  is_free: boolean;
  estimated_duration?: string;
  status: 'active' | 'inactive' | 'maintenance';
  max_concurrent_requests: number;
  current_requests: number;
}

export interface ServiceRequest {
  id: number;
  request_id: string;
  service: TestService;
  client: any; // Client interface would be defined separately
  title: string;
  description: string;
  status: 'submitted' | 'under_review' | 'approved' | 'in_progress' | 'completed' | 'rejected';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  requested_date: string;
  estimated_cost?: number;
  final_cost?: number;
  assigned_technician?: User;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiErrorData {
  detail?: string;
  field_errors?: Record<string, string[]>;
  [key: string]: any;
}

export class ApiError extends Error {
  status: number;
  data: ApiErrorData;
  
  constructor(status: number, message: string, data?: ApiErrorData);
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  headers?: Record<string, string>;
  body?: string | FormData;
}

export interface QueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
  [key: string]: any;
}

export class AuthEndpoints {
  constructor(client: ApiClient);
  
  login(email: string, password: string): Promise<{ access: string; refresh: string; user: User }>;
  logout(): Promise<void>;
  register(userData: Partial<User> & { password: string }): Promise<User>;
  getCurrentUser(): Promise<User>;
  updateProfile(userData: Partial<User>): Promise<User>;
  getUsers(params?: QueryParams): Promise<PaginatedResponse<User>>;
}

export class ResearchEndpoints {
  constructor(client: ApiClient);
  
  getPublications(params?: QueryParams): Promise<PaginatedResponse<Publication>>;
  getPublication(id: number): Promise<Publication>;
  createPublication(data: Partial<Publication>): Promise<Publication>;
  updatePublication(id: number, data: Partial<Publication>): Promise<Publication>;
  deletePublication(id: number): Promise<void>;
  approvePublication(id: number, reviewData: any): Promise<Publication>;
}

export class OrganizationEndpoints {
  constructor(client: ApiClient);
  
  getDepartments(params?: QueryParams): Promise<PaginatedResponse<Department>>;
  getLabs(params?: QueryParams): Promise<PaginatedResponse<Lab>>;
  getEquipment(params?: QueryParams): Promise<PaginatedResponse<any>>;
  getStaff(params?: QueryParams): Promise<PaginatedResponse<User>>;
}

export class ContentEndpoints {
  constructor(client: ApiClient);
  
  getAnnouncements(params?: QueryParams): Promise<PaginatedResponse<Announcement>>;
  createAnnouncement(data: Partial<Announcement>): Promise<Announcement>;
  getPosts(params?: QueryParams): Promise<PaginatedResponse<any>>;
  createPost(data: any): Promise<any>;
}

export class TrainingEndpoints {
  constructor(client: ApiClient);
  
  getCourses(params?: QueryParams): Promise<PaginatedResponse<Course>>;
  getSummerTraining(params?: QueryParams): Promise<PaginatedResponse<any>>;
  getPublicServices(params?: QueryParams): Promise<PaginatedResponse<any>>;
  enrollInCourse(courseId: number, data?: any): Promise<any>;
  applyForSummerTraining(programId: number, data?: any): Promise<any>;
}

export class ServicesEndpoints {
  constructor(client: ApiClient);
  
  getTestServices(params?: QueryParams): Promise<PaginatedResponse<TestService>>;
  createServiceRequest(data: Partial<ServiceRequest>): Promise<ServiceRequest>;
  getServiceRequests(params?: QueryParams): Promise<PaginatedResponse<ServiceRequest>>;
  getClients(params?: QueryParams): Promise<PaginatedResponse<any>>;
}

export class FileUploadHelper {
  constructor(client: ApiClient);
  
  uploadFile(endpoint: string, file: File, additionalData?: Record<string, any>): Promise<any>;
}

export class ApiClient {
  baseURL: string;
  accessToken: string | null;
  refreshToken: string | null;
  
  auth: AuthEndpoints;
  research: ResearchEndpoints;
  organization: OrganizationEndpoints;
  content: ContentEndpoints;
  training: TrainingEndpoints;
  services: ServicesEndpoints;
  
  constructor(baseURL?: string);
  
  request(endpoint: string, options?: RequestOptions): Promise<any>;
  refreshAccessToken(): Promise<boolean>;
  setTokens(accessToken: string, refreshToken: string): void;
  clearTokens(): void;
  isAuthenticated(): boolean;
  files(): FileUploadHelper;
}

export default ApiClient;
