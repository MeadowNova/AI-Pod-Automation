import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import Card from './Card';
import Button from './Button';
// Use a different icon that we know exists
import { ArrowTrendingUpIcon as CogIcon } from '@heroicons/react/24/outline';

const meta: Meta<typeof Card> = {
  component: Card,
  title: 'Components/Card',
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
};

export default meta;
type Story = StoryObj<typeof Card>;

export const Basic: Story = {
  args: {
    children: <p>This is a basic card with some content.</p>,
  },
};

export const WithTitle: Story = {
  args: {
    title: 'Card Title',
    children: <p>This is a card with a title.</p>,
  },
};

export const WithTitleAndSubtitle: Story = {
  args: {
    title: 'Card Title',
    subtitle: 'Card Subtitle',
    children: <p>This is a card with a title and subtitle.</p>,
  },
};

export const WithFooter: Story = {
  args: {
    title: 'Card Title',
    children: <p>This is a card with a footer.</p>,
    footer: (
      <div className="flex justify-end">
        <Button variant="primary">Save</Button>
      </div>
    ),
  },
};

export const WithHeaderAction: Story = {
  args: {
    title: 'Card Title',
    headerAction: (
      <Button variant="icon" icon={CogIcon} title="Settings" />
    ),
    children: <p>This is a card with a header action.</p>,
  },
};

export const Complete: Story = {
  args: {
    title: 'Card Title',
    subtitle: 'Card Subtitle',
    headerAction: (
      <Button variant="icon" icon={CogIcon} title="Settings" />
    ),
    children: <p>This is a complete card with all features.</p>,
    footer: (
      <div className="flex justify-between items-center">
        <span className="text-sm text-light-text-secondary dark:text-dark-text-secondary">Last updated: Today</span>
        <Button variant="primary">Save</Button>
      </div>
    ),
  },
};
