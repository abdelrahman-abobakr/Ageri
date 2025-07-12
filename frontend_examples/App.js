/**
 * App.js - Main Application with Organization Settings Integration
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { OrganizationProvider } from './OrganizationAPI';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';
import './App.css';

function App() {
  return (
    <OrganizationProvider>
      <Router>
        <div className="App">
          <Header />
          <main>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/contact" element={<ContactPage />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </OrganizationProvider>
  );
}

// Footer component using organization settings
const Footer = () => {
  const { settings } = useOrganization();

  return (
    <footer className="site-footer">
      <div className="container">
        <div className="row">
          <div className="col-md-6">
            <h5>{settings?.name}</h5>
            {settings?.about && (
              <p className="footer-description">
                {settings.about.substring(0, 150)}...
              </p>
            )}
          </div>
          <div className="col-md-3">
            <h6>Contact</h6>
            {settings?.email && <p>Email: {settings.email}</p>}
            {settings?.phone && <p>Phone: {settings.phone}</p>}
          </div>
          <div className="col-md-3">
            <h6>Follow Us</h6>
            <div className="social-links">
              {settings?.facebook && (
                <a href={settings.facebook} target="_blank" rel="noopener noreferrer">
                  Facebook
                </a>
              )}
              {settings?.twitter && (
                <a href={settings.twitter} target="_blank" rel="noopener noreferrer">
                  Twitter
                </a>
              )}
              {settings?.linkedin && (
                <a href={settings.linkedin} target="_blank" rel="noopener noreferrer">
                  LinkedIn
                </a>
              )}
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2024 {settings?.name}. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default App;
