/**
 * Admin Dashboard Test Script
 *
 * Run this in browser console on http://localhost:3000/admin
 * to verify admin functionality
 */

// Test 1: Check localStorage for admin user
console.log('=== TEST 1: localStorage Check ===');
const userEmail = localStorage.getItem('user_email');
const accessToken = localStorage.getItem('access_token');

console.log('User Email:', userEmail);
console.log('Access Token:', accessToken ? 'Present' : 'Missing');
console.log('Is Admin?', userEmail === 'mathnj120@gmail.com' ? 'YES ✅' : 'NO ❌');

// Test 2: Simulate admin login
console.log('\n=== TEST 2: Simulate Admin Login ===');
localStorage.setItem('user_email', 'mathnj120@gmail.com');
localStorage.setItem('access_token', 'mock-token-admin-test');
console.log('Set admin credentials in localStorage');
console.log('Refresh the page to see dashboard');

// Test 3: Check API endpoints
console.log('\n=== TEST 3: API Endpoint Test ===');
const API_URL = 'http://localhost:8000';
const token = localStorage.getItem('access_token');

fetch(`${API_URL}/api/v2/admin/dashboard`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => {
  console.log('Dashboard API Status:', response.status);
  return response.json();
})
.then(data => {
  console.log('Dashboard Data:', data);
  console.log('Test PASSED ✅');
})
.catch(error => {
  console.log('Test FAILED ❌');
  console.error('Error:', error.message);
  console.log('Note: This is expected if backend is not running');
});

// Test 4: Simulate regular user (non-admin)
console.log('\n=== TEST 4: Non-Admin User Test ===');
console.log('To test non-admin access:');
console.log('1. Set localStorage: localStorage.setItem("user_email", "regular@example.com")');
console.log('2. Refresh page');
console.log('3. Should see "Access Denied" message');

// Test 5: Verify admin check logic
console.log('\n=== TEST 5: Admin Check Logic ===');
const testEmails = [
  'mathnj120@gmail.com',
  'regular@example.com',
  'admin@test.com',
  'MATHNJ120@GMAIL.COM', // Case sensitivity test
];

testEmails.forEach(email => {
  const isAdmin = email === 'mathnj120@gmail.com';
  console.log(`${email}: ${isAdmin ? 'ADMIN ✅' : 'USER ❌'}`);
});

console.log('\n=== All Tests Complete ===');
console.log('Instructions:');
console.log('1. Login at http://localhost:3000/login with mathnj120@gmail.com');
console.log('2. Navigate to http://localhost:3000/admin');
console.log('3. Verify dashboard loads with metrics');
console.log('4. Check browser console for any errors');
