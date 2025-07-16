'use client';
import { useEffect, useState } from 'react';
import { supabase } from '@/utils/supabaseClient';
import UserStoryBlock from '@/components/UserStoryBlock';
import './evaluate.css';

interface UserStory {
  id: string;
  story_text: string;
  avg_score: number | null;
  index: number;
}

interface Review {
  id: string;
  content: string;
  user_stories: UserStory[];
}

export default function EvaluatePage() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [ratings, setRatings] = useState<number[][][]>([]); // shape: [review][story][aspect]
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      const email = localStorage.getItem('user_email');
      if (!email) return;

      const { data: user } = await supabase.from('users').select('*').eq('email', email).single();
      if (!user) return;
      setUserId(user.id);

      const { data: allReviews } = await supabase
        .from('app_reviews')
        .select('id, content, user_stories(id, story_text, avg_score, index)')
        .order('id', { ascending: true });

      const { data: userRatings } = await supabase
        .from('ratings')
        .select('story_id')
        .eq('user_id', user.id);

      const ratedStoryIds = userRatings?.map((r) => r.story_id) || [];

      const filteredReviews = (allReviews || [])
        .map((review) => {
          const filteredStories = review.user_stories.filter(
            (s: UserStory) => !ratedStoryIds.includes(s.id)
          );
          return { ...review, user_stories: filteredStories };
        })
        .filter((r) => r.user_stories.length > 0);

      setReviews(filteredReviews);
      setRatings(
        filteredReviews.map((review) =>
          review.user_stories.map(() => [0, 0, 0, 0]) // 4 aspects
        )
      );
    };

    load();
  }, []);

  const handleRatingChange = (storyIdx: number, aspectIdx: number, val: number) => {
    setRatings((prev) => {
      const updated = [...prev];
      updated[currentIndex][storyIdx][aspectIdx] = val;
      return updated;
    });
  };

  const submitRatings = async () => {
    if (!userId) return;

    const review = reviews[currentIndex];
    const reviewRatings = ratings[currentIndex];

    for (let i = 0; i < review.user_stories.length; i++) {
      const story = review.user_stories[i];
      const scores = reviewRatings[i];

      const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;

      // Insert rating
      await supabase.from('ratings').insert({
        user_id: userId,
        story_id: story.id,
        score: avgScore,
      });

      // Update avg_score and rating_count
      const { data: all } = await supabase
        .from('ratings')
        .select('score')
        .eq('story_id', story.id);

      const allScores = all?.map((r) => r.score) || [];
      const avg = allScores.reduce((a, b) => a + b, 0) / allScores.length;

      await supabase
        .from('user_stories')
        .update({ avg_score: avg, rating_count: allScores.length })
        .eq('id', story.id);
    }

    if (currentIndex < reviews.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      alert('✅ All reviews completed!');
      setReviews([]);
    }
  };

  const prevReview = () => setCurrentIndex((prev) => Math.max(0, prev - 1));
  const nextReview = () => setCurrentIndex((prev) => Math.min(reviews.length - 1, prev + 1));

  if (reviews.length === 0) {
    return <p className="text-center p-10">🎉 All reviews completed!</p>;
  }

  const currentReview = reviews[currentIndex];

  return (
    <div className="p-8">
      <h2 className="text-xl font-bold mb-4">App Review</h2>
      <p className="mb-6">{currentReview.content}</p>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {currentReview.user_stories.map((story, storyIdx) => (
          <UserStoryBlock
            key={story.id}
            story={story.story_text}
            ratings={ratings[currentIndex][storyIdx]}
            setRatings={(aspectIdx: number, value: number) =>
              handleRatingChange(storyIdx, aspectIdx, value)
            }
          />
        ))}
      </div>

      <div className="flex justify-between mt-6">
        <button
          onClick={prevReview}
          disabled={currentIndex === 0}
          className="px-4 py-2 bg-gray-300 text-black rounded"
        >
          Previous
        </button>

        <button
          onClick={submitRatings}
          className="px-6 py-2 bg-green-600 text-white rounded"
        >
          Submit Ratings for This Review
        </button>

        <button
          onClick={nextReview}
          disabled={currentIndex === reviews.length - 1}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Next
        </button>
      </div>
    </div>
  );
}
