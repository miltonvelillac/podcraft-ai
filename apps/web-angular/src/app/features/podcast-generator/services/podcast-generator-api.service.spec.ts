import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';

import { PodcastGeneratorApiService } from './podcast-generator-api.service';

describe('PodcastGeneratorApiService', () => {
  let service: PodcastGeneratorApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    service = TestBed.inject(PodcastGeneratorApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('posts text generation requests', () => {
    service
      .generateFromText({
        input_type: 'text',
        generation_mode: 'podcast',
        text: 'FastAPI coordinates the podcast generation workflow.',
        style: 'educational',
        voice: 'default',
        language: 'es',
        target_duration: 'short',
      })
      .subscribe((response) => {
        expect(response.podcast_id).toBe('podcast-test');
      });

    const request = httpMock.expectOne('/api/podcasts/generate/text');
    expect(request.request.method).toBe('POST');
    expect(request.request.body.input_type).toBe('text');
    expect(request.request.body.generation_mode).toBe('podcast');
    expect(request.request.body.language).toBe('es');
    request.flush({
      podcast_id: 'podcast-test',
      title: 'Generated title',
      script: 'Generated script',
      audio_url: '/generated/audio/podcast-test.wav',
      duration_seconds: 120,
    });
  });

  it('posts PDF generation requests as form data', () => {
    const file = new File(['pdf'], 'source.pdf', { type: 'application/pdf' });

    service.generateFromPdf(file, 'podcast', 'conversational', 'default', 'pt', 'medium').subscribe();

    const request = httpMock.expectOne('/api/podcasts/generate/pdf');
    expect(request.request.method).toBe('POST');
    expect(request.request.body instanceof FormData).toBeTrue();
    expect(request.request.body.get('file')).toBe(file);
    expect(request.request.body.get('generation_mode')).toBe('podcast');
    expect(request.request.body.get('style')).toBe('conversational');
    expect(request.request.body.get('language')).toBe('pt');
    expect(request.request.body.get('target_duration')).toBe('medium');
    request.flush({
      podcast_id: 'podcast-test',
      title: 'Generated title',
      script: 'Generated script',
      audio_url: '/generated/audio/podcast-test.wav',
      duration_seconds: 240,
    });
  });
});
