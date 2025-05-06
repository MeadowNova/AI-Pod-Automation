import type { Meta, StoryObj } from '@storybook/react';
import StatCard from './StatCard';
import { BanknotesIcon, DocumentDuplicateIcon, CpuChipIcon } from '@heroicons/react/24/outline';

const meta: Meta<typeof StatCard> = {
  component: StatCard,
  title: 'Components/StatCard',
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
};

export default meta;
type Story = StoryObj<typeof StatCard>;

export const Revenue: Story = {
  args: {
    title: "Revenue",
    value: "$123.45",
    change: "+10%",
    icon: BanknotesIcon
  },
};

export const Orders: Story = {
  args: {
    title: "Orders",
    value: "15",
    change: "-5%",
    icon: DocumentDuplicateIcon
  },
};

export const Credits: Story = {
  args: {
    title: "AI Credits",
    value: "850",
    icon: CpuChipIcon
  },
};
