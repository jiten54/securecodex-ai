import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import AIAnalysis from './pages/AIAnalysis';
import APIKeys from './pages/APIKeys';
import Login from './pages/Login';

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = !!localStorage.getItem('token') || !!localStorage.getItem('apiKey');
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
  const isAuthenticated = !!localStorage.getItem('token') || !!localStorage.getItem('apiKey');

  return (
    <Router>
      <div className="min-h-screen bg-background text-foreground">
        {isAuthenticated && <Navbar />}
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/analysis"
            element={
              <PrivateRoute>
                <AIAnalysis />
              </PrivateRoute>
            }
          />
          <Route
            path="/keys"
            element={
              <PrivateRoute>
                <APIKeys />
              </PrivateRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
