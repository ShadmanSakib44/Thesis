'use client';
import { useEffect, useState } from 'react';
import { supabase } from '@/utils/supabaseClient';
import UserStoryBlock from '@/components/UserStoryBlock';
import './evaluate.css';

interface UserStory {
  id: string;
  story_text: string;
  avg_score: number | null;
}

interface Review {
  id: string;
  text: string;
  user_stories: UserStory[];
}

export default function EvaluatePage() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [ratings, setRatings] = useState<number[][][]>([]);
  const [submitted, setSubmitted] = useState<boolean[]>([]);
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      const email = localStorage.getItem('user_email');
      if (!email) {
        console.warn('⚠️ No email found in localStorage.');
        return;
      }

      const { data: user, error: userError } = await supabase
        .from('users')
        .select('*')
        .eq('email', email)
        .single();

      if (userError || !user) {
        console.error('❌ Error fetching user or user not found:', userError);
        return;
      }

      setUserId(user.id);

      const { data: allReviews, error: reviewError } = await supabase
        .from('reviews')
        .select('id, text, user_stories(id, story_text, avg_score)')
        .order('id', { ascending: true });

      if (reviewError) {
        console.error('❌ Error fetching reviews:', reviewError);
        return;
      }

      const { data: userRatings, error: ratingsError } = await supabase
        .from('ratings')
        .select('story_id')
        .eq('user_id', user.id);

      if (ratingsError) {
        console.error('❌ Error fetching user ratings:', ratingsError);
        return;
      }

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
          review.user_stories.map(() => [0, 0, 0, 0])
        )
      );
      setSubmitted(filteredReviews.map(() => false));
    };

    load();
  }, []);

  // Check if all stories have been rated (no zeros)
  const allRated =
    reviews.length > 0 &&
    ratings[currentIndex].every((storyRatings) =>
      storyRatings.every((val) => val > 0)
    );

  const handleRatingChange = (
    storyIdx: number,
    aspectIdx: number,
    val: number
  ) => {
    setRatings((prev) => {
      const updated = [...prev];
      updated[currentIndex][storyIdx][aspectIdx] = val;
      return updated;
    });
  };

  const submitRatings = async () => {
    if (!userId) return;

    if (!allRated) {
      alert('Please rate all aspects of all stories before submitting.');
      return;
    }

    const review = reviews[currentIndex];
    const reviewRatings = ratings[currentIndex];

    for (let i = 0; i < review.user_stories.length; i++) {
      const story = review.user_stories[i];
      const [readability, understandability, specifyability, technicalAspects] =
        reviewRatings[i];
      const avgScore =
        (readability + understandability + specifyability + technicalAspects) / 4;

      await supabase.from('ratings').insert({
        user_id: userId,
        story_id: story.id,
        score: avgScore,
        readability,
        understandability,
        specifyability,
        technical_aspects: technicalAspects,
      });

      const { data: all, error: fetchError } = await supabase
        .from('ratings')
        .select('score')
        .eq('story_id', story.id);

      if (!fetchError && all) {
        const allScores = all.map((r) => r.score);
        const avg =
          allScores.reduce((a, b) => a + b, 0) / allScores.length;

        await supabase
          .from('user_stories')
          .update({ avg_score: avg, rating_count: allScores.length })
          .eq('id', story.id);
      }
    }

    // Mark this review as submitted
    setSubmitted((prev) => {
      const updated = [...prev];
      updated[currentIndex] = true;
      return updated;
    });

    // Move to next review or finish
    if (currentIndex < reviews.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      alert('✅ All reviews completed!');
      setReviews([]);
    }
  };

  const prevReview = () =>
    setCurrentIndex((prev) => Math.max(0, prev - 1));
  const nextReview = () =>
    setCurrentIndex((prev) => Math.min(reviews.length - 1, prev + 1));

  const handleLogout = () => {
    localStorage.removeItem('user_email');
    window.location.href = '/register';
  };

  if (reviews.length === 0) {
    return (
      <div className="text-center p-10">
        <p className="mb-6">🎉 All reviews completed!</p>
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-600 text-white rounded"
        >
          Logout
        </button>
      </div>
    );
  }

  const currentReview = reviews[currentIndex];

  return (
    <div className="p-8">
      <h2 className="text-xl font-bold mb-4">App Review</h2>
      <p className="mb-6">{currentReview.text}</p>

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
          disabled={!allRated || submitted[currentIndex]}
          className="px-6 py-2 bg-green-600 text-white rounded disabled:opacity-50"
        >
          {submitted[currentIndex] ? 'Submitted' : 'Submit Ratings for This Review'}
        </button>

        <button
          onClick={nextReview}
          disabled={!submitted[currentIndex] || currentIndex === reviews.length - 1}
          className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
}
