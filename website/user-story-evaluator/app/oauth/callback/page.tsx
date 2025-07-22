'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/utils/supabaseClient';

export default function OAuthCallbackPage() {
  const router = useRouter();

  useEffect(() => {
    const handleOAuthRedirect = async () => {
      const {
        data: { session },
        error,
      } = await supabase.auth.getSession();

      if (error) {
        console.error('Session error:', error.message);
        return;
      }

      if (!session) {
        console.log('Session not ready yet. Retrying in 500ms...');
        setTimeout(handleOAuthRedirect, 500); // retry after short delay
        return;
      }

      const user = session.user;
      const email = user.email;
      const username = user.user_metadata?.name || email?.split('@')[0];

      if (!email || !username) {
        alert('Missing user information from Google account.');
        return;
      }

      localStorage.setItem('user_email', email);
      localStorage.setItem('user_name', username);

      try {
        const { data: existingUser, error: fetchError } = await supabase
          .from('users')
          .select('*')
          .eq('email', email)
          .single();

        if (fetchError && fetchError.code !== 'PGRST116') {
          console.error('Fetch user error:', fetchError.message);
          return;
        }

        if (!existingUser) {
          const { error: insertError } = await supabase
            .from('users')
            .insert({ email, username });

          if (insertError) {
            console.error('Insert user error:', insertError.message);
            return;
          }

          console.log('✅ New user inserted');
        } else {
          console.log('✅ Existing user found');
        }

        router.push('/evaluate');
      } catch (err) {
        console.error('Unexpected error:', err);
      }
    };

    handleOAuthRedirect();
  }, [router]);

  return <p>Redirecting... please wait</p>;
}
