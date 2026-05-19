export type PodcastInputMode = 'text' | 'pdf';
export type PodcastStyle = 'educational' | 'conversational' | 'executive_summary';
export type PodcastTargetDuration = 'short' | 'medium' | 'long';

export interface GeneratePodcastTextRequest {
  input_type: 'text';
  text: string;
  style: PodcastStyle;
  voice: string;
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
