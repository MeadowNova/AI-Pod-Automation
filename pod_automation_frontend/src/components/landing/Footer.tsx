import React from 'react';
import { Link } from 'react-router-dom';

// Placeholder for social icons - could use a library like react-icons
const SocialIcon: React.FC<{ name: string }> = ({ name }) => {
  return <span className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">[{name}]</span>;
};

const Footer: React.FC = () => {
  const footerLinks = {
    Company: [
      { name: 'About', href: '/about' },
      { name: 'Blog', href: '/blog' },
      { name: 'Contact', href: '/contact' },
      { name: 'Affiliates', href: '/affiliates' },
    ],
    Features: [
      { name: 'Trends', href: '/features/trends' },
      { name: 'AI Studio', href: '/features/ai-studio' },
      { name: 'Mockups', href: '/features/mockups' },
      { name: 'Publishing', href: '/features/publishing' },
    ],
    Resources: [
      { name: 'Help Center', href: '/help' },
      { name: 'Pricing', href: '/pricing' },
      { name: 'Status', href: '/status' },
    ],
    Legal: [
      { name: 'Privacy Policy', href: '/privacy' },
      { name: 'Terms of Service', href: '/terms' },
    ],
  };

  return (
    <footer className="bg-gray-100 dark:bg-dark-bg border-t border-gray-200 dark:border-dark-border py-12 px-6">
      <div className="container mx-auto grid grid-cols-2 md:grid-cols-5 gap-8 mb-8">
        {/* Logo Column */}
        <div className="col-span-2 md:col-span-1">
          <div className="text-xl font-bold text-primary mb-4">POD Co-Pilot</div>
          {/* Optional: Short description */}
        </div>

        {/* Link Columns */}
        {Object.entries(footerLinks).map(([title, links]) => (
          <div key={title}>
            <h4 className="font-semibold text-light-text dark:text-dark-text mb-3 uppercase text-sm tracking-wider">{title}</h4>
            <ul className="space-y-2">
              {links.map((link) => (
                <li key={link.name}>
                  <Link to={link.href} className="text-light-text-secondary dark:text-dark-text-secondary hover:text-primary dark:hover:text-primary-light text-sm">
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="container mx-auto flex flex-col md:flex-row justify-between items-center border-t border-gray-200 dark:border-dark-border pt-8">
        <p className="text-sm text-light-text-secondary dark:text-dark-text-secondary mb-4 md:mb-0">
          &copy; {new Date().getFullYear()} POD Automation System. All rights reserved.
        </p>
        <div className="flex space-x-4">
          <SocialIcon name="Twitter" />
          <SocialIcon name="Facebook" />
          <SocialIcon name="LinkedIn" />
        </div>
      </div>
    </footer>
  );
};

export default Footer;

