import { HttpErrorResponse } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';

import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatTooltipModule } from '@angular/material/tooltip';

import {
  GeneratePodcastResponse,
  Option,
  PodcastInputMode,
  PodcastStyle,
  PodcastTargetDuration,
} from '../models/podcast-generator.models';
import { PodcastGeneratorApiService } from '../services/podcast-generator-api.service';

@Component({
  selector: 'app-podcast-generator-page',
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatCardModule,
    MatDividerModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    MatTooltipModule,
  ],
  templateUrl: './podcast-generator-page.component.html',
  styleUrl: './podcast-generator-page.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PodcastGeneratorPageComponent {
  private readonly formBuilder = inject(FormBuilder);
  private readonly api = inject(PodcastGeneratorApiService);

  protected readonly styles: Option<PodcastStyle>[] = [
    { value: 'educational', label: 'Educational' },
    { value: 'conversational', label: 'Conversational' },
    { value: 'executive_summary', label: 'Executive summary' },
  ];
  protected readonly voices: Option<string>[] = [
    { value: 'default', label: 'Default' },
    { value: 'studio', label: 'Studio' },
    { value: 'briefing', label: 'Briefing' },
  ];
  protected readonly durations: Option<PodcastTargetDuration>[] = [
    { value: 'short', label: 'Short' },
    { value: 'medium', label: 'Medium' },
    { value: 'long', label: 'Long' },
  ];

  protected readonly form = this.formBuilder.nonNullable.group({
    inputMode: this.formBuilder.nonNullable.control<PodcastInputMode>('text'),
    text: this.formBuilder.nonNullable.control('', [Validators.required, Validators.minLength(10)]),
    style: this.formBuilder.nonNullable.control<PodcastStyle>('educational', [Validators.required]),
    voice: this.formBuilder.nonNullable.control('default', [Validators.required]),
    targetDuration: this.formBuilder.nonNullable.control<PodcastTargetDuration>('short', [
      Validators.required,
    ]),
  });

  protected readonly selectedFile = signal<File | null>(null);
  protected readonly isLoading = signal(false);
  protected readonly errorMessage = signal<string | null>(null);
  protected readonly result = signal<GeneratePodcastResponse | null>(null);
  protected readonly audioSource = computed(() => this.result()?.audio_url ?? '');

  protected get isPdfMode(): boolean {
    return this.form.controls.inputMode.value === 'pdf';
  }

  protected get selectedFileLabel(): string {
    return this.selectedFile()?.name ?? 'No PDF selected';
  }

  protected onModeChange(mode: PodcastInputMode): void {
    this.form.controls.inputMode.setValue(mode);
    this.errorMessage.set(null);

    if (mode === 'pdf') {
      this.form.controls.text.clearValidators();
      this.form.controls.text.setValue('');
    } else {
      this.selectedFile.set(null);
      this.form.controls.text.setValidators([Validators.required, Validators.minLength(10)]);
    }

    this.form.controls.text.updateValueAndValidity();
  }

  protected onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;

    if (file && file.type !== 'application/pdf') {
      this.selectedFile.set(null);
      this.errorMessage.set('Upload a PDF file.');
      input.value = '';
      return;
    }

    this.errorMessage.set(null);
    this.selectedFile.set(file);
  }

  protected generatePodcast(): void {
    this.errorMessage.set(null);
    this.result.set(null);

    if (!this.isPdfMode && this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    if (this.isPdfMode && !this.selectedFile()) {
      this.errorMessage.set('Select a PDF before generating.');
      return;
    }

    this.isLoading.set(true);
    const request$ = this.isPdfMode
      ? this.api.generateFromPdf(
          this.selectedFile() as File,
          this.form.controls.style.value,
          this.form.controls.voice.value,
          this.form.controls.targetDuration.value,
        )
      : this.api.generateFromText({
          input_type: 'text',
          text: this.form.controls.text.value,
          style: this.form.controls.style.value,
          voice: this.form.controls.voice.value,
          target_duration: this.form.controls.targetDuration.value,
        });

    request$
      .pipe(finalize(() => this.isLoading.set(false)))
      .subscribe({
        next: (response) => this.result.set(response),
        error: (error: unknown) => this.errorMessage.set(this.resolveErrorMessage(error)),
      });
  }

  private resolveErrorMessage(error: unknown): string {
    if (error instanceof HttpErrorResponse) {
      if (typeof error.error?.detail === 'string') {
        return error.error.detail;
      }

      return 'The podcast could not be generated. Check the input and try again.';
    }

    return 'Unexpected frontend error.';
  }
}
