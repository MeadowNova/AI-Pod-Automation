import { Link } from 'react-router-dom';
import { ChevronDownIcon } from '@heroicons/react/24/solid';
import HowItWorksSection from '../components/landing/HowItWorksSection';
import FeatureSection from '../components/landing/FeatureSection';
import TestimonialsSection from '../components/landing/TestimonialsSection';
import PricingSnippetSection from '../components/landing/PricingSnippetSection';
import FinalCTASection from '../components/landing/FinalCTASection';
import Footer from '../components/landing/Footer';
import Button from '../components/Button';
import { ThemeProvider } from '../contexts/ThemeContext';

// Dropdown Menu Component
interface DropdownMenuProps {
  label: string;
}

const DropdownMenu = ({ label }: DropdownMenuProps) => {
  return (
    <button className="flex items-center space-x-1 hover:text-primary dark:hover:text-primary-light">
      <span>{label}</span>
      <ChevronDownIcon className="h-4 w-4" />
    </button>
  );
};

const LandingPageHeader = () => {
  return (
    <header className="sticky top-0 z-50 bg-white dark:bg-dark-bg shadow-md">
      <nav className="container mx-auto px-6 py-3 flex justify-between items-center">
        <div className="text-xl font-bold text-primary dark:text-primary-light">POD Co-Pilot</div>
        <div className="hidden md:flex items-center space-x-6">
          <DropdownMenu label="Features" />
          <DropdownMenu label="Resources" />
          <Link to="/pricing" className="hover:text-primary dark:hover:text-primary-light">Pricing</Link>
        </div>
        <div className="hidden md:flex items-center space-x-4">
          <Button variant="link" to="/login">Sign In</Button>
          <Button variant="primary" to="/signup">Start Free Trial</Button>
        </div>
        {/* TODO: Add Mobile Menu Button */}
      </nav>
    </header>
  );
};

const HeroSection = () => {
  return (
    <section className="bg-gradient-to-b from-white to-light-bg dark:from-dark-bg dark:to-dark-card py-20 px-6 text-center">
      <div className="container mx-auto">
        {/* Placeholder for compelling visual/animation */}
        <div className="h-64 w-full bg-gray-300 dark:bg-dark-border rounded-lg mb-8 flex items-center justify-center">
          <span className="text-gray-500 dark:text-dark-text-secondary">[Compelling Visual/Animation Placeholder]</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-light-text dark:text-dark-text mb-4">
          Your AI Co-Pilot for Effortless Etsy POD Success
        </h1>
        <p className="text-lg text-light-text-secondary dark:text-dark-text-secondary mb-8 max-w-2xl mx-auto">
          Leverage AI to find trends, generate unique designs, and automate your POD shop
        </p>
        <Button variant="primary" className="text-lg" to="/signup">Start Free Trial</Button>
        <div className="mt-10 text-sm text-light-text-secondary dark:text-dark-text-secondary">
          Trusted by 1000+ Etsy Sellers {/* Placeholder logos */}
          <span className="inline-block mx-2 font-semibold">Etsy</span>
          <span className="inline-block mx-2 font-semibold">Printify</span>
        </div>
      </div>
    </section>
  );
};

// Placeholder Mockup Content Components
const TrendMockup = () => <div className="text-sm text-center">[Mockup: Trend Graph/Keyword List Interface]</div>;
const AIStudioMockup = () => <div className="text-sm text-center">[Mockup: AI Design Studio Interface]</div>;
const AutoMockupMockup = () => <div className="text-sm text-center">[Mockup: Design applied to T-Shirt, Mug, etc.]</div>;
const PublishingMockup = () => <div className="text-sm text-center">[Mockup: Listing Editor w/ SEO Score]</div>;


const LandingPage = () => {
  return (
    <ThemeProvider>
      <div className="bg-white dark:bg-dark-bg min-h-screen text-light-text dark:text-dark-text">
        <LandingPageHeader />
        <HeroSection />
        <HowItWorksSection />

        <FeatureSection
          title="Spot Winning Trends Before They Peak"
          description="Let our AI analyze Etsy market data to uncover high-demand, low-competition niches and keywords. Stay ahead of the curve."
          mockupContent={<TrendMockup />}
          textPosition="left"
          ctaLink="/features/trends"
        />

        <FeatureSection
          title="Generate Unique Designs Instantly"
          description="Describe your idea, and our AI brings it to life in seconds. Create endless variations, never run out of design ideas."
          mockupContent={<AIStudioMockup />}
          textPosition="right"
          ctaText="Try the Demo >"
          ctaLink="/demo/ai-studio"
        />

        <FeatureSection
          title="Create Stunning Product Mockups Automatically"
          description="Apply your AI designs to professional mockups for t-shirts, mugs, posters, and more in just a click."
          mockupContent={<AutoMockupMockup />}
          textPosition="left"
          ctaText="See Examples >"
          ctaLink="/features/mockups"
        />

        <FeatureSection
          title="Publish Listings That Get Found"
          description="Our AI helps optimize your titles, descriptions and tags for maximum Etsy visibility. Publish directly to Etsy drafts."
          mockupContent={<PublishingMockup />}
          textPosition="right"
          ctaLink="/features/publishing"
        />

        <TestimonialsSection />
        <PricingSnippetSection />
        <FinalCTASection />
        <Footer />
      </div>
    </ThemeProvider>
  );
};

export default LandingPage;

