import type { Meta, StoryObj } from '@storybook/react';
import ThemeToggle from './ThemeToggle';
import { ThemeProvider } from '../contexts/ThemeContext';

const meta: Meta<typeof ThemeToggle> = {
  component: ThemeToggle,
  title: 'Components/ThemeToggle',
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof ThemeToggle>;

export const Default: Story = {
  args: {},
};

export const WithCustomClass: Story = {
  args: {
    className: 'border border-gray-300 dark:border-gray-700',
  },
};
