import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import AppLayout from './AppLayout';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

// Create a mock page component to render inside the Outlet
const MockPage = () => (
  <div className="p-6 bg-white dark:bg-dark-bg rounded-lg shadow">
    <h1 className="text-2xl font-bold text-light-text dark:text-dark-text mb-4">Dashboard Page</h1>
    <p className="text-light-text-secondary dark:text-dark-text-secondary">
      This is a placeholder for the page content that would normally be rendered by the Outlet component.
    </p>
  </div>
);

const meta: Meta<typeof AppLayout> = {
  component: AppLayout,
  title: 'Layouts/AppLayout',
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    // Skip the default router decorator from preview.tsx
    skipRouter: true,
  },
  // Custom decorator with proper route setup for AppLayout
  decorators: [
    (Story) => (
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route path="/" element={<Story />}>
            <Route index element={<MockPage />} />
            <Route path="trends" element={<MockPage />} />
            <Route path="ai-studio" element={<MockPage />} />
            <Route path="mockups" element={<MockPage />} />
            <Route path="listings" element={<MockPage />} />
            <Route path="analytics" element={<MockPage />} />
            <Route path="settings" element={<MockPage />} />
          </Route>
        </Routes>
      </MemoryRouter>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof AppLayout>;

export const Default: Story = {
  args: {},
};
