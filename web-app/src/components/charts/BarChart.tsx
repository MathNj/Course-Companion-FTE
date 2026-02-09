'use client';

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface BarChartProps {
  data: number[];
  labels: string[];
  label?: string;
  title?: string;
  horizontal?: boolean;
}

export function BarChart({ data, labels, label = 'Value', title, horizontal = false }: BarChartProps) {
  const chartData = {
    labels,
    datasets: [
      {
        label,
        data,
        backgroundColor: data.map((value) =>
          value >= 80 ? '#06b6d4' : value >= 60 ? '#f59e0b' : '#ef4444'
        ),
        borderColor: data.map((value) =>
          value >= 80 ? '#0891b2' : value >= 60 ? '#d97706' : '#dc2626'
        ),
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: (horizontal ? 'y' : 'x') as 'x' | 'y',
    plugins: {
      legend: {
        display: false,
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
        callbacks: {
          label: (context: any) => `${context.parsed.x || context.parsed.y}%`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        grid: {
          color: '#27272a',
        },
        ticks: {
          color: '#a1a1aa',
          callback: (value: string | number) => `${value}%`,
        },
      },
      x: {
        grid: {
          color: '#27272a',
        },
        ticks: {
          color: '#a1a1aa',
        },
      },
    },
  };

  return (
    <div className="h-64 w-full">
      <Bar data={chartData} options={options} />
    </div>
  );
}
