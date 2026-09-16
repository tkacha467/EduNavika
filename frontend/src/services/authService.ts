// Authentication and User Session Service

import { api } from './api';
import { User, Role } from '../types';

const STORAGE_KEY_USER = 'edunavika_user';
const STORAGE_KEY_ROLE = 'edunavika_role';

export const DEFAULT_STUDENT: User = {
  id: 'stu-aarav-sharma-001',
  email: 'a.sharma@dps.edu.in',
  full_name: 'Aarav Sharma',
  name: 'Aarav Sharma',
  role: 'student',
  is_active: true,
  initials: 'AS',
  grade: 'Grade 10',
  section: 'Science',
  school: 'Delhi Public School, Bangalore',
  roll: 'STU-2026-0142',
  joined: 'June 2024',
  streak: 7,
  weeklyGoal: 85,
  todayGoal: 3,
};

export const DEFAULT_TEACHER: User = {
  id: 'tch-priya-nair-001',
  email: 'p.nair@dps.edu.in',
  full_name: 'Ms. Priya Nair',
  name: 'Ms. Priya Nair',
  role: 'teacher',
  is_active: true,
  initials: 'PN',
  grade: 'Grade 10',
  section: 'Science',
  school: 'Delhi Public School, Bangalore',
  subjects: 'Mathematics & Physics',
};

export class AuthService {
  private currentUser: User | null = null;
  private currentRole: Role = 'student';

  constructor() {
    this.loadSession();
  }

  private loadSession() {
    if (typeof localStorage === 'undefined') return;
    const savedUser = localStorage.getItem(STORAGE_KEY_USER);
    const savedRole = localStorage.getItem(STORAGE_KEY_ROLE) as Role | null;

    if (savedUser) {
      try {
        this.currentUser = JSON.parse(savedUser);
      } catch {
        this.currentUser = null;
      }
    }
    if (savedRole && (savedRole === 'student' || savedRole === 'teacher')) {
      this.currentRole = savedRole;
    }
  }

  public setRole(role: Role) {
    this.currentRole = role;
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(STORAGE_KEY_ROLE, role);
    }
  }

  public getRole(): Role {
    return this.currentRole;
  }

  public getUser(): User | null {
    return this.currentUser;
  }

  public isAuthenticated(): boolean {
    return this.currentUser !== null;
  }

  public async login(email: string, role: Role): Promise<User> {
    this.currentRole = role;
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(STORAGE_KEY_ROLE, role);
    }

    // If backend has user endpoint, attempt lookup or fallback gracefully
    try {
      // Look up user by email or ID if available
      const backendUser = await api.get<User>(`/users/${encodeURIComponent(email)}`);
      if (backendUser && backendUser.id) {
        this.currentUser = {
          ...backendUser,
          role,
          initials: backendUser.full_name
            ? backendUser.full_name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
            : 'U',
        };
        if (typeof localStorage !== 'undefined') {
          localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(this.currentUser));
        }
        return this.currentUser;
      }
    } catch {
      // Graceful fallback to approved role default
    }

    // Default profile matching approved design specifications
    const fallbackUser = role === 'student' ? { ...DEFAULT_STUDENT, email } : { ...DEFAULT_TEACHER, email };
    this.currentUser = fallbackUser;
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(this.currentUser));
    }
    return this.currentUser;
  }

  public logout() {
    this.currentUser = null;
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem(STORAGE_KEY_USER);
    }
  }
}

export const authService = new AuthService();

export const STUDENT = DEFAULT_STUDENT;
export const TEACHER = DEFAULT_TEACHER;

export function getCurrentUser(): User {
  return authService.getUser() || (authService.getRole() === 'teacher' ? DEFAULT_TEACHER : DEFAULT_STUDENT);
}

export function isAuthenticated(): boolean {
  return authService.isAuthenticated();
}

export function getRole(): Role {
  return authService.getRole();
}
