import { createClient, SupabaseClient } from '@supabase/supabase-js'

let supabaseInstance: SupabaseClient | null = null

export function getSupabase(): SupabaseClient {
  if (!supabaseInstance) {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL!
    const key = process.env.NEXT_PUBLIC_SUPABASE_KEY!
    supabaseInstance = createClient(url, key)
  }
  return supabaseInstance
}

export const supabase = {
  from: (table: string) => getSupabase().from(table)
}
