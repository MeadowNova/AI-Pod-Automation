import type { Meta, StoryObj } from '@storybook/react';
import DashboardPage from './DashboardPage';

const meta: Meta<typeof DashboardPage> = {
  component: DashboardPage,
  title: 'Pages/Dashboard',
  tags: ['autodocs'],
  parameters: {
    // Use a larger canvas for page components
    layout: 'fullscreen',
    // Ensure proper padding for the page
    padding: {
      top: 0,
      bottom: 0,
      left: 0,
      right: 0,
    },
  },
  // Add a decorator to provide the page with proper layout
  decorators: [
    (Story) => (
      <div className="p-6 min-h-screen bg-light-bg dark:bg-dark-bg">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof DashboardPage>;

export const Default: Story = {
  args: {},
};

export const DarkMode: Story = {
  args: {},
  parameters: {
    backgrounds: {
      default: 'dark',
    },
  },
};
