// utils/parseCSV.ts
import Papa from 'papaparse';

export async function loadCSV() {
  const response = await fetch('/reviews.csv');
  const text = await response.text();

  const parsed = Papa.parse(text, {
    header: true,
    skipEmptyLines: true,
  });

  return parsed.data;
}
