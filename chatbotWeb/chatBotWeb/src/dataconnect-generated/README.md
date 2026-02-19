# Generated TypeScript README
This README will guide you through the process of using the generated JavaScript SDK package for the connector `example`. It will also provide examples on how to use your generated SDK to call your Data Connect queries and mutations.

**If you're looking for the `React README`, you can find it at [`dataconnect-generated/react/README.md`](./react/README.md)**

***NOTE:** This README is generated alongside the generated SDK. If you make changes to this file, they will be overwritten when the SDK is regenerated.*

# Table of Contents
- [**Overview**](#generated-javascript-readme)
- [**Accessing the connector**](#accessing-the-connector)
  - [*Connecting to the local Emulator*](#connecting-to-the-local-emulator)
- [**Queries**](#queries)
  - [*ListAllCourses*](#listallcourses)
  - [*GetStudentProfile*](#getstudentprofile)
- [**Mutations**](#mutations)
  - [*EnrollStudentInCourse*](#enrollstudentincourse)
  - [*CreateNewProfessor*](#createnewprofessor)

# Accessing the connector
A connector is a collection of Queries and Mutations. One SDK is generated for each connector - this SDK is generated for the connector `example`. You can find more information about connectors in the [Data Connect documentation](https://firebase.google.com/docs/data-connect#how-does).

You can use this generated SDK by importing from the package `@dataconnect/generated` as shown below. Both CommonJS and ESM imports are supported.

You can also follow the instructions from the [Data Connect documentation](https://firebase.google.com/docs/data-connect/web-sdk#set-client).

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig } from '@dataconnect/generated';

const dataConnect = getDataConnect(connectorConfig);
```

## Connecting to the local Emulator
By default, the connector will connect to the production service.

To connect to the emulator, you can use the following code.
You can also follow the emulator instructions from the [Data Connect documentation](https://firebase.google.com/docs/data-connect/web-sdk#instrument-clients).

```typescript
import { connectDataConnectEmulator, getDataConnect } from 'firebase/data-connect';
import { connectorConfig } from '@dataconnect/generated';

const dataConnect = getDataConnect(connectorConfig);
connectDataConnectEmulator(dataConnect, 'localhost', 9399);
```

After it's initialized, you can call your Data Connect [queries](#queries) and [mutations](#mutations) from your generated SDK.

# Queries

There are two ways to execute a Data Connect Query using the generated Web SDK:
- Using a Query Reference function, which returns a `QueryRef`
  - The `QueryRef` can be used as an argument to `executeQuery()`, which will execute the Query and return a `QueryPromise`
- Using an action shortcut function, which returns a `QueryPromise`
  - Calling the action shortcut function will execute the Query and return a `QueryPromise`

The following is true for both the action shortcut function and the `QueryRef` function:
- The `QueryPromise` returned will resolve to the result of the Query once it has finished executing
- If the Query accepts arguments, both the action shortcut function and the `QueryRef` function accept a single argument: an object that contains all the required variables (and the optional variables) for the Query
- Both functions can be called with or without passing in a `DataConnect` instance as an argument. If no `DataConnect` argument is passed in, then the generated SDK will call `getDataConnect(connectorConfig)` behind the scenes for you.

Below are examples of how to use the `example` connector's generated functions to execute each query. You can also follow the examples from the [Data Connect documentation](https://firebase.google.com/docs/data-connect/web-sdk#using-queries).

## ListAllCourses
You can execute the `ListAllCourses` query using the following action shortcut function, or by calling `executeQuery()` after calling the following `QueryRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
listAllCourses(): QueryPromise<ListAllCoursesData, undefined>;

interface ListAllCoursesRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (): QueryRef<ListAllCoursesData, undefined>;
}
export const listAllCoursesRef: ListAllCoursesRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `QueryRef` function.
```typescript
listAllCourses(dc: DataConnect): QueryPromise<ListAllCoursesData, undefined>;

interface ListAllCoursesRef {
  ...
  (dc: DataConnect): QueryRef<ListAllCoursesData, undefined>;
}
export const listAllCoursesRef: ListAllCoursesRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the listAllCoursesRef:
```typescript
const name = listAllCoursesRef.operationName;
console.log(name);
```

### Variables
The `ListAllCourses` query has no variables.
### Return Type
Recall that executing the `ListAllCourses` query returns a `QueryPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `ListAllCoursesData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
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
```
### Using `ListAllCourses`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, listAllCourses } from '@dataconnect/generated';


// Call the `listAllCourses()` function to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await listAllCourses();

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await listAllCourses(dataConnect);

console.log(data.courses);

// Or, you can use the `Promise` API.
listAllCourses().then((response) => {
  const data = response.data;
  console.log(data.courses);
});
```

### Using `ListAllCourses`'s `QueryRef` function

```typescript
import { getDataConnect, executeQuery } from 'firebase/data-connect';
import { connectorConfig, listAllCoursesRef } from '@dataconnect/generated';


// Call the `listAllCoursesRef()` function to get a reference to the query.
const ref = listAllCoursesRef();

// You can also pass in a `DataConnect` instance to the `QueryRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = listAllCoursesRef(dataConnect);

// Call `executeQuery()` on the reference to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeQuery(ref);

console.log(data.courses);

// Or, you can use the `Promise` API.
executeQuery(ref).then((response) => {
  const data = response.data;
  console.log(data.courses);
});
```

## GetStudentProfile
You can execute the `GetStudentProfile` query using the following action shortcut function, or by calling `executeQuery()` after calling the following `QueryRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
getStudentProfile(vars: GetStudentProfileVariables): QueryPromise<GetStudentProfileData, GetStudentProfileVariables>;

interface GetStudentProfileRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: GetStudentProfileVariables): QueryRef<GetStudentProfileData, GetStudentProfileVariables>;
}
export const getStudentProfileRef: GetStudentProfileRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `QueryRef` function.
```typescript
getStudentProfile(dc: DataConnect, vars: GetStudentProfileVariables): QueryPromise<GetStudentProfileData, GetStudentProfileVariables>;

interface GetStudentProfileRef {
  ...
  (dc: DataConnect, vars: GetStudentProfileVariables): QueryRef<GetStudentProfileData, GetStudentProfileVariables>;
}
export const getStudentProfileRef: GetStudentProfileRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the getStudentProfileRef:
```typescript
const name = getStudentProfileRef.operationName;
console.log(name);
```

### Variables
The `GetStudentProfile` query requires an argument of type `GetStudentProfileVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface GetStudentProfileVariables {
  studentId: UUIDString;
}
```
### Return Type
Recall that executing the `GetStudentProfile` query returns a `QueryPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `GetStudentProfileData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
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
```
### Using `GetStudentProfile`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, getStudentProfile, GetStudentProfileVariables } from '@dataconnect/generated';

// The `GetStudentProfile` query requires an argument of type `GetStudentProfileVariables`:
const getStudentProfileVars: GetStudentProfileVariables = {
  studentId: ..., 
};

// Call the `getStudentProfile()` function to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await getStudentProfile(getStudentProfileVars);
// Variables can be defined inline as well.
const { data } = await getStudentProfile({ studentId: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await getStudentProfile(dataConnect, getStudentProfileVars);

console.log(data.student);

// Or, you can use the `Promise` API.
getStudentProfile(getStudentProfileVars).then((response) => {
  const data = response.data;
  console.log(data.student);
});
```

### Using `GetStudentProfile`'s `QueryRef` function

```typescript
import { getDataConnect, executeQuery } from 'firebase/data-connect';
import { connectorConfig, getStudentProfileRef, GetStudentProfileVariables } from '@dataconnect/generated';

// The `GetStudentProfile` query requires an argument of type `GetStudentProfileVariables`:
const getStudentProfileVars: GetStudentProfileVariables = {
  studentId: ..., 
};

// Call the `getStudentProfileRef()` function to get a reference to the query.
const ref = getStudentProfileRef(getStudentProfileVars);
// Variables can be defined inline as well.
const ref = getStudentProfileRef({ studentId: ..., });

// You can also pass in a `DataConnect` instance to the `QueryRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = getStudentProfileRef(dataConnect, getStudentProfileVars);

// Call `executeQuery()` on the reference to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeQuery(ref);

console.log(data.student);

// Or, you can use the `Promise` API.
executeQuery(ref).then((response) => {
  const data = response.data;
  console.log(data.student);
});
```

# Mutations

There are two ways to execute a Data Connect Mutation using the generated Web SDK:
- Using a Mutation Reference function, which returns a `MutationRef`
  - The `MutationRef` can be used as an argument to `executeMutation()`, which will execute the Mutation and return a `MutationPromise`
- Using an action shortcut function, which returns a `MutationPromise`
  - Calling the action shortcut function will execute the Mutation and return a `MutationPromise`

The following is true for both the action shortcut function and the `MutationRef` function:
- The `MutationPromise` returned will resolve to the result of the Mutation once it has finished executing
- If the Mutation accepts arguments, both the action shortcut function and the `MutationRef` function accept a single argument: an object that contains all the required variables (and the optional variables) for the Mutation
- Both functions can be called with or without passing in a `DataConnect` instance as an argument. If no `DataConnect` argument is passed in, then the generated SDK will call `getDataConnect(connectorConfig)` behind the scenes for you.

Below are examples of how to use the `example` connector's generated functions to execute each mutation. You can also follow the examples from the [Data Connect documentation](https://firebase.google.com/docs/data-connect/web-sdk#using-mutations).

## EnrollStudentInCourse
You can execute the `EnrollStudentInCourse` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
enrollStudentInCourse(vars: EnrollStudentInCourseVariables): MutationPromise<EnrollStudentInCourseData, EnrollStudentInCourseVariables>;

interface EnrollStudentInCourseRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: EnrollStudentInCourseVariables): MutationRef<EnrollStudentInCourseData, EnrollStudentInCourseVariables>;
}
export const enrollStudentInCourseRef: EnrollStudentInCourseRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
enrollStudentInCourse(dc: DataConnect, vars: EnrollStudentInCourseVariables): MutationPromise<EnrollStudentInCourseData, EnrollStudentInCourseVariables>;

interface EnrollStudentInCourseRef {
  ...
  (dc: DataConnect, vars: EnrollStudentInCourseVariables): MutationRef<EnrollStudentInCourseData, EnrollStudentInCourseVariables>;
}
export const enrollStudentInCourseRef: EnrollStudentInCourseRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the enrollStudentInCourseRef:
```typescript
const name = enrollStudentInCourseRef.operationName;
console.log(name);
```

### Variables
The `EnrollStudentInCourse` mutation requires an argument of type `EnrollStudentInCourseVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface EnrollStudentInCourseVariables {
  studentId: UUIDString;
  courseId: UUIDString;
  notes?: string | null;
}
```
### Return Type
Recall that executing the `EnrollStudentInCourse` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `EnrollStudentInCourseData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface EnrollStudentInCourseData {
  studentCourse_insert: StudentCourse_Key;
}
```
### Using `EnrollStudentInCourse`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, enrollStudentInCourse, EnrollStudentInCourseVariables } from '@dataconnect/generated';

// The `EnrollStudentInCourse` mutation requires an argument of type `EnrollStudentInCourseVariables`:
const enrollStudentInCourseVars: EnrollStudentInCourseVariables = {
  studentId: ..., 
  courseId: ..., 
  notes: ..., // optional
};

// Call the `enrollStudentInCourse()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await enrollStudentInCourse(enrollStudentInCourseVars);
// Variables can be defined inline as well.
const { data } = await enrollStudentInCourse({ studentId: ..., courseId: ..., notes: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await enrollStudentInCourse(dataConnect, enrollStudentInCourseVars);

console.log(data.studentCourse_insert);

// Or, you can use the `Promise` API.
enrollStudentInCourse(enrollStudentInCourseVars).then((response) => {
  const data = response.data;
  console.log(data.studentCourse_insert);
});
```

### Using `EnrollStudentInCourse`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, enrollStudentInCourseRef, EnrollStudentInCourseVariables } from '@dataconnect/generated';

// The `EnrollStudentInCourse` mutation requires an argument of type `EnrollStudentInCourseVariables`:
const enrollStudentInCourseVars: EnrollStudentInCourseVariables = {
  studentId: ..., 
  courseId: ..., 
  notes: ..., // optional
};

// Call the `enrollStudentInCourseRef()` function to get a reference to the mutation.
const ref = enrollStudentInCourseRef(enrollStudentInCourseVars);
// Variables can be defined inline as well.
const ref = enrollStudentInCourseRef({ studentId: ..., courseId: ..., notes: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = enrollStudentInCourseRef(dataConnect, enrollStudentInCourseVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.studentCourse_insert);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.studentCourse_insert);
});
```

## CreateNewProfessor
You can execute the `CreateNewProfessor` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
createNewProfessor(vars: CreateNewProfessorVariables): MutationPromise<CreateNewProfessorData, CreateNewProfessorVariables>;

interface CreateNewProfessorRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: CreateNewProfessorVariables): MutationRef<CreateNewProfessorData, CreateNewProfessorVariables>;
}
export const createNewProfessorRef: CreateNewProfessorRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
createNewProfessor(dc: DataConnect, vars: CreateNewProfessorVariables): MutationPromise<CreateNewProfessorData, CreateNewProfessorVariables>;

interface CreateNewProfessorRef {
  ...
  (dc: DataConnect, vars: CreateNewProfessorVariables): MutationRef<CreateNewProfessorData, CreateNewProfessorVariables>;
}
export const createNewProfessorRef: CreateNewProfessorRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the createNewProfessorRef:
```typescript
const name = createNewProfessorRef.operationName;
console.log(name);
```

### Variables
The `CreateNewProfessor` mutation requires an argument of type `CreateNewProfessorVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface CreateNewProfessorVariables {
  firstName: string;
  lastName: string;
  department: string;
  email?: string | null;
  officeHours?: string | null;
  researchInterests?: string[] | null;
}
```
### Return Type
Recall that executing the `CreateNewProfessor` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `CreateNewProfessorData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface CreateNewProfessorData {
  professor_insert: Professor_Key;
}
```
### Using `CreateNewProfessor`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, createNewProfessor, CreateNewProfessorVariables } from '@dataconnect/generated';

// The `CreateNewProfessor` mutation requires an argument of type `CreateNewProfessorVariables`:
const createNewProfessorVars: CreateNewProfessorVariables = {
  firstName: ..., 
  lastName: ..., 
  department: ..., 
  email: ..., // optional
  officeHours: ..., // optional
  researchInterests: ..., // optional
};

// Call the `createNewProfessor()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await createNewProfessor(createNewProfessorVars);
// Variables can be defined inline as well.
const { data } = await createNewProfessor({ firstName: ..., lastName: ..., department: ..., email: ..., officeHours: ..., researchInterests: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await createNewProfessor(dataConnect, createNewProfessorVars);

console.log(data.professor_insert);

// Or, you can use the `Promise` API.
createNewProfessor(createNewProfessorVars).then((response) => {
  const data = response.data;
  console.log(data.professor_insert);
});
```

### Using `CreateNewProfessor`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, createNewProfessorRef, CreateNewProfessorVariables } from '@dataconnect/generated';

// The `CreateNewProfessor` mutation requires an argument of type `CreateNewProfessorVariables`:
const createNewProfessorVars: CreateNewProfessorVariables = {
  firstName: ..., 
  lastName: ..., 
  department: ..., 
  email: ..., // optional
  officeHours: ..., // optional
  researchInterests: ..., // optional
};

// Call the `createNewProfessorRef()` function to get a reference to the mutation.
const ref = createNewProfessorRef(createNewProfessorVars);
// Variables can be defined inline as well.
const ref = createNewProfessorRef({ firstName: ..., lastName: ..., department: ..., email: ..., officeHours: ..., researchInterests: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = createNewProfessorRef(dataConnect, createNewProfessorVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.professor_insert);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.professor_insert);
});
```

