import { ChangeDetectionStrategy, Component } from '@angular/core';

import { PodcastGeneratorPageComponent } from './features/podcast-generator/pages/podcast-generator-page.component';

@Component({
  selector: 'app-root',
  imports: [PodcastGeneratorPageComponent],
  template: '<app-podcast-generator-page />',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AppComponent {}
