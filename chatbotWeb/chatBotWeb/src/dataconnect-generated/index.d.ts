import { ConnectorConfig, DataConnect, QueryRef, QueryPromise, MutationRef, MutationPromise } from 'firebase/data-connect';

export const connectorConfig: ConnectorConfig;

export type TimestampString = string;
export type UUIDString = string;
export type Int64String = string;
export type DateString = string;




export interface Course_Key {
  id: UUIDString;
  __typename?: 'Course_Key';
}

export interface CreateNewProfessorData {
  professor_insert: Professor_Key;
}

export interface CreateNewProfessorVariables {
  firstName: string;
  lastName: string;
  department: string;
  email?: string | null;
  officeHours?: string | null;
  researchInterests?: string[] | null;
}

export interface EnrollStudentInCourseData {
  studentCourse_insert: StudentCourse_Key;
}

export interface EnrollStudentInCourseVariables {
  studentId: UUIDString;
  courseId: UUIDString;
  notes?: string | null;
}

export interface GetStudentProfileData {
  student?: {
    id: UUIDString;
    displayName: string;
    email?: string | null;
    major?: string | null;
    year?: number | null;
    photoUrl?: string | null;
  } & Student_Key;
}

export interface GetStudentProfileVariables {
  studentId: UUIDString;
}

export interface ListAllCoursesData {
  courses: ({
    id: UUIDString;
    title: string;
    courseCode: string;
    units: number;
    quarterOffered?: string[] | null;
    geAreas?: string[] | null;
  } & Course_Key)[];
}

export interface Professor_Key {
  id: UUIDString;
  __typename?: 'Professor_Key';
}

export interface StudentCourse_Key {
  studentId: UUIDString;
  courseId: UUIDString;
  __typename?: 'StudentCourse_Key';
}

export interface StudentProfessor_Key {
  studentId: UUIDString;
  professorId: UUIDString;
  __typename?: 'StudentProfessor_Key';
}

export interface Student_Key {
  id: UUIDString;
  __typename?: 'Student_Key';
}

export interface Teaches_Key {
  professorId: UUIDString;
  courseId: UUIDString;
  quarter: string;
  year: number;
  __typename?: 'Teaches_Key';
}

interface ListAllCoursesRef {
  /* Allow users to create refs without passing in DataConnect */
  (): QueryRef<ListAllCoursesData, undefined>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect): QueryRef<ListAllCoursesData, undefined>;
  operationName: string;
}
export const listAllCoursesRef: ListAllCoursesRef;

export function listAllCourses(): QueryPromise<ListAllCoursesData, undefined>;
export function listAllCourses(dc: DataConnect): QueryPromise<ListAllCoursesData, undefined>;

interface GetStudentProfileRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: GetStudentProfileVariables): QueryRef<GetStudentProfileData, GetStudentProfileVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: GetStudentProfileVariables): QueryRef<GetStudentProfileData, GetStudentProfileVariables>;
  operationName: string;
}
export const getStudentProfileRef: GetStudentProfileRef;

export function getStudentProfile(vars: GetStudentProfileVariables): QueryPromise<GetStudentProfileData, GetStudentProfileVariables>;
export function getStudentProfile(dc: DataConnect, vars: GetStudentProfileVariables): QueryPromise<GetStudentProfileData, GetStudentProfileVariables>;

interface EnrollStudentInCourseRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: EnrollStudentInCourseVariables): MutationRef<EnrollStudentInCourseData, EnrollStudentInCourseVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: EnrollStudentInCourseVariables): MutationRef<EnrollStudentInCourseData, EnrollStudentInCourseVariables>;
  operationName: string;
}
export const enrollStudentInCourseRef: EnrollStudentInCourseRef;

export function enrollStudentInCourse(vars: EnrollStudentInCourseVariables): MutationPromise<EnrollStudentInCourseData, EnrollStudentInCourseVariables>;
export function enrollStudentInCourse(dc: DataConnect, vars: EnrollStudentInCourseVariables): MutationPromise<EnrollStudentInCourseData, EnrollStudentInCourseVariables>;

interface CreateNewProfessorRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: CreateNewProfessorVariables): MutationRef<CreateNewProfessorData, CreateNewProfessorVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: CreateNewProfessorVariables): MutationRef<CreateNewProfessorData, CreateNewProfessorVariables>;
  operationName: string;
}
export const createNewProfessorRef: CreateNewProfessorRef;

export function createNewProfessor(vars: CreateNewProfessorVariables): MutationPromise<CreateNewProfessorData, CreateNewProfessorVariables>;
export function createNewProfessor(dc: DataConnect, vars: CreateNewProfessorVariables): MutationPromise<CreateNewProfessorData, CreateNewProfessorVariables>;

