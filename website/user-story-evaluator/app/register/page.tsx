// 'use client';
// // import { useRouter } from 'next/navigation';
// import { supabase } from '@/utils/supabaseClient';
// import './register.css';

// export default function RegisterPage() {
//   // const router = useRouter();

//   const handleGoogleSignIn = async () => {
//     const { error } = await supabase.auth.signInWithOAuth({
//       provider: 'google',
//       options: {
//         // 👇 force it to the exact registered redirect URI
//         redirectTo: 'http://localhost:3000/oauth/callback',
//       },
//     });

//     if (error) {
//       console.error('Google sign-in error:', error.message);
//       alert('Google Sign-In failed');
//     }
//   };

//   return (
//     <div className="landing-wrapper">
//       <h1 className="landing-title">Welcome to the User-Story Evaluation Tool</h1>
//       <p className="landing-subtitle">
//         Sign in to evaluate user stories based on clarity, understandability, readability, and technical relevance.
//       </p>

//       <button onClick={handleGoogleSignIn} className="google-button">
//         <img
//           src="https://developers.google.com/identity/images/g-logo.png"
//           alt="Google logo"
//           className="google-logo"
//         />
//         Sign in with Google
//       </button>
//     </div>
//   );
// }
'use client';
import { supabase } from '@/utils/supabaseClient';
import './register.css';

export default function RegisterPage() {
  const handleGoogleSignIn = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: 'http://localhost:3000/oauth/callback',
      },
    });

    if (error) {
      console.error('Google sign-in error:', error.message);
      alert('Google Sign-In failed');
    }
  };

  return (
    <div className="landing-container">
      <nav className="navbar">
        <h2 className="brand">RUSTEval</h2>
      </nav>

      <div className="hero">
        <h2 className="hero-title">Better Evaluation for Better User Stories</h2>
        <p className="hero-subtitle">
          Evaluate user stories generated from app reviews using the <strong>RUST</strong> framework:
          <strong> Readability</strong>, <strong>Understandability</strong>,
          <strong> Specificity</strong>, and <strong>Technical relevance</strong>.
        </p>
      </div>

      <div className="card-container">
        <div className="card rust-readability">
          <h3>R - Readability</h3>
          <ul>
            <li>Grammatical correctness</li>
            <li>Spelling accuracy</li>
            <li>Redundancy</li>
            <li>Test case readability</li>
          </ul>
        </div>
        <div className="card rust-understandability">
          <h3>U - Understandability</h3>
          <ul>
            <li>Semantic clarity</li>
            <li>Comprehensibility</li>
            <li>Objective understanding</li>
          </ul>
        </div>
        <div className="card rust-specificity">
          <h3>S - Specificity</h3>
          <ul>
            <li>Effort estimation</li>
            <li>Acceptance criteria</li>
            <li>Implementation-critical info</li>
          </ul>
        </div>
        <div className="card rust-technical">
          <h3>T - Technical Relevance</h3>
          <ul>
            <li>Matches requirements</li>
            <li>Follows best practices</li>
          </ul>
        </div>
      </div>

      <div className="cta-container">
        <button className="google-button" onClick={handleGoogleSignIn}>
          <img
            src="https://developers.google.com/identity/images/g-logo.png"
            alt="Google logo"
            className="google-logo"
          />
          Sign in with Google
        </button>
      </div>
    </div>
  );
}
