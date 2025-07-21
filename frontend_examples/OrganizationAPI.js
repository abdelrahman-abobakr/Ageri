/**
 * Frontend Examples: How to Get Organization Vision and Message
 * 
 * Your API endpoint: http://localhost:8000/api/organization/settings/
 * This endpoint is PUBLIC - no authentication required for reading
 */

// Method 1: Simple Fetch API
export const getOrganizationSettings = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/organization/settings/');
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching organization settings:', error);
    return null;
  }
};

// Method 2: Using Axios (if you prefer)
import axios from 'axios';

export const getOrganizationSettingsAxios = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/organization/settings/');
    return response.data;
  } catch (error) {
    console.error('Error fetching organization settings:', error);
    return null;
  }
};

// Method 3: React Hook for Organization Settings
import { useState, useEffect } from 'react';

export const useOrganizationSettings = () => {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        const data = await getOrganizationSettings();
        setSettings(data);
        setError(null);
      } catch (err) {
        setError(err.message);
        setSettings(null);
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, []);

  return { settings, loading, error };
};

// Method 4: React Component Example
import React from 'react';

const OrganizationInfo = () => {
  const { settings, loading, error } = useOrganizationSettings();

  if (loading) return <div>Loading organization info...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!settings) return <div>No organization data available</div>;

  return (
    <div className="organization-info">
      <div className="org-header">
        {settings.logo && (
          <img 
            src={settings.logo} 
            alt="Organization Logo" 
            className="org-logo"
          />
        )}
        <h1>{settings.name}</h1>
      </div>
      
      {settings.vision && (
        <div className="org-vision">
          <h3>Our Vision</h3>
          <p>{settings.vision}</p>
        </div>
      )}
      
      {settings.mission && (
        <div className="org-mission">
          <h3>Our Mission</h3>
          <p>{settings.mission}</p>
        </div>
      )}
      
      {settings.about && (
        <div className="org-about">
          <h3>About Us</h3>
          <p>{settings.about}</p>
        </div>
      )}
      
      <div className="org-contact">
        {settings.email && <p>Email: {settings.email}</p>}
        {settings.phone && <p>Phone: {settings.phone}</p>}
        {settings.address && <p>Address: {settings.address}</p>}
      </div>
      
      <div className="org-social">
        {settings.website && (
          <a href={settings.website} target="_blank" rel="noopener noreferrer">
            Website
          </a>
        )}
        {settings.facebook && (
          <a href={settings.facebook} target="_blank" rel="noopener noreferrer">
            Facebook
          </a>
        )}
        {settings.twitter && (
          <a href={settings.twitter} target="_blank" rel="noopener noreferrer">
            Twitter
          </a>
        )}
      </div>
    </div>
  );
};

export default OrganizationInfo;

// Method 5: Context Provider for Global Access
import React, { createContext, useContext } from 'react';

const OrganizationContext = createContext();

export const OrganizationProvider = ({ children }) => {
  const { settings, loading, error } = useOrganizationSettings();

  return (
    <OrganizationContext.Provider value={{ settings, loading, error }}>
      {children}
    </OrganizationContext.Provider>
  );
};

export const useOrganization = () => {
  const context = useContext(OrganizationContext);
  if (!context) {
    throw new Error('useOrganization must be used within OrganizationProvider');
  }
  return context;
};

// Method 6: Header Component with Organization Info
const Header = () => {
  const { settings } = useOrganization();

  return (
    <header className="site-header">
      <div className="container">
        <div className="header-content">
          {settings?.logo && (
            <img src={settings.logo} alt="Logo" className="header-logo" />
          )}
          <div className="header-text">
            <h1>{settings?.name || 'Research Platform'}</h1>
            {settings?.vision && (
              <p className="header-tagline">{settings.vision}</p>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

// Method 7: Homepage Hero Section
const HeroSection = () => {
  const { settings } = useOrganization();

  return (
    <section className="hero">
      {settings?.banner && (
        <div 
          className="hero-background"
          style={{ backgroundImage: `url(${settings.banner})` }}
        />
      )}
      <div className="hero-content">
        <h1>{settings?.name}</h1>
        {settings?.vision && (
          <h2 className="hero-subtitle">{settings.vision}</h2>
        )}
        {settings?.mission && (
          <p className="hero-description">{settings.mission}</p>
        )}
        <div className="hero-actions">
          <button className="btn btn-primary">Get Started</button>
          <button className="btn btn-secondary">Learn More</button>
        </div>
      </div>
    </section>
  );
};

// Method 8: About Page Component
const AboutPage = () => {
  const { settings, loading } = useOrganization();

  if (loading) return <div>Loading...</div>;

  return (
    <div className="about-page">
      <div className="container">
        <div className="row">
          <div className="col-md-8">
            <h1>About {settings?.name}</h1>
            
            {settings?.about && (
              <div className="about-description">
                <p>{settings.about}</p>
              </div>
            )}
            
            <div className="vision-mission">
              {settings?.vision && (
                <div className="vision-section">
                  <h3>Our Vision</h3>
                  <p>{settings.vision}</p>
                </div>
              )}
              
              {settings?.mission && (
                <div className="mission-section">
                  <h3>Our Mission</h3>
                  <p>{settings.mission}</p>
                </div>
              )}
            </div>
          </div>
          
          <div className="col-md-4">
            {settings?.logo && (
              <img 
                src={settings.logo} 
                alt="Organization Logo" 
                className="img-fluid"
              />
            )}
            
            <div className="contact-info">
              <h4>Contact Information</h4>
              {settings?.email && <p>Email: {settings.email}</p>}
              {settings?.phone && <p>Phone: {settings.phone}</p>}
              {settings?.address && <p>Address: {settings.address}</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export { OrganizationInfo, Header, HeroSection, AboutPage };
