import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideAnimations } from '@angular/platform-browser/animations';
import { of } from 'rxjs';

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
    fixture.componentInstance['generatePodcast']();
    fixture.detectChanges();

    expect(api.generateFromText).toHaveBeenCalled();
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('Generated script');
  });
});
