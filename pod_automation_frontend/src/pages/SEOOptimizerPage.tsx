import React, { useState, useEffect } from 'react';
import { ArrowPathIcon, SparklesIcon, InformationCircleIcon, DocumentTextIcon, CloudArrowUpIcon, XMarkIcon } from '@heroicons/react/24/outline';
import Button from '../components/Button'; // Import shared Button

// Mock data - replace with API calls
interface EtsyListing {
  id: string;
  title: string;
  thumbnailUrl: string;
  seoScore: number; // 0-100
  status: 'Active' | 'Draft' | 'Inactive';
  tags: string[];
  description: string;
}

const mockListings: EtsyListing[] = [
  {
    id: '1',
    title: 'Vintage Sunset T-Shirt - Retro 80s Style Graphic Tee',
    thumbnailUrl: '/placeholder-image.png',
    seoScore: 75,
    status: 'Active',
    tags: ['vintage t-shirt', 'retro shirt', '80s graphics', 'sunset tee', 'graphic tee'],
    description: 'A super soft vintage-style t-shirt featuring a stunning retro sunset graphic. Perfect for 80s enthusiasts and lovers of unique graphic tees. Made from 100% cotton for maximum comfort.'
  },
  {
    id: '2',
    title: 'Funny Cat Mug - "I Need More Coffee" - Cute Pet Lover Gift',
    thumbnailUrl: '/placeholder-image.png',
    seoScore: 60,
    status: 'Active',
    tags: ['cat mug', 'funny coffee mug', 'pet lover gift', 'cute cat', 'coffee lover'],
    description: 'Start your day with a smile with this hilarious cat mug! Features a cute cat illustration and the relatable phrase "I Need More Coffee". A great gift for any cat owner or coffee addict.'
  },
  {
    id: '3',
    title: 'Minimalist Line Art Print - Abstract Face Poster, Modern Wall Decor',
    thumbnailUrl: '/placeholder-image.png',
    seoScore: 85,
    status: 'Draft',
    tags: ['line art', 'abstract print', 'minimalist decor', 'modern wall art', 'face poster'],
    description: 'Add a touch of modern elegance to your home with this minimalist line art print. Featuring an abstract face design, this poster is perfect for contemporary interiors. High-quality print on premium paper.'
  },
];

interface SEOAnalysisDetail {
    score: number;
    feedback: string;
}

interface SEOAnalysisTagsDetail extends SEOAnalysisDetail {
    count: number;
}

interface SEOAnalysisState {
    overallScore: number;
    title: SEOAnalysisDetail;
    tags: SEOAnalysisTagsDetail;
    description: SEOAnalysisDetail;
}

const initialSeoAnalysisState: SEOAnalysisState = {
    overallScore: 0,
    title: { score: 0, feedback: 'N/A' },
    tags: { score: 0, feedback: 'N/A', count: 0 },
    description: { score: 0, feedback: 'N/A' }
};

const SEOOptimizerPage: React.FC = () => {
  const [listings, setListings] = useState<EtsyListing[]>([]);
  const [selectedListing, setSelectedListing] = useState<EtsyListing | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoadingListings, setIsLoadingListings] = useState(false);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);

  // Form states for the selected listing
  const [currentTitle, setCurrentTitle] = useState('');
  const [currentTags, setCurrentTags] = useState<string[]>([]);
  const [currentTagInput, setCurrentTagInput] = useState('');
  const [currentDescription, setCurrentDescription] = useState('');

  // AI Suggestion states
  const [titleSuggestions, setTitleSuggestions] = useState<string[]>([]);
  const [tagSuggestions, setTagSuggestions] = useState<string[]>([]);
  const [descriptionSuggestions, setDescriptionSuggestions] = useState<string[]>([]);
  
  const [seoAnalysis, setSeoAnalysis] = useState<SEOAnalysisState>(initialSeoAnalysisState);

  const fetchListings = () => {
    setIsLoadingListings(true);
    setTimeout(() => {
      setListings(mockListings);
      setIsLoadingListings(false);
    }, 1000);
  };

  useEffect(() => {
    fetchListings();
  }, []);

  useEffect(() => {
    if (selectedListing) {
      setCurrentTitle(selectedListing.title);
      setCurrentTags(selectedListing.tags || []);
      setCurrentDescription(selectedListing.description);
      updateSeoAnalysis(selectedListing.title, selectedListing.tags || [], selectedListing.description);
    } else {
      setCurrentTitle('');
      setCurrentTags([]);
      setCurrentDescription('');
      setSeoAnalysis(initialSeoAnalysisState);
    }
  }, [selectedListing]);

  const handleSelectListing = (listing: EtsyListing) => {
    setSelectedListing(listing);
  };

  const filteredListings = listings.filter(listing =>
    listing.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getSeoScoreColor = (score: number) => {
    if (score >= 80) return 'bg-success';
    if (score >= 50) return 'bg-yellow-500';
    return 'bg-error';
  };

  const handleTagInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentTagInput(e.target.value);
  };

  const handleAddTag = () => {
    if (currentTagInput.trim() !== '' && currentTags.length < 13 && !currentTags.includes(currentTagInput.trim())) {
      const newTags = [...currentTags, currentTagInput.trim()];
      setCurrentTags(newTags);
      updateSeoAnalysis(currentTitle, newTags, currentDescription);
    }
    setCurrentTagInput('');
  };

  const handleRemoveTag = (tagToRemove: string) => {
    const newTags = currentTags.filter(tag => tag !== tagToRemove);
    setCurrentTags(newTags);
    updateSeoAnalysis(currentTitle, newTags, currentDescription);
  };

  const fetchAISuggestions = (type: 'title' | 'tags' | 'description') => {
    setIsLoadingSuggestions(true);
    setTimeout(() => {
      if (type === 'title') setTitleSuggestions(['Optimized Title Example 1', 'Another Great Title Idea']);
      if (type === 'tags') setTagSuggestions(['new tag 1', 'suggested tag 2', 'keyword idea']);
      if (type === 'description') setDescriptionSuggestions(['This is an AI suggested description snippet that is much better.', 'Alternative description focusing on benefits.']);
      setIsLoadingSuggestions(false);
    }, 1500);
  };

  const updateSeoAnalysis = (title: string, tags: string[], description: string) => {
    let overallScore = 0;
    let titleScore = 0;
    const titleFeedbackMessages = [];
    if (title.length > 10 && title.length < 140) titleScore += 40; else titleFeedbackMessages.push('Title length suboptimal.');
    if (title.toLowerCase().includes('vintage')) titleScore += 10;
    titleScore = Math.min(titleScore, 100);
    overallScore += titleScore * 0.4;

    let tagScore = 0;
    const tagFeedbackMessages = [];
    if (tags.length > 5 && tags.length <= 13) tagScore += 50; else tagFeedbackMessages.push('Tag count suboptimal.');
    if (tags.some(t => t.includes('shirt'))) tagScore += 10;
    tagScore = Math.min(tagScore, 100);
    overallScore += tagScore * 0.3;

    let descScore = 0;
    const descFeedbackMessages = [];
    if (description.length > 50) descScore += 30; else descFeedbackMessages.push('Description too short.');
    if (description.toLowerCase().includes('cotton')) descScore += 10;
    descScore = Math.min(descScore, 100);
    overallScore += descScore * 0.3;
    
    setSeoAnalysis({
        overallScore: Math.round(overallScore),
        title: { score: titleScore, feedback: titleFeedbackMessages.join(' ') || 'Looking good!' },
        tags: { score: tagScore, feedback: tagFeedbackMessages.join(' ') || 'Well tagged!', count: tags.length },
        description: { score: descScore, feedback: descFeedbackMessages.join(' ') || 'Description seems fine.' }
    });
  };

  useEffect(() => {
    if (selectedListing) {
        updateSeoAnalysis(currentTitle, currentTags, currentDescription);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentTitle, currentTags, currentDescription]);

  const handleSaveDraft = () => { alert('Save Draft clicked (not implemented)'); };
  const handlePublish = () => { alert('Publish to Etsy clicked (not implemented)'); };

  return (
    <div className="flex flex-col lg:flex-row gap-6 h-full">
      {/* Left Panel: Listing Management */}
      <div className="lg:w-1/3 bg-white dark:bg-dark-bg p-6 rounded-lg shadow space-y-4 flex flex-col">
        <h2 className="text-xl font-semibold text-light-text dark:text-dark-text">Your Etsy Listings</h2>
        <div className="flex items-center space-x-2">
          <input
            type="text"
            placeholder="Search your listings..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-grow p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text"
          />
          <Button variant="primary" onClick={fetchListings} disabled={isLoadingListings} title="Fetch/Refresh Listings" className="px-3 py-1.5">
            <ArrowPathIcon className={`h-5 w-5 ${isLoadingListings ? 'animate-spin' : ''}`} />
          </Button>
        </div>
        <div className="flex-grow overflow-y-auto space-y-3 pr-1">
          {isLoadingListings ? (
            <p className="text-light-text-secondary dark:text-dark-text-secondary">Loading listings...</p>
          ) : filteredListings.length > 0 ? (
            filteredListings.map(listing => (
              <div
                key={listing.id}
                onClick={() => handleSelectListing(listing)}
                className={`p-3 border rounded-lg cursor-pointer hover:border-primary dark:hover:border-primary-light transition-colors flex items-center space-x-3 ${selectedListing?.id === listing.id ? 'border-primary dark:border-primary-light bg-primary-light/10 dark:bg-primary/10' : 'border-gray-200 dark:border-dark-border'}`}
              >
                <img src={listing.thumbnailUrl} alt={listing.title} className="w-16 h-16 object-cover rounded-md bg-gray-200 dark:bg-dark-border" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-light-text dark:text-dark-text truncate">{listing.title}</p>
                  <div className="flex items-center text-xs mt-1">
                    <span className={`w-3 h-3 rounded-full mr-1.5 ${getSeoScoreColor(listing.seoScore)}`}></span>
                    <span className="text-light-text-secondary dark:text-dark-text-secondary">{listing.seoScore}/100 | {listing.status}</span>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p className="text-light-text-secondary dark:text-dark-text-secondary">No listings found. Try a different search or refresh.</p>
          )}
        </div>
      </div>

      {/* Right Panel: Detailed Optimization View */}
      <div className="lg:w-2/3 bg-white dark:bg-dark-bg p-6 rounded-lg shadow space-y-6 overflow-y-auto">
        {selectedListing ? (
          <>
            <h2 className="text-xl font-semibold text-light-text dark:text-dark-text">Optimize: <span className="text-primary dark:text-primary-light">{selectedListing.title}</span></h2>
            
            <div className="p-4 border border-gray-200 dark:border-dark-border rounded-lg">
                <h3 className="text-lg font-semibold mb-2 text-light-text dark:text-dark-text">Overall SEO Score: {seoAnalysis.overallScore}/100</h3>
                <div className="w-full bg-gray-200 rounded-full h-4 dark:bg-dark-border mb-2">
                    <div className={`h-4 rounded-full ${getSeoScoreColor(seoAnalysis.overallScore)}`} style={{ width: `${seoAnalysis.overallScore}%` }}></div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div><strong className="block text-light-text-secondary dark:text-dark-text-secondary">Title:</strong> {seoAnalysis.title.feedback} ({seoAnalysis.title.score}/100)</div>
                    <div><strong className="block text-light-text-secondary dark:text-dark-text-secondary">Tags ({seoAnalysis.tags.count}/13):</strong> {seoAnalysis.tags.feedback} ({seoAnalysis.tags.score}/100)</div>
                    <div><strong className="block text-light-text-secondary dark:text-dark-text-secondary">Description:</strong> {seoAnalysis.description.feedback} ({seoAnalysis.description.score}/100)</div>
                </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="title" className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary">Title ({currentTitle.length}/140)</label>
              <div className="flex items-center">
                <input
                  type="text"
                  id="title"
                  value={currentTitle}
                  onChange={(e) => setCurrentTitle(e.target.value)}
                  maxLength={140}
                  className="flex-grow p-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text"
                />
                <Button variant="secondary" onClick={() => fetchAISuggestions('title')} disabled={isLoadingSuggestions} className="rounded-l-none rounded-r-md border-l-0 border-gray-300 dark:border-dark-border px-3 py-1.5">
                  <SparklesIcon className={`h-5 w-5 ${isLoadingSuggestions ? 'animate-spin' : ''}`} /> AI
                </Button>
              </div>
              {titleSuggestions.length > 0 && (
                <div className="mt-2 p-2 border border-gray-200 dark:border-dark-border rounded-md bg-gray-50 dark:bg-dark-card/50 space-y-1">
                  {titleSuggestions.map((s, i) => <Button key={i} variant='link' onClick={() => setCurrentTitle(s)}>{s}</Button>)}
                </div>
              )}
            </div>

            <div className="space-y-2">
              <label htmlFor="tags" className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary">Tags ({currentTags.length}/13)</label>
              <div className="flex items-center mb-2">
                <input
                  type="text"
                  id="tags"
                  placeholder="Enter a tag and press Add..."
                  value={currentTagInput}
                  onChange={handleTagInputChange}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                  className="flex-grow p-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text"
                />
                <Button variant="secondary" onClick={handleAddTag} disabled={currentTags.length >= 13 || currentTagInput.trim() === ''} className="rounded-l-none rounded-r-md border-l-0 border-gray-300 dark:border-dark-border px-3 py-1.5">
                  Add Tag
                </Button>
                <Button variant="secondary" onClick={() => fetchAISuggestions('tags')} disabled={isLoadingSuggestions} className="ml-2 px-3 py-1.5">
                  <SparklesIcon className={`h-5 w-5 ${isLoadingSuggestions ? 'animate-spin' : ''}`} /> AI Tags
                </Button>
              </div>
              <div className="flex flex-wrap gap-2 mb-2">
                {currentTags.map(tag => (
                  <span key={tag} className="flex items-center bg-gray-200 dark:bg-dark-card text-sm rounded-full px-3 py-1">
                    {tag}
                    <Button variant="icon" onClick={() => handleRemoveTag(tag)} className="ml-1.5 p-0.5 hover:bg-gray-300 dark:hover:bg-dark-border rounded-full">
                      <XMarkIcon className="h-3 w-3" />
                    </Button>
                  </span>
                ))}
              </div>
              {tagSuggestions.length > 0 && (
                <div className="mt-2 p-2 border border-gray-200 dark:border-dark-border rounded-md bg-gray-50 dark:bg-dark-card/50 space-y-1">
                  {tagSuggestions.map((s, i) => <Button key={i} variant='link' onClick={() => { if (currentTags.length < 13 && !currentTags.includes(s)) { const newTags = [...currentTags, s]; setCurrentTags(newTags); updateSeoAnalysis(currentTitle, newTags, currentDescription); } }}>{s}</Button>)}
                </div>
              )}
            </div>

            <div className="space-y-2">
              <label htmlFor="description" className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary">Description</label>
              <div className="relative">
                <textarea
                  id="description"
                  rows={6}
                  value={currentDescription}
                  onChange={(e) => setCurrentDescription(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text"
                />
                <Button variant="icon" onClick={() => fetchAISuggestions('description')} disabled={isLoadingSuggestions} className="absolute bottom-2 right-2 p-1">
                  <SparklesIcon className={`h-5 w-5 ${isLoadingSuggestions ? 'animate-spin' : ''}`} />
                </Button>
              </div>
              {descriptionSuggestions.length > 0 && (
                <div className="mt-2 p-2 border border-gray-200 dark:border-dark-border rounded-md bg-gray-50 dark:bg-dark-card/50 space-y-1">
                  {descriptionSuggestions.map((s, i) => <Button key={i} variant='link' onClick={() => setCurrentDescription(prev => prev + (prev ? '\n\n' : '') + s)}>{s} (Append)</Button>)}
                </div>
              )}
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-dark-border">
              <Button variant="outline" onClick={handleSaveDraft}>
                <DocumentTextIcon className="h-5 w-5 mr-1" /> Save Draft
              </Button>
              <Button variant="primary" onClick={handlePublish}>
                <CloudArrowUpIcon className="h-5 w-5 mr-1" /> Publish to Etsy
              </Button>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <InformationCircleIcon className="h-16 w-16 text-gray-400 dark:text-gray-500 mb-4" />
            <p className="text-lg font-medium text-light-text dark:text-dark-text">Select a listing from the left panel to start optimizing.</p>
            <p className="text-sm text-light-text-secondary dark:text-dark-text-secondary">Use the search to find specific listings or refresh to fetch the latest data.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SEOOptimizerPage;

