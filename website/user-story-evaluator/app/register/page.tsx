'use client';
// import { useRouter } from 'next/navigation';
import { supabase } from '@/utils/supabaseClient';
import './register.css';

export default function RegisterPage() {
  // const router = useRouter();

  const handleGoogleSignIn = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        // 👇 force it to the exact registered redirect URI
        redirectTo: 'http://localhost:3000/oauth/callback',
      },
    });

    if (error) {
      console.error('Google sign-in error:', error.message);
      alert('Google Sign-In failed');
    }
  };

  return (
    <div className="landing-wrapper">
      <h1 className="landing-title">Welcome to the User-Story Evaluation Tool</h1>
      <p className="landing-subtitle">
        Sign in to evaluate user stories based on clarity, understandability, readability, and technical relevance.
      </p>

      <button onClick={handleGoogleSignIn} className="google-button">
        <img
          src="https://developers.google.com/identity/images/g-logo.png"
          alt="Google logo"
          className="google-logo"
        />
        Sign in with Google
      </button>
    </div>
  );
}
