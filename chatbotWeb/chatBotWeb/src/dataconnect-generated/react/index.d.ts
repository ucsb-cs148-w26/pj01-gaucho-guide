import { ListAllCoursesData, GetStudentProfileData, GetStudentProfileVariables, EnrollStudentInCourseData, EnrollStudentInCourseVariables, CreateNewProfessorData, CreateNewProfessorVariables } from '../';
import { UseDataConnectQueryResult, useDataConnectQueryOptions, UseDataConnectMutationResult, useDataConnectMutationOptions} from '@tanstack-query-firebase/react/data-connect';
import { UseQueryResult, UseMutationResult} from '@tanstack/react-query';
import { DataConnect } from 'firebase/data-connect';
import { FirebaseError } from 'firebase/app';


export function useListAllCourses(options?: useDataConnectQueryOptions<ListAllCoursesData>): UseDataConnectQueryResult<ListAllCoursesData, undefined>;
export function useListAllCourses(dc: DataConnect, options?: useDataConnectQueryOptions<ListAllCoursesData>): UseDataConnectQueryResult<ListAllCoursesData, undefined>;

export function useGetStudentProfile(vars: GetStudentProfileVariables, options?: useDataConnectQueryOptions<GetStudentProfileData>): UseDataConnectQueryResult<GetStudentProfileData, GetStudentProfileVariables>;
export function useGetStudentProfile(dc: DataConnect, vars: GetStudentProfileVariables, options?: useDataConnectQueryOptions<GetStudentProfileData>): UseDataConnectQueryResult<GetStudentProfileData, GetStudentProfileVariables>;

export function useEnrollStudentInCourse(options?: useDataConnectMutationOptions<EnrollStudentInCourseData, FirebaseError, EnrollStudentInCourseVariables>): UseDataConnectMutationResult<EnrollStudentInCourseData, EnrollStudentInCourseVariables>;
export function useEnrollStudentInCourse(dc: DataConnect, options?: useDataConnectMutationOptions<EnrollStudentInCourseData, FirebaseError, EnrollStudentInCourseVariables>): UseDataConnectMutationResult<EnrollStudentInCourseData, EnrollStudentInCourseVariables>;

export function useCreateNewProfessor(options?: useDataConnectMutationOptions<CreateNewProfessorData, FirebaseError, CreateNewProfessorVariables>): UseDataConnectMutationResult<CreateNewProfessorData, CreateNewProfessorVariables>;
export function useCreateNewProfessor(dc: DataConnect, options?: useDataConnectMutationOptions<CreateNewProfessorData, FirebaseError, CreateNewProfessorVariables>): UseDataConnectMutationResult<CreateNewProfessorData, CreateNewProfessorVariables>;
