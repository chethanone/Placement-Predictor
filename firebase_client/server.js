const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { initializeApp } = require('firebase/app');
const { getFirestore, collection, addDoc, getDocs, doc, getDoc, updateDoc, query, where, orderBy } = require('firebase/firestore');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

// Firebase Configuration
const firebaseConfig = {
  apiKey: "AIzaSyA39-fAX2f7WFr_aF_PIKK4qBy4mSzSGrQ",
  authDomain: "placementpredictor-35d83.firebaseapp.com",
  projectId: "placementpredictor-35d83",
  storageBucket: "placementpredictor-35d83.firebasestorage.app",
  messagingSenderId: "707514061675",
  appId: "1:707514061675:web:3c54a58d494d600c5d722e"
};

// Initialize Firebase
const firebaseApp = initializeApp(firebaseConfig);
const db = getFirestore(firebaseApp);

console.log(' Firebase initialized!');

// ==================== API ENDPOINTS ====================

// Save student prediction to Firebase
app.post('/api/save-prediction', async (req, res) => {
  try {
    const predictionData = {
      ...req.body,
      timestamp: new Date().toISOString(),
      status: 'pending_verification'
    };
    
    const docRef = await addDoc(collection(db, 'predictions'), predictionData);
    
    res.json({
      success: true,
      message: 'Prediction saved to Firebase!',
      id: docRef.id
    });
  } catch (error) {
    console.error('Error saving prediction:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get all pending verifications (for teacher dashboard)
app.get('/api/pending-verifications', async (req, res) => {
  try {
    const q = query(
      collection(db, 'predictions'),
      where('status', '==', 'pending_verification'),
      orderBy('timestamp', 'desc')
    );
    
    const querySnapshot = await getDocs(q);
    const pending = [];
    
    querySnapshot.forEach((doc) => {
      pending.push({ id: doc.id, ...doc.data() });
    });
    
    res.json({
      success: true,
      count: pending.length,
      data: pending
    });
  } catch (error) {
    console.error('Error fetching pending:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get all students
app.get('/api/students', async (req, res) => {
  try {
    const querySnapshot = await getDocs(collection(db, 'predictions'));
    const students = [];
    
    querySnapshot.forEach((doc) => {
      students.push({ id: doc.id, ...doc.data() });
    });
    
    res.json({
      success: true,
      count: students.length,
      data: students
    });
  } catch (error) {
    console.error('Error fetching students:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get single student by ID
app.get('/api/student/:id', async (req, res) => {
  try {
    const docRef = doc(db, 'predictions', req.params.id);
    const docSnap = await getDoc(docRef);
    
    if (docSnap.exists()) {
      res.json({
        success: true,
        data: { id: docSnap.id, ...docSnap.data() }
      });
    } else {
      res.status(404).json({
        success: false,
        error: 'Student not found'
      });
    }
  } catch (error) {
    console.error('Error fetching student:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Verify student scores (teacher action)
app.post('/api/verify-scores/:id', async (req, res) => {
  try {
    const docRef = doc(db, 'predictions', req.params.id);
    
    const updateData = {
      ...req.body.verifiedData,
      status: 'verified',
      verifiedBy: req.body.teacherId || 'teacher',
      verifiedAt: new Date().toISOString()
    };
    
    await updateDoc(docRef, updateData);
    
    res.json({
      success: true,
      message: 'Scores verified successfully!'
    });
  } catch (error) {
    console.error('Error verifying scores:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get statistics for dashboard
app.get('/api/statistics', async (req, res) => {
  try {
    const querySnapshot = await getDocs(collection(db, 'predictions'));
    
    let total = 0;
    let pending = 0;
    let verified = 0;
    let totalProbability = 0;
    
    querySnapshot.forEach((doc) => {
      const data = doc.data();
      total++;
      if (data.status === 'pending_verification') pending++;
      if (data.status === 'verified') verified++;
      if (data.probability) totalProbability += data.probability;
    });
    
    res.json({
      success: true,
      statistics: {
        totalStudents: total,
        pendingVerifications: pending,
        verifiedStudents: verified,
        averageProbability: total > 0 ? (totalProbability / total).toFixed(2) : 0
      }
    });
  } catch (error) {
    console.error('Error fetching statistics:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', firebase: 'connected' });
});

// Start server
app.listen(PORT, () => {
  console.log(`\n Firebase API Server running on http://localhost:${PORT}`);
  console.log(` API Endpoints:`);
  console.log(` - POST /api/save-prediction`);
  console.log(` - GET /api/pending-verifications`);
  console.log(` - GET /api/students`);
  console.log(` - GET /api/student/:id`);
  console.log(` - POST /api/verify-scores/:id`);
  console.log(` - GET /api/statistics\n`);
});

module.exports = app;
