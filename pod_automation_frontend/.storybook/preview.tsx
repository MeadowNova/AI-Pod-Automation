import React from 'react';
import type { Preview } from '@storybook/react';
import { MemoryRouter } from 'react-router-dom';
import '../src/index.css'; // Import your global styles

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: '^on[A-Z].*' },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    // Add padding for components but not for full-page stories
    layout: 'padded',
    backgrounds: {
      default: 'light',
      values: [
        {
          name: 'light',
          value: '#F9FAFB', // Light background from your theme
        },
        {
          name: 'dark',
          value: '#111827', // Dark background from your theme
        },
      ],
    },
  },
  // Add decorators for context providers
  decorators: [
    // Dark mode decorator
    (Story, context) => {
      // Apply dark mode class if using dark background
      const isDarkMode = context.parameters.backgrounds?.value === '#111827';

      return (
        <div className={`font-sans antialiased ${isDarkMode ? 'dark' : ''}`}>
          <div className={`${context.parameters.layout === 'fullscreen' ? 'min-h-screen bg-light-bg dark:bg-dark-bg' : ''}`}>
            <Story />
          </div>
        </div>
      );
    },

    // Router decorator - wrap all stories in MemoryRouter by default
    // Individual stories can override this with their own router setup
    (Story, context) => {
      // Skip router if the story explicitly opts out
      if (context.parameters.skipRouter) {
        return <Story />;
      }

      return (
        <MemoryRouter initialEntries={['/']}>
          <Story />
        </MemoryRouter>
      );
    },
  ],
};

export default preview;
