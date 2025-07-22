'use client';
import { useEffect, useState } from 'react';
import Papa from 'papaparse';
import { supabase } from '@/utils/supabaseClient';

const ALLOWED_USER_ID = '7ad2e323-d3a0-4cfa-9ec5-89e6e72ed928';
const SOURCE_TAGS = ['human_story', 'chatgpt', 'gemini', 'mistral'];

export default function CSVUploadPage() {
  const [authorized, setAuthorized] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState('');

  useEffect(() => {
    const checkAuth = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (session?.user?.id === ALLOWED_USER_ID) {
        setAuthorized(true);
      }
    };
    checkAuth();
  }, []);

  const handleCSVUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setStatus('Reading file...');

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: async (results) => {
        const rows = results.data as any[];

        for (const row of rows) {
          const reviewText = row['app_review'];
          const { data: reviewData, error: reviewError } = await supabase
            .from('reviews')
            .insert({ text: reviewText })
            .select('id')
            .single();

          if (reviewError || !reviewData) {
            console.error('❌ Review insert error:', reviewError?.message);
            setStatus(`Failed to insert review: ${reviewText}`);
            continue;
          }

          const reviewId = reviewData.id;

          const stories = SOURCE_TAGS.map((tag, index) => ({
            review_id: reviewId,
            index,
            story_text: row[tag],
            source_tag: tag,
          }));

          const { error: storyError } = await supabase.from('user_stories').insert(stories);
          if (storyError) {
            console.error('❌ Story insert error:', storyError.message);
            setStatus(`Failed to insert stories for review: ${reviewText}`);
            continue;
          }

          console.log(`✅ Inserted: ${reviewText}`);
        }

        setStatus('🎉 Upload complete!');
        setUploading(false);
      },
    });
  };

  if (!authorized) {
    return <p className="p-8 text-red-600">🚫 Access Denied</p>;
  }

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-4">CSV Upload (Admin Only)</h2>
      <input
        type="file"
        accept=".csv"
        onChange={handleCSVUpload}
        disabled={uploading}
        className="mb-4"
      />
      <p>{status}</p>
    </div>
  );
}
