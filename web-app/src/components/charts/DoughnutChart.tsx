'use client';

import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { Doughnut } from 'react-chartjs-2';

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend
);

interface DoughnutChartProps {
  data: number[];
  labels: string[];
  colors?: string[];
  title?: string;
  centerText?: string;
}

export function DoughnutChart({
  data,
  labels,
  colors,
  title,
  centerText
}: DoughnutChartProps) {
  const defaultColors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  const chartData = {
    labels,
    datasets: [
      {
        data,
        backgroundColor: colors || defaultColors,
        borderColor: '#18181b',
        borderWidth: 4,
        hoverOffset: 10,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '70%',
    plugins: {
      legend: {
        display: true,
        position: 'bottom' as const,
        labels: {
          color: '#a1a1aa',
          padding: 16,
          font: {
            size: 12,
          },
          usePointStyle: true,
          pointStyle: 'circle' as const,
        },
      },
      title: {
        display: !!title,
        text: title,
        color: '#fff',
        font: {
          size: 16,
          weight: 'bold' as const,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#3f3f46',
        borderWidth: 1,
        padding: 12,
      },
    },
  };

  return (
    <div className="relative h-64 w-full">
      <Doughnut data={chartData} options={options} />
      {centerText && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center">
            <p className="text-3xl font-bold text-white">{centerText}</p>
            <p className="text-sm text-zinc-400">Complete</p>
          </div>
        </div>
      )}
    </div>
  );
}
