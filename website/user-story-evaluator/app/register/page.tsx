// 'use client';
// import { useState } from 'react';
// import { useRouter } from 'next/navigation';
// import { supabase } from '@/utils/supabaseClient';

// export default function RegisterPage() {
//   const [email, setEmail] = useState('');
//   const [username, setUsername] = useState('');
//   const router = useRouter();

//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault();

//     if (!email || !username) {
//       alert('Please provide both username and email');
//       return;
//     }

//     localStorage.setItem('user_email', email);
//     localStorage.setItem('user_name', username);

//     const { data: existingUser, error } = await supabase
//       .from('users')
//       .select('*')
//       .eq('email', email)
//       .single();

//     if (error && error.code !== 'PGRST116') {
//       console.error('Error fetching user:', error);
//       alert('Unexpected error');
//       return;
//     }

//     if (!existingUser) {
//       const { error: insertError } = await supabase
//         .from('users')
//         .insert({ email, username });

//       if (insertError) {
//         console.error('Insert error:', insertError);
//         alert('Failed to register user');
//         return;
//       }

//       console.log('✅ New user inserted into Supabase.');
//     } else {
//       console.log('✅ Existing user found, skipping insert.');
//     }

//     router.push('/evaluate');
//   };

//   return (
//     <div className="min-h-screen flex items-center justify-center p-4">
//       <form onSubmit={handleSubmit} className="bg-white p-8 rounded shadow-md space-y-4 w-full max-w-sm">
//         <h2 className="text-2xl font-bold mb-4">Register</h2>

//         <input
//           type="text"
//           placeholder="Username"
//           value={username}
//           onChange={(e) => setUsername(e.target.value)}
//           className="border p-2 w-full rounded"
//           required
//         />

//         <input
//           type="email"
//           placeholder="Email"
//           value={email}
//           onChange={(e) => setEmail(e.target.value)}
//           className="border p-2 w-full rounded"
//           required
//         />

//         <button
//           type="submit"
//           className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
//         >
//           Continue
//         </button>
//       </form>
//     </div>
//   );
// }
'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/utils/supabaseClient';
import './register.css'; // 👈 Import your CSS

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !username) {
      alert('Please provide both username and email');
      return;
    }

    localStorage.setItem('user_email', email);
    localStorage.setItem('user_name', username);

    const { data: existingUser, error } = await supabase
      .from('users')
      .select('*')
      .eq('email', email)
      .single();

    if (error && error.code !== 'PGRST116') {
      console.error('Error fetching user:', error);
      alert('Unexpected error');
      return;
    }

    if (!existingUser) {
      const { error: insertError } = await supabase
        .from('users')
        .insert({ email, username });

      if (insertError) {
        console.error('Insert error:', insertError);
        alert('Failed to register user');
        return;
      }

      console.log('✅ New user inserted into Supabase.');
    } else {
      console.log('✅ Existing user found, skipping insert.');
    }

    router.push('/evaluate');
  };

  return (
    <div className="landing-wrapper">
      <h1 className="landing-title">Welcome to the User-Story Evaluation Tool</h1>
      <p className="landing-subtitle">
        Rate multiple user stories based on readability, understandability, specificity, and technical clarity.
        Please register with your email and username to begin evaluating.
      </p>

      <form onSubmit={handleSubmit} className="register-form">
        <h2>Register</h2>

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <button type="submit">Continue</button>
      </form>
    </div>
  );
}
