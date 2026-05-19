import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import {
  GeneratePodcastResponse,
  GeneratePodcastTextRequest,
  PodcastStyle,
  PodcastTargetDuration,
} from '../models/podcast-generator.models';

@Injectable({
  providedIn: 'root',
})
export class PodcastGeneratorApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api/podcasts/generate';

  generateFromText(request: GeneratePodcastTextRequest): Observable<GeneratePodcastResponse> {
    return this.http.post<GeneratePodcastResponse>(`${this.baseUrl}/text`, request);
  }

  generateFromPdf(
    file: File,
    style: PodcastStyle,
    voice: string,
    targetDuration: PodcastTargetDuration,
  ): Observable<GeneratePodcastResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('style', style);
    formData.append('voice', voice);
    formData.append('target_duration', targetDuration);

    return this.http.post<GeneratePodcastResponse>(`${this.baseUrl}/pdf`, formData);
  }
}
