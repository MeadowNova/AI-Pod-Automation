import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import Button from './Button';
// Import icons from Heroicons
import { MagnifyingGlassIcon } from '@heroicons/react/24/solid';
import { SparklesIcon } from '@heroicons/react/24/outline';

const meta: Meta<typeof Button> = {
  component: Button,
  title: 'Components/Button',
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    children: 'Primary Button',
    variant: 'primary',
  },
};

export const Secondary: Story = {
  args: {
    children: 'Secondary Button',
    variant: 'secondary',
  },
};

export const Outline: Story = {
  args: {
    children: 'Outline Button',
    variant: 'outline',
  },
};

export const Link: Story = {
  args: {
    children: 'Link Button',
    variant: 'link',
  },
};

export const WithLink: Story = {
  args: {
    children: 'Button with Link',
    variant: 'primary',
    to: '#',
  },
};

export const WithIcon: Story = {
  args: {
    children: 'Search',
    variant: 'primary',
    icon: MagnifyingGlassIcon,
  },
};

export const IconOnly: Story = {
  args: {
    variant: 'icon',
    icon: SparklesIcon,
    title: 'Generate with AI',
  },
};

export const Disabled: Story = {
  args: {
    children: 'Disabled Button',
    variant: 'primary',
    disabled: true,
  },
};

export const ExternalLink: Story = {
  args: {
    children: 'External Link',
    variant: 'primary',
    to: 'https://example.com',
    isExternal: true,
  },
};
