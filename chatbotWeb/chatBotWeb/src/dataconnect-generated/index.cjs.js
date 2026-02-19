const { queryRef, executeQuery, mutationRef, executeMutation, validateArgs } = require('firebase/data-connect');

const connectorConfig = {
  connector: 'example',
  service: 'pj01-gaucho-guide',
  location: 'us-east4'
};
exports.connectorConfig = connectorConfig;

const listAllCoursesRef = (dc) => {
  const { dc: dcInstance} = validateArgs(connectorConfig, dc, undefined);
  dcInstance._useGeneratedSdk();
  return queryRef(dcInstance, 'ListAllCourses');
}
listAllCoursesRef.operationName = 'ListAllCourses';
exports.listAllCoursesRef = listAllCoursesRef;

exports.listAllCourses = function listAllCourses(dc) {
  return executeQuery(listAllCoursesRef(dc));
};

const getStudentProfileRef = (dcOrVars, vars) => {
  const { dc: dcInstance, vars: inputVars} = validateArgs(connectorConfig, dcOrVars, vars, true);
  dcInstance._useGeneratedSdk();
  return queryRef(dcInstance, 'GetStudentProfile', inputVars);
}
getStudentProfileRef.operationName = 'GetStudentProfile';
exports.getStudentProfileRef = getStudentProfileRef;

exports.getStudentProfile = function getStudentProfile(dcOrVars, vars) {
  return executeQuery(getStudentProfileRef(dcOrVars, vars));
};

const enrollStudentInCourseRef = (dcOrVars, vars) => {
  const { dc: dcInstance, vars: inputVars} = validateArgs(connectorConfig, dcOrVars, vars, true);
  dcInstance._useGeneratedSdk();
  return mutationRef(dcInstance, 'EnrollStudentInCourse', inputVars);
}
enrollStudentInCourseRef.operationName = 'EnrollStudentInCourse';
exports.enrollStudentInCourseRef = enrollStudentInCourseRef;

exports.enrollStudentInCourse = function enrollStudentInCourse(dcOrVars, vars) {
  return executeMutation(enrollStudentInCourseRef(dcOrVars, vars));
};

const createNewProfessorRef = (dcOrVars, vars) => {
  const { dc: dcInstance, vars: inputVars} = validateArgs(connectorConfig, dcOrVars, vars, true);
  dcInstance._useGeneratedSdk();
  return mutationRef(dcInstance, 'CreateNewProfessor', inputVars);
}
createNewProfessorRef.operationName = 'CreateNewProfessor';
exports.createNewProfessorRef = createNewProfessorRef;

exports.createNewProfessor = function createNewProfessor(dcOrVars, vars) {
  return executeMutation(createNewProfessorRef(dcOrVars, vars));
};
