import React from 'react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

// This decorator wraps stories in a MemoryRouter
export const RouterDecorator = (Story) => (
  <MemoryRouter initialEntries={['/']}>
    <Routes>
      <Route path="/" element={<Story />} />
    </Routes>
  </MemoryRouter>
);

// This decorator is for components that need to be inside a Route with an Outlet
export const OutletRouterDecorator = (Story) => {
  const MockOutlet = () => (
    <div className="p-4 bg-white dark:bg-dark-bg rounded shadow">
      <h2 className="text-xl font-bold mb-2">Mock Outlet Content</h2>
      <p>This is placeholder content for the Outlet component.</p>
    </div>
  );

  return (
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route path="/" element={<Story />}>
          <Route index element={<MockOutlet />} />
          <Route path="trends" element={<MockOutlet />} />
          <Route path="ai-studio" element={<MockOutlet />} />
          <Route path="mockups" element={<MockOutlet />} />
          <Route path="listings" element={<MockOutlet />} />
          <Route path="analytics" element={<MockOutlet />} />
          <Route path="settings" element={<MockOutlet />} />
        </Route>
      </Routes>
    </MemoryRouter>
  );
};
