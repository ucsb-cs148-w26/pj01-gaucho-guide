import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './ProfilePage.css';

const ProfilePage = ({ onBack }) => {
    const { user, signOut } = useAuth();

    const [editing, setEditing] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        bio: '',
        major: '',
        year: ''
    });
    const [saveStatus, setSaveStatus] = useState('');

    // Load real user data + any saved extras on mount / when user changes
    useEffect(() => {
        if (!user) return;

        const saved = localStorage.getItem(`userProfile_${user.email}`);
        const extras = saved ? JSON.parse(saved) : {};

        setFormData({
            name: user.name || '',
            email: user.email || '',
            bio: extras.bio || '',
            major: extras.major || '',
            year: extras.year || '',
        });
    }, [user]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaveStatus('saving');
        try {
            await new Promise(resolve => setTimeout(resolve, 600));
            // Save only the editable extras keyed by email so different users don't share data
            const extras = { bio: formData.bio, major: formData.major, year: formData.year };
            localStorage.setItem(`userProfile_${user.email}`, JSON.stringify(extras));
            setEditing(false);
            setSaveStatus('saved');
            setTimeout(() => setSaveStatus(''), 3000);
        } catch {
            setSaveStatus('error');
            setTimeout(() => setSaveStatus(''), 3000);
        }
    };

    const handleCancel = () => {
        setEditing(false);
        if (!user) return;
        const saved = localStorage.getItem(`userProfile_${user.email}`);
        const extras = saved ? JSON.parse(saved) : {};
        setFormData({
            name: user.name || '',
            email: user.email || '',
            bio: extras.bio || '',
            major: extras.major || '',
            year: extras.year || '',
        });
    };

    const handleSignOut = async () => {
        await signOut();
    };

    if (!user) {
        return (
            <div className="profile-page">
                <div className="profile-container">
                    <p>You are not signed in.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="profile-page">
            <div className="profile-container">
                {/* Header */}
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
                    {/* Banner */}
                    <div className="profile-banner">
                        <div className="profile-avatar-section">
                            <img
                                src={user.picture}
                                alt={formData.name}
                                className="profile-avatar"
                            />
                            {user.verified && (
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

                    {/* Content */}
                    <div className="profile-content">
                        {saveStatus && (
                            <div className={`save-status ${saveStatus}`}>
                                {saveStatus === 'saving' && 'Saving changes...'}
                                {saveStatus === 'saved' && '✓ Changes saved successfully!'}
                                {saveStatus === 'error' && '✗ Failed to save changes'}
                            </div>
                        )}

                        {!editing ? (
                            <div className="profile-view">
                                {/* About */}
                                <div className="profile-section">
                                    <h3 className="section-title">About</h3>
                                    <p className="section-content">
                                        {formData.bio || 'No bio added yet. Click "Edit Profile" to add information about yourself.'}
                                    </p>
                                </div>

                                {/* Academic Info */}
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

                                {/* Account Info */}
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

                                {/* ── Classes Section (placeholder) ── */}
                                <div className="profile-section">
                                    <h3 className="section-title">My Classes</h3>
                                    <div className="classes-placeholder">
                                        <div className="classes-empty-icon">
                                            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                                                <path d="M12 14l9-5-9-5-9 5 9 5z" />
                                                <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                                            </svg>
                                        </div>
                                        <p className="classes-empty-title">No classes added yet</p>
                                        <p className="classes-empty-sub">
                                            Your enrolled and planned courses will appear here once this feature is available.
                                        </p>
                                        <button className="btn btn-outline" disabled>
                                            Coming Soon
                                        </button>
                                    </div>
                                </div>

                                <div className="profile-actions">
                                    <button onClick={() => setEditing(true)} className="btn btn-primary">
                                        Edit Profile
                                    </button>
                                    <button onClick={handleSignOut} className="btn btn-danger">
                                        Sign Out
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <form onSubmit={handleSubmit} className="profile-edit">
                                <div className="form-section">
                                    <h3 className="section-title">Personal Information</h3>

                                    <div className="form-group">
                                        <label className="form-label">Display Name</label>
                                        <input
                                            type="text"
                                            name="name"
                                            value={formData.name}
                                            className="form-input"
                                            disabled
                                            title="Name is linked to your account"
                                        />
                                        <small className="form-help">Name is linked to your UCSB account</small>
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