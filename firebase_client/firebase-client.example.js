// Firebase Configuration and Initialization
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, addDoc, getDocs, doc, getDoc, updateDoc, query, where } from 'firebase/firestore';
import { getStorage, ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword } from 'firebase/auth';

// Your Firebase configuration
// COPY THIS FILE TO firebase-client.js AND ADD YOUR ACTUAL CREDENTIALS
const firebaseConfig = {
  apiKey: "YOUR_API_KEY_HERE",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.firebasestorage.app",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID",
  measurementId: "YOUR_MEASUREMENT_ID"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const storage = getStorage(app);
const auth = getAuth(app);

console.log(' Firebase initialized successfully!');

// ==================== STUDENT OPERATIONS ====================

export async function saveStudentPrediction(studentData) {
  try {
    const docRef = await addDoc(collection(db, 'predictions'), {
      ...studentData,
      timestamp: new Date().toISOString(),
      status: 'pending_verification'
    });
    console.log(' Prediction saved to Firebase:', docRef.id);
    return { success: true, id: docRef.id };
  } catch (error) {
    console.error(' Error saving prediction:', error);
    return { success: false, error: error.message };
  }
}

export async function saveStudentSkills(studentId, skillData) {
  try {
    const docRef = await addDoc(collection(db, 'student_skills'), {
      studentId,
      ...skillData,
      timestamp: new Date().toISOString(),
      verified: false
    });
    console.log(' Skills saved to Firebase:', docRef.id);
    return { success: true, id: docRef.id };
  } catch (error) {
    console.error(' Error saving skills:', error);
    return { success: false, error: error.message };
  }
}

export async function saveQuizResult(quizData) {
  try {
    const docRef = await addDoc(collection(db, 'quiz_results'), {
      ...quizData,
      timestamp: new Date().toISOString(),
      status: 'completed'
    });
    console.log(' Quiz result saved:', docRef.id);
    return { success: true, id: docRef.id };
  } catch (error) {
    console.error(' Error saving quiz:', error);
    return { success: false, error: error.message };
  }
}

// ==================== TEACHER OPERATIONS ====================

export async function getPendingVerifications() {
  try {
    const q = query(
      collection(db, 'predictions'),
      where('status', '==', 'pending_verification')
    );
    const querySnapshot = await getDocs(q);
    const pending = [];
    querySnapshot.forEach((doc) => {
      pending.push({ id: doc.id, ...doc.data() });
    });
    console.log(` Found ${pending.length} pending verifications`);
    return { success: true, data: pending };
  } catch (error) {
    console.error(' Error fetching pending:', error);
    return { success: false, error: error.message };
  }
}

export async function verifyStudentScores(predictionId, verifiedData, teacherId) {
  try {
    const docRef = doc(db, 'predictions', predictionId);
    await updateDoc(docRef, {
      ...verifiedData,
      status: 'verified',
      verifiedBy: teacherId,
      verifiedAt: new Date().toISOString()
    });
    console.log(' Scores verified:', predictionId);
    return { success: true };
  } catch (error) {
    console.error(' Error verifying:', error);
    return { success: false, error: error.message };
  }
}

export async function getAllStudents() {
  try {
    const querySnapshot = await getDocs(collection(db, 'predictions'));
    const students = [];
    querySnapshot.forEach((doc) => {
      students.push({ id: doc.id, ...doc.data() });
    });
    console.log(` Found ${students.length} students`);
    return { success: true, data: students };
  } catch (error) {
    console.error(' Error fetching students:', error);
    return { success: false, error: error.message };
  }
}

// ==================== FILE OPERATIONS ====================

export async function uploadSyllabus(file, studentId) {
  try {
    const timestamp = new Date().getTime();
    const fileName = `syllabus/${studentId}/${timestamp}_${file.name}`;
    const storageRef = ref(storage, fileName);
    
    await uploadBytes(storageRef, file);
    const downloadURL = await getDownloadURL(storageRef);
    
    console.log(' Syllabus uploaded:', downloadURL);
    return { success: true, url: downloadURL };
  } catch (error) {
    console.error(' Error uploading:', error);
    return { success: false, error: error.message };
  }
}

export { db, storage, auth };
