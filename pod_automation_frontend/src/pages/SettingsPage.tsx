import React, { useState } from 'react';
import { UserCircleIcon, CreditCardIcon, PuzzlePieceIcon, BellIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

// Reusable Button component (assuming it exists or is defined elsewhere)
const Button: React.FC<{ children: React.ReactNode; variant?: 'primary' | 'secondary' | 'outline' | 'link' | 'icon'; className?: string; onClick?: () => void; title?: string }> = ({ children, variant = 'primary', className = '', onClick, title }) => {
  const baseStyle = 'px-3 py-1.5 rounded-md font-medium transition-colors inline-flex items-center justify-center text-sm';
  const primaryStyle = 'bg-primary text-dark-text hover:bg-primary-light';
  const secondaryStyle = 'bg-gray-200 text-light-text hover:bg-gray-300 dark:bg-dark-card dark:text-dark-text dark:hover:bg-dark-border';
  const outlineStyle = 'border border-gray-300 dark:border-dark-border text-light-text dark:text-dark-text hover:bg-gray-100 dark:hover:bg-dark-border';
  const linkStyle = 'text-primary hover:underline dark:text-primary-light p-0 text-sm';
  const iconStyle = 'p-1.5 text-light-text-secondary dark:text-dark-text-secondary hover:text-primary dark:hover:text-primary-light'; // Style for icon-only buttons

  let styles = `${baseStyle} ${className}`;
  if (variant === 'primary') styles += ` ${primaryStyle}`;
  else if (variant === 'secondary') styles += ` ${secondaryStyle}`;
  else if (variant === 'outline') styles += ` ${outlineStyle}`;
  else if (variant === 'link') styles += ` ${linkStyle}`;
  else if (variant === 'icon') styles = `${iconStyle} ${className}`; // Use specific style for icon buttons

  return <button onClick={onClick} className={styles} title={title}>{children}</button>;
};

// Reusable Input component (simple version)
const InputField: React.FC<{ id: string; label: string; type?: string; value: string; onChange: (e: React.ChangeEvent<HTMLInputElement>) => void; placeholder?: string; disabled?: boolean; className?: string }> = 
  ({ id, label, type = 'text', value, onChange, placeholder, disabled, className = '' }) => (
  <div className={className}>
    <label htmlFor={id} className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-1">{label}</label>
    <input
      type={type}
      id={id}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      className={`w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text ${disabled ? 'bg-gray-100 dark:bg-dark-border cursor-not-allowed' : ''}`}
    />
  </div>
);

// Reusable Checkbox component
const CheckboxField: React.FC<{ id: string; label: string; checked: boolean; onChange: (e: React.ChangeEvent<HTMLInputElement>) => void; className?: string }> = 
  ({ id, label, checked, onChange, className = '' }) => (
  <div className={`flex items-center ${className}`}>
    <input
      id={id}
      type="checkbox"
      checked={checked}
      onChange={onChange}
      className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:checked:bg-primary dark:focus:ring-offset-dark-bg"
    />
    <label htmlFor={id} className="ml-2 block text-sm text-light-text dark:text-dark-text">
      {label}
    </label>
  </div>
);


type Tab = 'profile' | 'billing' | 'integrations' | 'notifications';

const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('profile');

  // Placeholder state for form fields
  const [name, setName] = useState('User Name');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [notifWeekly, setNotifWeekly] = useState(true);
  const [notifFeatures, setNotifFeatures] = useState(true);
  const [notifBilling, setNotifBilling] = useState(true);
  const [notifDesign, setNotifDesign] = useState(true);
  const [notifPublish, setNotifPublish] = useState(true);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-light-text dark:text-dark-text">Account Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-end">
              <InputField id="name" label="Name" value={name} onChange={(e) => setName(e.target.value)} />
              <Button variant="primary" className="w-full md:w-auto">Save Name</Button>
            </div>
            <InputField id="email" label="Email" value="user@example.com" onChange={() => {}} disabled />
            
            <hr className="border-gray-200 dark:border-dark-border" />

            <h3 className="text-lg font-semibold text-light-text dark:text-dark-text">Change Password</h3>
            <div className="space-y-4 max-w-md">
              <InputField id="currentPassword" label="Current Password" type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} />
              <InputField id="newPassword" label="New Password" type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
              <InputField id="confirmPassword" label="Confirm New Password" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
              <Button variant="primary">Update Password</Button>
            </div>
          </div>
        );
      case 'billing':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-light-text dark:text-dark-text">Current Plan</h3>
            <div className="bg-gray-100 dark:bg-dark-card p-4 rounded-md flex justify-between items-center">
              <div>
                <p className="font-medium text-light-text dark:text-dark-text">Pro Plan ($29 / month)</p>
                <p className="text-sm text-light-text-secondary dark:text-dark-text-secondary">Next Billing Date: 2025-06-01</p>
              </div>
              <Button variant="outline">Change Plan</Button>
            </div>

            <h3 className="text-lg font-semibold text-light-text dark:text-dark-text">Payment Method</h3>
            <div className="bg-gray-100 dark:bg-dark-card p-4 rounded-md flex justify-between items-center">
              <p className="text-light-text dark:text-dark-text">Visa ending in 1234</p>
              <Button variant="outline">Update Method</Button>
            </div>

            <h3 className="text-lg font-semibold text-light-text dark:text-dark-text">Billing History</h3>
            {/* Placeholder Table */}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-dark-border">
                <thead className="bg-gray-50 dark:bg-dark-card">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase">Date</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase">Amount</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase">Status</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase">Invoice</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-dark-bg divide-y divide-gray-200 dark:divide-dark-border">
                  <tr>
                    <td className="px-4 py-2 text-sm">2025-05-01</td>
                    <td className="px-4 py-2 text-sm">$29.00</td>
                    <td className="px-4 py-2 text-sm"><span className="text-success">Paid</span></td>
                    <td className="px-4 py-2 text-sm"><Button variant="link">View</Button></td>
                  </tr>
                  {/* More rows... */}
                </tbody>
              </table>
            </div>
          </div>
        );
      case 'integrations':
        return (
          <div className="space-y-6">
            <div className="bg-gray-100 dark:bg-dark-card p-4 rounded-md flex justify-between items-center">
              <div>
                <p className="font-medium text-light-text dark:text-dark-text">Etsy</p>
                <p className="text-sm text-success flex items-center"><CheckCircleIcon className="h-4 w-4 mr-1"/> Connected (Shop: YourEtsyShop)</p>
              </div>
              <Button variant="outline" className="text-error border-error hover:bg-error hover:text-white">Disconnect</Button>
            </div>
            <div className="bg-gray-100 dark:bg-dark-card p-4 rounded-md flex justify-between items-center">
              <div>
                <p className="font-medium text-light-text dark:text-dark-text">Printify</p>
                <p className="text-sm text-success flex items-center"><CheckCircleIcon className="h-4 w-4 mr-1"/> Connected (API Key: ********)</p>
              </div>
              <div>
                <Button variant="outline" className="mr-2">Update Key</Button>
                <Button variant="outline" className="text-error border-error hover:bg-error hover:text-white">Disconnect</Button>
              </div>
            </div>
             <div className="bg-gray-100 dark:bg-dark-card p-4 rounded-md flex justify-between items-center">
              <div>
                <p className="font-medium text-light-text dark:text-dark-text">AI Provider (e.g., OpenAI)</p>
                {/* Example: Not Connected */}
                {/* <p className="text-sm text-light-text-secondary dark:text-dark-text-secondary flex items-center"><XCircleIcon className="h-4 w-4 mr-1 text-error"/> Not Connected</p> */}
                <p className="text-sm text-success flex items-center"><CheckCircleIcon className="h-4 w-4 mr-1"/> Active (API Key: ********)</p>
              </div>
              <Button variant="outline">Update Key</Button>
              {/* <Button variant="primary">Connect</Button> */}
            </div>
          </div>
        );
      case 'notifications':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-light-text dark:text-dark-text">Email Notifications</h3>
            <div className="space-y-2">
              <CheckboxField id="notifWeekly" label="Weekly Summary" checked={notifWeekly} onChange={(e) => setNotifWeekly(e.target.checked)} />
              <CheckboxField id="notifFeatures" label="New Feature Announcements" checked={notifFeatures} onChange={(e) => setNotifFeatures(e.target.checked)} />
              <CheckboxField id="notifBilling" label="Billing Updates" checked={notifBilling} onChange={(e) => setNotifBilling(e.target.checked)} />
            </div>

            <hr className="border-gray-200 dark:border-dark-border" />

            <h3 className="text-lg font-semibold text-light-text dark:text-dark-text">In-App Notifications</h3>
            <div className="space-y-2">
              <CheckboxField id="notifDesign" label="Design Generation Complete" checked={notifDesign} onChange={(e) => setNotifDesign(e.target.checked)} />
              <CheckboxField id="notifPublish" label="Publishing Success/Failure" checked={notifPublish} onChange={(e) => setNotifPublish(e.target.checked)} />
            </div>
            
            <Button variant="primary">Save Preferences</Button>
          </div>
        );
      default:
        return null;
    }
  };

  const tabs: { id: Tab; name: string; icon: React.ElementType }[] = [
    { id: 'profile', name: 'Profile', icon: UserCircleIcon },
    { id: 'billing', name: 'Billing', icon: CreditCardIcon },
    { id: 'integrations', name: 'Integrations', icon: PuzzlePieceIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-light-text dark:text-dark-text mb-6">Settings</h1>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200 dark:border-dark-border">
        <nav className="-mb-px flex space-x-6 overflow-x-auto" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm flex items-center ${activeTab === tab.id
                  ? 'border-primary text-primary dark:border-primary-light dark:text-primary-light'
                  : 'border-transparent text-light-text-secondary hover:text-gray-700 hover:border-gray-300 dark:text-dark-text-secondary dark:hover:text-gray-300 dark:hover:border-gray-700'
                }`}
            >
              <tab.icon className="-ml-0.5 mr-2 h-5 w-5" aria-hidden="true" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white dark:bg-dark-bg p-6 rounded-lg shadow">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default SettingsPage;

