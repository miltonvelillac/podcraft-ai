export type PodcastInputMode = 'text' | 'pdf';
export type GenerationMode = 'podcast' | 'read_aloud';
export type PodcastStyle = 'educational' | 'conversational' | 'executive_summary';
export type PodcastTargetDuration = 'short' | 'medium' | 'long';
export type PodcastLanguage = 'en' | 'es' | 'pt';

export interface GeneratePodcastTextRequest {
  input_type: 'text';
  generation_mode: GenerationMode;
  text: string;
  style: PodcastStyle;
  voice: string;
  language: PodcastLanguage;
  target_duration: PodcastTargetDuration;
}

export interface GeneratePodcastResponse {
  podcast_id: string;
  title: string;
  script: string;
  audio_url: string;
  duration_seconds: number;
}

export interface Option<TValue extends string> {
  value: TValue;
  label: string;
}
