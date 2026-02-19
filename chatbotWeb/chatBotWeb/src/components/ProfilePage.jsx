import React, { useState } from 'react';
import './ProfilePage.css';

const ProfilePage = ({ onBack }) => {
    // Mock user data (will be replaced with OAuth later)
    const mockUser = {
        name: "UCSB Student",
        email: "student@ucsb.edu",
        picture: "https://ui-avatars.com/api/?name=UCSB+Student&background=003660&color=febc11&size=120",
        verified: true
    };

    const [editing, setEditing] = useState(false);
    const [formData, setFormData] = useState({
        name: mockUser.name,
        email: mockUser.email,
        bio: '',
        major: '',
        year: ''
    });
    const [saveStatus, setSaveStatus] = useState('');

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaveStatus('saving');

        try {
            // Simulate saving (replace with actual API call later)
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Store in localStorage for now
            localStorage.setItem('userProfile', JSON.stringify(formData));

            setEditing(false);
            setSaveStatus('saved');
            setTimeout(() => setSaveStatus(''), 3000);
        } catch (error) {
            console.error('Error updating profile:', error);
            setSaveStatus('error');
            setTimeout(() => setSaveStatus(''), 3000);
        }
    };

    const handleCancel = () => {
        setEditing(false);
        // Reload from localStorage if exists
        const saved = localStorage.getItem('userProfile');
        if (saved) {
            setFormData(JSON.parse(saved));
        } else {
            setFormData({
                name: mockUser.name,
                email: mockUser.email,
                bio: '',
                major: '',
                year: ''
            });
        }
    };

    // Load saved profile on mount
    React.useEffect(() => {
        const saved = localStorage.getItem('userProfile');
        if (saved) {
            setFormData(JSON.parse(saved));
        }
    }, []);

    return (
        <div className="profile-page">
            <div className="profile-container">
                {/* Header with Back Button */}
                <div className="profile-header">
                    <button onClick={onBack} className="back-button">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" />
                        </svg>
                        Back to Chat
                    </button>
                    <h1 className="profile-title">My Profile</h1>
                </div>

                {/* Profile Card */}
                <div className="profile-card">
                    {/* Banner Section */}
                    <div className="profile-banner">
                        <div className="profile-avatar-section">
                            <img
                                src={mockUser.picture}
                                alt={formData.name}
                                className="profile-avatar"
                            />
                            {mockUser.verified && (
                                <div className="verified-badge" title="UCSB Email Verified">
                                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                    </svg>
                                </div>
                            )}
                        </div>
                        <div className="profile-info">
                            <h2 className="profile-name">{formData.name}</h2>
                            <p className="profile-email">{formData.email}</p>
                        </div>
                    </div>

                    {/* Content Section */}
                    <div className="profile-content">
                        {saveStatus && (
                            <div className={`save-status ${saveStatus}`}>
                                {saveStatus === 'saving' && 'Saving changes...'}
                                {saveStatus === 'saved' && '✓ Changes saved successfully!'}
                                {saveStatus === 'error' && '✗ Failed to save changes'}
                            </div>
                        )}

                        {!editing ? (
                            // View Mode
                            <div className="profile-view">
                                <div className="profile-section">
                                    <h3 className="section-title">About</h3>
                                    <p className="section-content">
                                        {formData.bio || 'No bio added yet. Click "Edit Profile" to add information about yourself.'}
                                    </p>
                                </div>

                                <div className="profile-section">
                                    <h3 className="section-title">Academic Information</h3>
                                    <div className="info-grid">
                                        <div className="info-item">
                                            <span className="info-label">Major</span>
                                            <span className="info-value">{formData.major || 'Not specified'}</span>
                                        </div>
                                        <div className="info-item">
                                            <span className="info-label">Year</span>
                                            <span className="info-value">{formData.year || 'Not specified'}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="profile-section">
                                    <h3 className="section-title">Account Information</h3>
                                    <div className="info-grid">
                                        <div className="info-item">
                                            <span className="info-label">Account Type</span>
                                            <span className="info-value">UCSB Student</span>
                                        </div>
                                        <div className="info-item">
                                            <span className="info-label">Email Status</span>
                                            <span className="info-value">
                                                <span className="status-verified">✓ Verified</span>
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <div className="profile-actions">
                                    <button onClick={() => setEditing(true)} className="btn btn-primary">
                                        Edit Profile
                                    </button>
                                </div>
                            </div>
                        ) : (
                            // Edit Mode
                            <form onSubmit={handleSubmit} className="profile-edit">
                                <div className="form-section">
                                    <h3 className="section-title">Personal Information</h3>

                                    <div className="form-group">
                                        <label className="form-label">Display Name</label>
                                        <input
                                            type="text"
                                            name="name"
                                            value={formData.name}
                                            onChange={handleInputChange}
                                            className="form-input"
                                            placeholder="Enter your display name"
                                            required
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">Email</label>
                                        <input
                                            type="email"
                                            name="email"
                                            value={formData.email}
                                            className="form-input"
                                            disabled
                                            title="Email cannot be changed"
                                        />
                                        <small className="form-help">Email is linked to your UCSB account</small>
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">Bio</label>
                                        <textarea
                                            name="bio"
                                            value={formData.bio}
                                            onChange={handleInputChange}
                                            className="form-textarea"
                                            rows={4}
                                            placeholder="Tell us about yourself..."
                                        />
                                    </div>
                                </div>

                                <div className="form-section">
                                    <h3 className="section-title">Academic Information</h3>

                                    <div className="form-group">
                                        <label className="form-label">Major</label>
                                        <input
                                            type="text"
                                            name="major"
                                            value={formData.major}
                                            onChange={handleInputChange}
                                            className="form-input"
                                            placeholder="e.g., Computer Science"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">Year</label>
                                        <select
                                            name="year"
                                            value={formData.year}
                                            onChange={handleInputChange}
                                            className="form-select"
                                        >
                                            <option value="">Select year</option>
                                            <option value="Freshman">Freshman</option>
                                            <option value="Sophomore">Sophomore</option>
                                            <option value="Junior">Junior</option>
                                            <option value="Senior">Senior</option>
                                            <option value="Graduate">Graduate</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="form-actions">
                                    <button type="submit" className="btn btn-primary" disabled={saveStatus === 'saving'}>
                                        {saveStatus === 'saving' ? 'Saving...' : 'Save Changes'}
                                    </button>
                                    <button type="button" onClick={handleCancel} className="btn btn-secondary">
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProfilePage;