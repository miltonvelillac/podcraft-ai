import { HttpErrorResponse } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideAnimations } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

import { PodcastGeneratorApiService } from '../services/podcast-generator-api.service';
import { PodcastGeneratorPageComponent } from './podcast-generator-page.component';

describe('PodcastGeneratorPageComponent', () => {
  let fixture: ComponentFixture<PodcastGeneratorPageComponent>;
  let api: jasmine.SpyObj<PodcastGeneratorApiService>;

  beforeEach(async () => {
    api = jasmine.createSpyObj<PodcastGeneratorApiService>('PodcastGeneratorApiService', [
      'generateFromText',
      'generateFromPdf',
    ]);

    await TestBed.configureTestingModule({
      imports: [PodcastGeneratorPageComponent],
      providers: [
        provideAnimations(),
        { provide: PodcastGeneratorApiService, useValue: api },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(PodcastGeneratorPageComponent);
    fixture.detectChanges();
  });

  it('renders the generator page', () => {
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.textContent).toContain('Podcast Generator');
    expect(compiled.textContent).toContain('Source');
    expect(compiled.textContent).toContain('Output');
  });

  it('calls the API and renders successful text generation', () => {
    api.generateFromText.and.returnValue(
      of({
        podcast_id: 'podcast-test',
        title: 'Generated title',
        script: 'Generated script',
        audio_url: '/generated/audio/podcast-test.wav',
        duration_seconds: 120,
      }),
    );

    fixture.componentInstance['form'].controls.text.setValue(
      'FastAPI coordinates the podcast generation workflow.',
    );
    fixture.componentInstance['form'].controls.language.setValue('es');
    fixture.componentInstance['generatePodcast']();
    fixture.detectChanges();

    expect(api.generateFromText).toHaveBeenCalledWith(
      jasmine.objectContaining({
        generation_mode: 'podcast',
        language: 'es',
      }),
    );
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('Generated script');
  });

  it('sends read aloud generation mode', () => {
    api.generateFromText.and.returnValue(
      of({
        podcast_id: 'audio-test',
        title: 'Narrated Audio',
        script: 'Narrated text',
        audio_url: '/generated/audio/audio-test.wav',
        duration_seconds: 30,
      }),
    );

    fixture.componentInstance['form'].controls.text.setValue('Read this text aloud directly.');
    fixture.componentInstance['form'].controls.generationMode.setValue('read_aloud');
    fixture.componentInstance['generatePodcast']();

    expect(api.generateFromText).toHaveBeenCalledWith(
      jasmine.objectContaining({
        generation_mode: 'read_aloud',
      }),
    );
  });

  it('renders translated narration text for read aloud responses', () => {
    api.generateFromText.and.returnValue(
      of({
        podcast_id: 'audio-test',
        title: 'Narrated Audio',
        script: 'Hello, I like pizza.',
        audio_url: '/generated/audio/audio-test.wav',
        duration_seconds: 30,
      }),
    );

    fixture.componentInstance['form'].controls.text.setValue('hola me gusta la pizza');
    fixture.componentInstance['form'].controls.generationMode.setValue('read_aloud');
    fixture.componentInstance['form'].controls.language.setValue('en');
    fixture.componentInstance['generatePodcast']();
    fixture.detectChanges();

    const textContent = (fixture.nativeElement as HTMLElement).textContent ?? '';
    expect(textContent).toContain('Narration Text');
    expect(textContent).toContain('Hello, I like pizza.');
  });

  it('renders backend translation errors', () => {
    api.generateFromText.and.returnValue(
      throwError(
        () =>
          new HttpErrorResponse({
            status: 400,
            error: {
              detail:
                'Translation is not configured. Set OPENAI_API_KEY or use TRANSLATION_PROVIDER=mock.',
            },
          }),
      ),
    );

    fixture.componentInstance['form'].controls.text.setValue('hola me gusta la pizza');
    fixture.componentInstance['form'].controls.generationMode.setValue('read_aloud');
    fixture.componentInstance['generatePodcast']();
    fixture.detectChanges();

    expect((fixture.nativeElement as HTMLElement).textContent).toContain(
      'Translation is not configured. Set OPENAI_API_KEY or use TRANSLATION_PROVIDER=mock.',
    );
  });
});
