'use client';
import { useEffect, useState } from 'react';
import Papa from 'papaparse';
import UserStoryBlock from '@/components/UserStoryBlock';

type ReviewData = {
  review: string;
  userStory1: string;
  userStory2: string;
  userStory3: string;
  userStory4: string;
};

export default function Home() {
  const [reviews, setReviews] = useState<ReviewData[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [ratings, setRatings] = useState([
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ]);
  const [averages, setAverages] = useState<number[]>([]);
  const [bestStory, setBestStory] = useState<string | null>(null);

  useEffect(() => {
    fetch('/evaluation.csv')
      .then((res) => res.text())
      .then((text) => {
        const parsed = Papa.parse(text, {
          header: false,
          skipEmptyLines: true,
        });

        const formatted: ReviewData[] = parsed.data.map((row: any) => ({
          review: row[0],
          userStory1: row[1],
          userStory2: row[2],
          userStory3: row[3],
          userStory4: row[4],
        }));

        setReviews(formatted);
      });
  }, []);

  const computeBest = () => {
    const avgs = ratings.map(r => r.reduce((a, b) => a + b, 0) / 4);
    const max = Math.max(...avgs);
    const bestIdx = avgs.findIndex(avg => avg === max);
    setAverages(avgs);
    setBestStory(`User Story ${bestIdx + 1}`);
  };

  const nextReview = () => {
    setCurrentIndex((prev) => Math.min(prev + 1, reviews.length - 1));
    resetRatings();
  };

  const prevReview = () => {
    setCurrentIndex((prev) => Math.max(prev - 1, 0));
    resetRatings();
  };

  const resetRatings = () => {
    setRatings([
      [0, 0, 0, 0],
      [0, 0, 0, 0],
      [0, 0, 0, 0],
      [0, 0, 0, 0],
    ]);
    setAverages([]);
    setBestStory(null);
  };

  if (reviews.length === 0) return <p className="p-10 text-center">Loading...</p>;

  const current = reviews[currentIndex];

  return (
    <div className="grid grid-cols-1 gap-8 p-8 min-h-screen">
      <div className="bg-gray-100 p-6 rounded shadow-md">
        <h2 className="text-xl font-semibold mb-4">App Review</h2>
        <p>{current.review}</p>
        <div className="mt-6 flex justify-between">
          <button
            onClick={prevReview}
            disabled={currentIndex === 0}
            className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
          >
            Previous
          </button>
          <button
            onClick={nextReview}
            disabled={currentIndex === reviews.length - 1}
            className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {[current.userStory1, current.userStory2, current.userStory3, current.userStory4].map((story, idx) => (
          <UserStoryBlock
            key={idx}
            story={story}
            ratings={ratings[idx]}
            setRatings={(newRatings) =>
              setRatings((prev) => {
                const updated = [...prev];
                updated[idx] = newRatings;
                return updated;
              })
            }
            disabled={!story?.trim()}
          />
        ))}
      </div>

      <div className="flex flex-col items-start gap-4 mt-4">
        <button
          onClick={computeBest}
          className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Submit Ratings
        </button>

        {averages.length > 0 && (
          <div className="p-4 bg-green-100 border rounded">
            {averages.map((avg, i) => (
              <p key={i}>Average Score (Story {i + 1}): <strong>{avg.toFixed(2)}</strong></p>
            ))}
            <p className="mt-2">🟢 <strong>Best:</strong> {bestStory}</p>
          </div>
        )}
      </div>
    </div>
  );
}
