<script lang="ts">
	interface Subtitle {
		start_time: string;
		end_time: string;
		style: string;
		text: string;
	}

	interface SubtitlePair {
		original: Subtitle;
		translated: Subtitle;
		id: number;
	}

	const API_URL = 'http://127.0.0.1:8000';
	let subtitlePairs: SubtitlePair[] = [];
	let selectedSubtitleId: number | null = null;
	let correctedText: string = '';
	let rating: number = 0;
	let loading: boolean = false;
	let progress = 0;
	let currentFileId: string | null = null; // Přidáno pro uchování file_id

	async function pollTranslationStatus(fileId: string): Promise<void> {
		while (true) {
			try {
				const response = await fetch(`${API_URL}/translation-status/${fileId}`);
				const status = await response.json();

				const percentage =
					status.total > 0 ? Math.round((status.completed / status.total) * 100) : 0;

				progress = percentage;
				console.log(`Překlad: ${percentage}% (${status.completed}/${status.total} řádků)`);

				if (status.status === 'completed') {
					console.log('Překlad dokončen');
					loading = false;
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
			alert('Error: Nevalidní soubor - je vyžadován .ass soubor');
			return;
		}

		loading = true;
		const formData = new FormData();
		formData.append('file', selectedFile);

		try {
			// Upload file
			const uploadResponse = await fetch(`${API_URL}/translate`, {
				method: 'POST',
				body: formData
			});

			if (!uploadResponse.ok) {
				throw new Error(`HTTP error! status: ${uploadResponse.status}`);
			}

			const { file_id } = await uploadResponse.json();
			currentFileId = file_id; // Uložíme file_id pro pozdější použití

			// Poll for translation status
			await pollTranslationStatus(file_id);

			// Get parsed subtitles
			const response = await fetch(`${API_URL}/get-file-content/${file_id}`);
			const data = await response.json();

			if (data.subtitles) {
				subtitlePairs = data.subtitles;
			}

			loading = false;
		} catch (error) {
			console.error('Error:', error);
			loading = false;
		}
	}

	async function submitFeedback(subtitlePair: SubtitlePair): Promise<void> {
		if (!currentFileId) {
			alert('Chyba: Chybí ID souboru');
			return;
		}

		if (rating === 0) {
			alert('Prosím vyberte hodnocení (1-5 hvězdiček)');
			return;
		}

		const formData = new FormData();
		formData.append('original_text', subtitlePair.original.text);
		formData.append('translated_text', subtitlePair.translated.text);
		formData.append('corrected_text', correctedText || '');
		formData.append('rating', rating.toString());
		formData.append('file_id', currentFileId); // Použijeme uložené file_id

		try {
			const response = await fetch(`${API_URL}/feedback`, {
				method: 'POST',
				body: formData,
				credentials: 'include'
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.detail || 'Chyba při ukládání zpětné vazby');
			}

			const result = await response.json();
			console.log('Feedback uložen:', result);

			// Reset formuláře
			correctedText = '';
			rating = 0;
			selectedSubtitleId = null;

			// Informujte uživatele
			alert('Hodnocení bylo úspěšně uloženo!');
		} catch (error) {
			console.error('Error submitting feedback:', error);
			alert('Chyba při ukládání hodnocení. Zkuste to prosím znovu.');
		}
	}
</script>

<main class="min-h-screen bg-gray-50 py-8">
	<div class="max-w-4xl mx-auto px-4">
		<!-- File upload section -->
		<div class="bg-white rounded-lg shadow-sm p-6 mb-8">
			<input
				type="file"
				accept=".ass"
				on:change={handleFileUpload}
				class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4
                       file:rounded-full file:border-0 file:text-sm file:font-semibold
                       file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
			/>
		</div>

		<!-- Loading indicator -->
		{#if loading}
			<div class="flex justify-center items-center py-12">
				<div class="animate-pulse text-lg text-gray-600">
					Probíhá překlad... {progress}%
				</div>
			</div>
		{/if}

		<!-- Subtitles list -->
		{#if subtitlePairs.length > 0}
			<div class="space-y-6">
				{#each subtitlePairs as pair (pair.id)}
					<div class="bg-white rounded-lg shadow-sm p-6">
						<div class="space-y-4">
							<!-- Timing info -->
							<div class="text-sm text-gray-500">
								{pair.original.start_time} → {pair.original.end_time}
							</div>

							<!-- Original text -->
							<div>
								<h3 class="text-sm font-medium text-gray-500">Originál</h3>
								<p class="mt-1 text-base text-gray-900">{pair.original.text}</p>
							</div>

							<!-- Translated text -->
							<div>
								<h3 class="text-sm font-medium text-gray-500">Překlad</h3>
								<p class="mt-1 text-base text-gray-900">{pair.translated.text}</p>
							</div>

							<!-- Feedback section -->
							{#if selectedSubtitleId === pair.id}
								<div class="mt-6 space-y-4">
									<textarea
										bind:value={correctedText}
										placeholder="Opravený překlad (volitelné)"
										class="w-full px-3 py-2 border border-gray-300 rounded-md"
										rows="3"
									></textarea>

									<!-- Rating stars -->
									<div class="flex items-center gap-2">
										<span class="text-sm text-gray-600">Hodnocení:</span>
										<div class="flex gap-1">
											{#each Array(5) as _, i}
												<button
													class="text-2xl {rating > i ? 'text-yellow-400' : 'text-gray-300'}"
													on:click={() => (rating = i + 1)}
												>
													★
												</button>
											{/each}
										</div>
									</div>

									<!-- Submit button -->
									<button
										on:click={() => submitFeedback(pair)}
										class="w-full py-2 px-4 bg-blue-600 text-white rounded-md"
									>
										Odeslat hodnocení
									</button>
								</div>
							{:else}
								<button
									on:click={() => (selectedSubtitleId = pair.id)}
									class="mt-4 px-4 py-2 border border-gray-300 rounded-md"
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
