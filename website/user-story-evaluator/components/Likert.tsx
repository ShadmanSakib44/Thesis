import React from 'react';

interface LikertProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  disabled?: boolean;
}

export default function Likert({ label, value, onChange, disabled = false }: LikertProps) {
  return (
    <div className="p-2">
      <label className="block mb-1">{label}</label>
      <div className="flex gap-2">
        {[1, 2, 3, 4, 5].map((num) => (
          <button
            key={num}
            disabled={disabled}
            className={`px-3 py-1 border rounded ${
              value === num ? 'bg-blue-500 text-white' : 'bg-white'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
            onClick={() => !disabled && onChange(num)}
          >
            {num}
          </button>
        ))}
      </div>
    </div>
  );
}
