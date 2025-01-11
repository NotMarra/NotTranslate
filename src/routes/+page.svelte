<script lang="ts">
	import { onMount } from 'svelte';

	const API_URL = 'http://127.0.0.1:8000';

	interface Translation {
		original: string;
		translated: string;
	}

	interface TranslationStatus {
		total: number;
		completed: number;
		status: 'not_found' | 'in_progress' | 'completed';
	}

	let file: File | null = null;
	let translations: Translation[] = [];
	let selectedTranslation: Translation | null = null;
	let correctedText: string = '';
	let rating: number = 0;
	let loading: boolean = false;
	let downloadUrl: string | null = null;
	let progress = 0;

	async function pollTranslationStatus(fileId: string): Promise<void> {
		while (true) {
			try {
				const response = await fetch(`${API_URL}/translation-status/${fileId}`);
				const status: TranslationStatus = await response.json();

				const percentage =
					status.total > 0 ? Math.round((status.completed / status.total) * 100) : 0;

				progress = percentage;
				console.log(`Překlad: ${percentage}% (${status.completed}/${status.total} řádků)`);

				if (status.status === 'completed') {
					console.log('Překlad dokončen');
					break;
				}

				await new Promise((resolve) => setTimeout(resolve, 500));
			} catch (error) {
				console.error('Chyba při získávání stavu překladu:', error);
				break;
			}
		}
	}

	async function handleFileUpload(event: Event): Promise<void> {
		const input = event.target as HTMLInputElement;
		const selectedFile = input.files?.[0];

		if (!selectedFile || !selectedFile.name.endsWith('.ass')) {
			console.log('Error: Nevalidní soubor - je vyžadován .ass soubor');
			return;
		}

		loading = true;
		progress = 0;
		const formData = new FormData();
		formData.append('file', selectedFile);

		try {
			console.log('Odesílám požadavek na překlad...');
			const response = await fetch(`${API_URL}/translate`, {
				method: 'POST',
				body: formData
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			console.log('Received data:', data);

			// Začneme sledovat stav překladu
			pollTranslationStatus(data.file_id);

			if (!Array.isArray(data.translations)) {
				throw new Error('Neplatný formát dat z serveru');
			}

			translations = data.translations.map((t: [string, string]) => ({
				original: t[0],
				translated: t[1]
			}));

			console.log('Zpracované překlady:', translations);

			const content = translations.map((t) => t.translated).join('\n');
			const blob = new Blob([content], { type: 'text/plain' });
			downloadUrl = URL.createObjectURL(blob);
		} catch (error) {
			if (error instanceof Error) {
				console.error('Chyba při překladu:', error.message);
				console.error('Stack trace:', error.stack);
			} else {
				console.error('Neočekávaná chyba při překladu:', error);
			}
		} finally {
			loading = false;
		}
	}

	async function submitFeedback(translation: Translation): Promise<void> {
		if (rating === 0) {
			console.log('Error: Není vybráno hodnocení');
			return;
		}

		const formData = new FormData();
		formData.append('original_text', translation.original);
		formData.append('translated_text', translation.translated);
		formData.append('corrected_text', correctedText);
		formData.append('rating', rating.toString());

		try {
			console.log('Odesílám zpětnou vazbu:', {
				original: translation.original,
				translated: translation.translated,
				corrected: correctedText,
				rating
			});

			const response = await fetch(`${API_URL}/feedback`, {
				method: 'POST',
				body: formData
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			console.log('Zpětná vazba úspěšně uložena');
			correctedText = '';
			rating = 0;
			selectedTranslation = null;
		} catch (error) {
			if (error instanceof Error) {
				console.error('Chyba při ukládání zpětné vazby:', error.message);
				console.error('Stack trace:', error.stack);
			} else {
				console.error('Neočekávaná chyba při ukládání zpětné vazby:', error);
			}
		}
	}

	onMount(() => {
		return () => {
			if (downloadUrl) {
				URL.revokeObjectURL(downloadUrl);
				console.log('Cleanup: URL objektu uvolněn');
			}
		};
	});
</script>

<main class="min-h-screen bg-gray-50 py-8">
	<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
		<h1 class="text-3xl font-bold text-gray-900 mb-8 text-center">Překladač titulků</h1>

		<div class="bg-white rounded-lg shadow-sm p-6 mb-8">
			<input
				type="file"
				accept=".ass"
				on:change={handleFileUpload}
				class="block w-full text-sm text-gray-500
               file:mr-4 file:py-2 file:px-4
               file:rounded-full file:border-0
               file:text-sm file:font-semibold
               file:bg-blue-50 file:text-blue-700
               hover:file:bg-blue-100
               cursor-pointer"
			/>
		</div>

		{#if loading}
			<div class="flex flex-col items-center justify-center py-12 space-y-4">
				<div class="w-full max-w-md bg-white rounded-lg shadow-sm p-4">
					<div class="flex justify-between mb-2">
						<span class="text-sm font-medium text-gray-700">Průběh překladu</span>
						<span class="text-sm font-medium text-gray-700">{progress}%</span>
					</div>
					<div class="w-full bg-gray-200 rounded-full h-2.5">
						<div class="bg-blue-600 h-2.5 rounded-full" style="width: {progress}%"></div>
					</div>
				</div>
				<div class="flex justify-center items-center py-12">
					<div class="animate-pulse text-lg text-gray-600">Probíhá překlad...</div>
				</div>
			</div>
		{/if}

		{#if translations.length > 0}
			<div class="mb-8 flex justify-center">
				<a
					href={downloadUrl}
					download="translated_subtitles.txt"
					class="inline-flex items-center px-6 py-3 border border-transparent
                 text-base font-medium rounded-md shadow-sm text-white
                 bg-green-600 hover:bg-green-700 focus:outline-none
                 focus:ring-2 focus:ring-offset-2 focus:ring-green-500
                 transition-colors duration-200"
				>
					Stáhnout přeložené titulky
				</a>
			</div>

			<div class="space-y-6">
				{#each translations as translation}
					<div
						class="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow duration-200"
					>
						<div class="space-y-4">
							<div>
								<h3 class="text-sm font-medium text-gray-500">Originál</h3>
								<p class="mt-1 text-base text-gray-900">{translation.original}</p>
							</div>
							<div>
								<h3 class="text-sm font-medium text-gray-500">Překlad</h3>
								<p class="mt-1 text-base text-gray-900">{translation.translated}</p>
							</div>

							{#if selectedTranslation === translation}
								<div class="mt-6 space-y-4">
									<textarea
										bind:value={correctedText}
										placeholder="Opravený překlad (volitelné)"
										class="w-full px-3 py-2 border border-gray-300 rounded-md
                           shadow-sm placeholder-gray-400 focus:outline-none
                           focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
										rows="3"
									></textarea>

									<div class="flex items-center gap-2">
										<span class="text-sm text-gray-600">Hodnocení:</span>
										<div class="flex gap-1">
											{#each Array(5) as _, i}
												<button
													class="text-2xl focus:outline-none {rating > i
														? 'text-yellow-400'
														: 'text-gray-300'} 
                                 hover:text-yellow-500 transition-colors duration-150"
													on:click={() => (rating = i + 1)}
												>
													★
												</button>
											{/each}
										</div>
									</div>

									<button
										on:click={() => submitFeedback(translation)}
										class="w-full inline-flex justify-center py-2 px-4 border border-transparent
                           rounded-md shadow-sm text-sm font-medium text-white bg-blue-600
                           hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2
                           focus:ring-blue-500 transition-colors duration-200"
									>
										Odeslat hodnocení
									</button>
								</div>
							{:else}
								<button
									on:click={() => (selectedTranslation = translation)}
									class="mt-4 inline-flex items-center px-4 py-2 border border-gray-300
                         rounded-md shadow-sm text-sm font-medium text-gray-700
                         bg-white hover:bg-gray-50 focus:outline-none focus:ring-2
                         focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
								>
									Ohodnotit překlad
								</button>
							{/if}
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</main>
